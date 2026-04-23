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

        # 🌟 เพิ่มตัวแปรสำหรับเก็บ Metrics ทั้ง 4 ข้อ แบบสะสมทั้ง Episode
        self.total_delivered = 0
        self.total_energy = 0
        self.cumulative_wait_time = 0

        self.action_space = spaces.MultiDiscrete([3] * self.num_elevators)
        
        # Observation Space: ตำแหน่ง(6) + ทิศทาง(6) + Hall Calls(20) + Car Calls(60) = 92
        total_obs_size = self.num_elevators + self.num_elevators + (self.num_floors * 2) + (self.num_elevators * self.num_floors)
        self.observation_space = spaces.Box(low=-1.0, high=100.0, shape=(total_obs_size,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.elevator_positions = np.linspace(0, self.num_floors - 1, self.num_elevators).astype(int)
        self.hall_calls = np.zeros(self.num_floors * 2)
        self.car_calls = np.zeros((self.num_elevators, self.num_floors))
        self.elevator_directions = np.zeros(self.num_elevators)
        self.current_step = 0

        # 🌟 รีเซ็ต Metrics ใหม่ทุกครั้งที่เริ่มวันใหม่
        self.total_delivered = 0
        self.total_energy = 0
        self.cumulative_wait_time = 0
        
        return self._get_observation(), {}

    def step(self, action):
        specialReward = 0 # [0, 1, 2, 0, 1, 0] 
        # วัดพลังงาน: ขยับ (0, 2) เสียพลังงาน, จอด (1) ไม่เสีย
        energy_used = np.sum([1 for a in action if a != 1])

        # 1. อัปเดตตำแหน่งและทิศทางลิฟต์
        for i in range(self.num_elevators):
            if action[i] == 2: # ขึ้น
                if self.elevator_positions[i] < self.num_floors - 1:
                    self.elevator_positions[i] += 1
                    self.elevator_directions[i] = 1
                else:
                    specialReward -= 0.5 # ชนเพดาน
                    self.elevator_directions[i] = 0
            elif action[i] == 0: # ลง
                if self.elevator_positions[i] > 0:
                    self.elevator_positions[i] -= 1
                    self.elevator_directions[i] = -1
                else:
                    specialReward -= 0.5 # ชนพื้น
                    self.elevator_directions[i] = 0
            elif action[i] == 1: # จอด/เปิดประตู
                self.elevator_directions[i] = 0

        # 2. ระบบนำทางและ Guidance Reward (SCAN Logic)
        waiting_outside = np.sum(self.hall_calls)
        for i in range(self.num_elevators):
            floor = int(self.elevator_positions[i])
            passengers_in_car = int(np.sum(self.car_calls[i]))
            has_target = False
            closest_target = -1
            
            if passengers_in_car > 0:
                destinations = np.where(self.car_calls[i] > 0)[0]
                direction = self.elevator_directions[i]
                
                if direction == 1: # กำลังขึ้น
                    targets_ahead = destinations[destinations >= floor]
                    closest_target = np.min(targets_ahead) if len(targets_ahead) > 0 else np.max(destinations)
                elif direction == -1: # กำลังลง
                    targets_ahead = destinations[destinations <= floor]
                    closest_target = np.max(targets_ahead) if len(targets_ahead) > 0 else np.min(destinations)
                else: # จอดนิ่ง
                    closest_target = destinations[np.argmin(np.abs(destinations - floor))]
                has_target = True
            elif waiting_outside > 0:
                floors_with_calls = np.where((self.hall_calls[:self.num_floors] > 0) | (self.hall_calls[self.num_floors:] > 0))[0]
                if len(floors_with_calls) > 0:
                    closest_target = floors_with_calls[np.argmin(np.abs(floors_with_calls - floor))]
                    has_target = True

            # ให้รางวัลการเดินถูกทิศทาง
            if has_target:
                if action[i] == 2: # สั่งขึ้น
                    specialReward += 0.1 if floor < closest_target else -0.1
                elif action[i] == 0: # สั่งลง
                    specialReward += 0.1 if floor > closest_target else -0.1
                elif action[i] == 1: # สั่งจอด
                    specialReward += 1.0 if floor == closest_target else -0.5
            else:
                if action[i] == 1: specialReward -= 0.2 # เปิดประตูเล่นตอนตึกว่าง

        # 3. จำลองคนเกิดและจัดการคิว (รับ/ส่ง)
        self._simulate_passengers_arriving()
        delivered_this_step, service_reward = self._clear_serviced_calls(action)
        specialReward += service_reward

        # 4. หักคะแนนการกระจุกตัว (Clustering Penalty)
        for f in range(self.num_floors):
            elevators_here = np.where(self.elevator_positions == f)[0]
            if len(elevators_here) > 1:
                empty_elevators = sum([1 for idx in elevators_here if np.sum(self.car_calls[idx]) == 0])
                if empty_elevators > 1:
                    specialReward -= (0.5 * empty_elevators)

        # 5. คำนวณ Penalty จากเวลาที่เสียไป
        current_waiting_hall = np.sum(self.hall_calls)
        current_waiting_car = np.sum(self.car_calls)
        penalty = (-0.05 * current_waiting_hall) + (-0.1 * current_waiting_car)
        
        reward = specialReward + penalty

        # 🌟 อัปเดตค่าตัวแปรสะสมเพื่อใช้คำนวณ Metrics ทั้ง 4
        self.total_delivered += delivered_this_step
        self.total_energy += energy_used
        self.cumulative_wait_time += (current_waiting_hall + current_waiting_car)
        
        # ป้องกันการหารด้วย 0 ในช่วงแรกที่ยังส่งคนไม่ได้เลย
        avg_wait_time = self.cumulative_wait_time / (self.total_delivered if self.total_delivered > 0 else 1)

        # 🌟 แพ็กข้อมูล 4 หัวข้อสำคัญลงใน `info` Dictionary ทันที
        info = {
            "delivered": delivered_this_step,               # คนที่ส่งได้ในสเต็ปนี้ (สำหรับพล็อต TensorBoard)
            "total_delivered": self.total_delivered,        # 1. Total Delivered 
            "total_energy": self.total_energy,              # 2. Energy Consumption
            "avg_wait_time": avg_wait_time,                 # 3. Average Wait Time
            "unserviced_people": int(current_waiting_hall + current_waiting_car), # 4. Unserviced Ratio (คนค้าง)
            # เอาไว้ตรวจสอบเชิงลึก (ถ้าต้องการ)
            "waiting_hall": current_waiting_hall,
            "waiting_car": current_waiting_car
        }

        self.current_step += 1
        truncated = self.current_step >= self.max_steps
        return self._get_observation(), float(reward), False, truncated, info

    def _get_observation(self):
        return np.concatenate((
            self.elevator_positions,
            self.elevator_directions,
            self.hall_calls,
            self.car_calls.flatten(),
        )).astype(np.float32)

    def _simulate_passengers_arriving(self):
        arrival_probability = 0.20
        if np.random.rand() < arrival_probability:
            floor = np.random.randint(0, self.num_floors)
            if floor == self.num_floors - 1:
                direction = 1 
            elif floor == 0:
                direction = 0 
            else:
                direction = np.random.choice([0, 1])

            if direction == 0: self.hall_calls[floor] += 1
            else: self.hall_calls[floor + self.num_floors] += 1

    def _clear_serviced_calls(self, action):
        specialReward = 0
        total_delivered_this_step = 0  
        for i, pos in enumerate(self.elevator_positions):
            floor = int(pos)
            current_passengers = int(np.sum(self.car_calls[i]))
            is_dest = self.car_calls[i][floor] > 0
            is_ai_open = (action[i] == 1)

            if is_dest or is_ai_open:
                # 1. ส่งคนลง
                getting_off = int(self.car_calls[i][floor])
                if getting_off > 0:
                    specialReward += (20.0 * getting_off)
                    total_delivered_this_step += getting_off
                    self.car_calls[i][floor] = 0
                    current_passengers -= getting_off

                # 2. รับคน (เฉพาะเมื่อ AI สั่งเปิดประตู)
                if is_ai_open:
                    success_load = False
                    # รับคนขึ้น
                    while self.hall_calls[floor] > 0 and current_passengers < 4:
                        specialReward += 2.0 
                        self.hall_calls[floor] -= 1
                        current_passengers += 1
                        self.car_calls[i][np.random.randint(floor + 1, self.num_floors)] += 1
                        success_load = True
                    # รับคนลง
                    idx_down = floor + self.num_floors
                    while self.hall_calls[idx_down] > 0 and current_passengers < 4:
                        specialReward += 2.0  
                        self.hall_calls[idx_down] -= 1
                        current_passengers += 1
                        self.car_calls[i][np.random.randint(0, floor)] += 1
                        success_load = True
                    
                    # บทลงโทษเปิดประตูวืด
                    if getting_off == 0 and not success_load:
                        specialReward -= 0.1

        return total_delivered_this_step, specialReward