import gymnasium as gym
from gymnasium import spaces
import numpy as np

class SmartElevatorEnv(gym.Env):
    def __init__(self):
        super(SmartElevatorEnv, self).__init__()
        self.num_elevators = 6
        self.num_floors = 10
        self.max_steps = 200
        
        self.elevator_positions = None
        self.hall_calls = None
        self.car_calls = None
        self.elevator_directions = None
        self.current_step = 0

        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3, 3, 3])
        total_obs_size = self.num_elevators + self.num_elevators + (self.num_floors * 2) + (self.num_elevators * self.num_floors)
        self.observation_space = spaces.Box(low=-1.0, high=100.0, shape=(total_obs_size,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.elevator_positions = np.linspace(0, self.num_floors - 1, self.num_elevators).astype(int)
        self.hall_calls = np.zeros(self.num_floors * 2)
        self.car_calls = np.zeros((self.num_elevators, self.num_floors))
        self.elevator_directions = np.zeros(self.num_elevators)
        self.current_step = 0
        return self._get_observation(), {}

    def step(self, action):
        specialReward = 0
        waiting_outside = np.sum(self.hall_calls)

        # 🌟 1. ดึงข้อมูลตำแหน่งปัจจุบัน เพื่อทำ Lightweight GPS
        current_positions = np.copy(self.elevator_positions)

        # 🌟 2. อัปเดตตำแหน่งลิฟต์ (Apply Action)
        for i in range(self.num_elevators):
            if action[i] == 2: # ขึ้น
                if self.elevator_positions[i] < self.num_floors - 1:
                    self.elevator_positions[i] += 1
                    self.elevator_directions[i] = 1
                else:
                    specialReward -= 0.2 # 🚨 ชนเพดาน โดนตีมือ!
                    self.elevator_directions[i] = 0
            elif action[i] == 0: # ลง
                if self.elevator_positions[i] > 0:
                    self.elevator_positions[i] -= 1
                    self.elevator_directions[i] = -1
                else:
                    specialReward -= 0.2 # 🚨 มุดดิน โดนตีมือ!
                    self.elevator_directions[i] = 0
            elif action[i] == 1: # เปิดประตู
                self.elevator_directions[i] = 0

        # 🌟 3. Lightweight GPS: หยอดเศษขนมปังให้ AI เดินตาม
        for i in range(self.num_elevators):
            passengers = int(np.sum(self.car_calls[i]))
            old_floor = current_positions[i]
            new_floor = self.elevator_positions[i]

            # ถ้าลิฟต์ว่าง ให้มองหาคนที่รออยู่ข้างนอก
            if passengers == 0 and waiting_outside > 0:
                floors_with_calls = np.where((self.hall_calls[:self.num_floors] > 0) | (self.hall_calls[self.num_floors:] > 0))[0]
                if len(floors_with_calls) > 0:
                    closest_call = floors_with_calls[np.argmin(np.abs(floors_with_calls - old_floor))]
                    # ถ้าเดินเข้าใกล้เป้าหมาย ให้ขนม +0.1, ถ้าเดินหนี หัก -0.1
                    if abs(new_floor - closest_call) < abs(old_floor - closest_call):
                        specialReward += 0.1
                    elif abs(new_floor - closest_call) > abs(old_floor - closest_call):
                        specialReward -= 0.1

            # ถ้าลิฟต์มีคน ให้มองหาชั้นที่จะไปส่ง
            elif passengers > 0:
                destinations = np.where(self.car_calls[i] > 0)[0]
                if len(destinations) > 0:
                    closest_dest = destinations[np.argmin(np.abs(destinations - old_floor))]
                    # เดินเข้าใกล้ที่หมาย +0.1, เดินหนี -0.1
                    if abs(new_floor - closest_dest) < abs(old_floor - closest_dest):
                        specialReward += 0.1
                    elif abs(new_floor - closest_dest) > abs(old_floor - closest_dest):
                        specialReward -= 0.1

        # 🌟 4. รับ/ส่งผู้โดยสาร
        self._simulate_passengers_arriving()
        specialReward += self._clear_serviced_calls(action)

        # 🌟 5. คำนวณ Penalty ของคนตกค้าง
        waiting_outside = np.sum(self.hall_calls)
        waiting_inside = np.sum(self.car_calls)
        
        # 🔧 ลดแรงกดดันลงมานิดนึง ให้ AI ไม่แพนิค
        penalty = -0.002 * (waiting_outside + waiting_inside)

        # 🌟 6. เช็กจบเกม
        self.current_step += 1
        truncated = self.current_step >= self.max_steps
        
        reward = specialReward + penalty

        # ลงโทษตอนจบเกม ไม่ต้องโหดมาก (คูณ 1.0 พอ) เพื่อไม่ให้กราฟ Loss กระชาก
        if truncated:
            reward -= (waiting_inside * 1.0)
            reward -= (waiting_outside * 1.0)

        return self._get_observation(), float(reward), False, truncated, {}

    def _get_observation(self):
        return np.concatenate((
            self.elevator_positions,
            self.elevator_directions,
            self.hall_calls,
            self.car_calls.flatten()
        )).astype(np.float32)

    def _simulate_passengers_arriving(self):
        if np.random.rand() < 0.20:
            floor = np.random.randint(0, self.num_floors)
            direction = 1 if floor == 0 else (0 if floor == self.num_floors - 1 else np.random.choice([0, 1]))
            if direction == 0:
                self.hall_calls[floor] += 1
            else:
                self.hall_calls[floor + self.num_floors] += 1

    def _clear_serviced_calls(self, action):
        specialReward = 0

        for i, pos in enumerate(self.elevator_positions):
            if action[i] == 1: # ถ้าสั่งเปิดประตู (1) ค่อยมาดูว่ามีใครเข้า/ออกไหม
                floor = int(pos)
                current_passengers = int(np.sum(self.car_calls[i]))
                success_action = False

                # ส่งคนลง (คะแนนใหญ่สุด +10)
                getting_off = self.car_calls[i][floor]
                if getting_off > 0:
                    specialReward += (10.0 * getting_off) 
                    self.car_calls[i][floor] = 0
                    current_passengers -= getting_off
                    success_action = True

                # รับคนขึ้น (คะแนนรอง +2)
                while self.hall_calls[floor] > 0 and current_passengers < 4:
                    specialReward += 2.0 
                    self.hall_calls[floor] -= 1
                    current_passengers += 1
                    success_action = True
                    if floor < self.num_floors - 1:
                        self.car_calls[i][np.random.randint(floor + 1, self.num_floors)] += 1

                # รับคนลง (คะแนนรอง +2)
                idx_down = floor + self.num_floors
                while self.hall_calls[idx_down] > 0 and current_passengers < 4:
                    specialReward += 2.0  
                    self.hall_calls[idx_down] -= 1
                    current_passengers += 1
                    success_action = True
                    if floor > 0:
                        self.car_calls[i][np.random.randint(0, floor)] += 1

                # เปิดประตูวืด (ไม่มีคนเข้า/ออก) ทำโทษเบาๆ
                if not success_action:
                    specialReward -= 0.5

        return specialReward