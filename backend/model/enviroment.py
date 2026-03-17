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
        
        # 🌟 แก้ไขจุดที่ 1: บวก 1 เพิ่มสำหรับตัวแปร "เวลา" (Time Fraction)
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

        # 🌟 2. อัปเดตตำแหน่งลิฟต์ (ลงโทษชนเพดานเท่าเดิม)
        for i in range(self.num_elevators):
            if action[i] == 2: # ขึ้น
                if self.elevator_positions[i] < self.num_floors - 1:
                    self.elevator_positions[i] += 1
                    self.elevator_directions[i] = 1
                else:
                    specialReward -= 0.5 # ✅ ลดจาก -2.0 เหลือแค่ -0.5
                    self.elevator_directions[i] = 0
            elif action[i] == 0: # ลง
                if self.elevator_positions[i] > 0:
                    self.elevator_positions[i] -= 1
                    self.elevator_directions[i] = -1
                else:
                    specialReward -= 0.5 # ✅ ลดจาก -2.0 เหลือแค่ -0.5
                    self.elevator_directions[i] = 0
            elif action[i] == 1: # จอด
                self.elevator_directions[i] = 0

        # 🌟 1. ระบบนำทาง (ลดบทลงโทษจุกจิก เน้นให้เดินหน้า)
        for i in range(self.num_elevators):
            floor = int(self.elevator_positions[i])
            passengers = int(np.sum(self.car_calls[i]))
            has_target = False
            closest_target = -1
            
            if passengers > 0:
                destinations = np.where(self.car_calls[i] > 0)[0]
                direction = self.elevator_directions[i]
                
                if direction == 1: # ⬆️ ลิฟต์กำลังวิ่งขึ้น
                    # หาเป้าหมายที่อยู่ "สูงกว่าหรือเท่ากับ" ชั้นปัจจุบัน
                    targets_ahead = destinations[destinations >= floor]
                    if len(targets_ahead) > 0:
                        closest_target = np.min(targets_ahead) # แวะชั้นที่ใกล้ที่สุดในขาขึ้น
                    else:
                        closest_target = np.max(destinations)  # หมดคิวขาขึ้น ให้เลี้ยวกลับไปส่งคนที่อยู่ไกลสุด
                        
                elif direction == -1: # ⬇️ ลิฟต์กำลังวิ่งลง
                    # หาเป้าหมายที่อยู่ "ต่ำกว่าหรือเท่ากับ" ชั้นปัจจุบัน
                    targets_ahead = destinations[destinations <= floor]
                    if len(targets_ahead) > 0:
                        closest_target = np.max(targets_ahead) # แวะชั้นที่ใกล้ที่สุดในขาลง
                    else:
                        closest_target = np.min(destinations)  # หมดคิวขาลง ให้เลี้ยวกลับไปส่งคนที่อยู่ต่ำสุด
                        
                else: # 🛑 ลิฟต์จอดนิ่งอยู่
                    # ถ้าเพิ่งเริ่มออกตัว ให้ไปหาคนที่ใกล้ที่สุดตามปกติ
                    closest_target = destinations[np.argmin(np.abs(destinations - floor))]
                
                has_target = True
            elif waiting_outside > 0:
                floors_with_calls = np.where((self.hall_calls[:self.num_floors] > 0) | (self.hall_calls[self.num_floors:] > 0))[0]
                if len(floors_with_calls) > 0:
                    closest_target = floors_with_calls[np.argmin(np.abs(floors_with_calls - floor))]
                    has_target = True

            # 🌟 [แก้ตรงนี้] ระบบนำทางและตีมือลิฟต์อู้
            if has_target:
                if action[i] == 2: # วิ่งขึ้น
                    if floor < closest_target: specialReward += 0.1
                    else: specialReward -= 0.1 # 🚨 วิ่งผิดทางโดนหัก
                elif action[i] == 0: # วิ่งลง
                    if floor > closest_target: specialReward += 0.1
                    else: specialReward -= 0.1 # 🚨 วิ่งผิดทางโดนหัก
                elif action[i] == 1: # สั่งจอด/เปิดประตู
                    if floor == closest_target: specialReward += 1.0 # 🌟 จอดตรงเป้าหมาย เอาโบนัสไปเต็มๆ!
                    else: specialReward -= 0.5 # 🚨 ยังไม่ถึงแต่ดันจอดเปิดประตู โดนหัก!
            else:
                # 🌟 ถ้าไม่มีงานให้ทำ (ตึกว่าง) 
                if action[i] == 1: # สั่งเปิดประตูเล่น
                    specialReward -= 0.2 # 🚨 เปิดประตูเล่นตอนตึกว่าง โดนหัก! (บังคับให้แช่ประตูปิดไว้รอ)
                elif action[i] == 0 or action[i] == 2: # สั่งวิ่งตรวจตราตึก (อนุญาตให้ทำได้)
                    pass

        # 🌟 3. รับ/ส่งผู้โดยสาร
        self._simulate_passengers_arriving()
        specialReward += self._clear_serviced_calls(action)

        # 🌟 4. หักคะแนนลิฟต์ซ้อนทับกัน (ลดความโหดลงเหลือ -0.5)
        for f in range(self.num_floors):
            elevators_here = np.where(self.elevator_positions == f)[0]
            if len(elevators_here) > 1:
                empty_elevators = sum([1 for idx in elevators_here if int(np.sum(self.car_calls[idx])) == 0])
                if empty_elevators > 1:
                    specialReward -= (0.5 * empty_elevators)

        # 🌟 5. แรงกดดันเวลาคนรอ & แก้อาการ "ลักพาตัวผู้โดยสาร" 
        waiting_outside = np.sum(self.hall_calls)
        waiting_inside = np.sum(self.car_calls)
        
        # เพิ่มความเจ็บปวดของการปล่อยคนรอหน้าลิฟต์
        penalty = -0.05 * waiting_outside # 🌟 เพิ่มจาก -0.01 เป็น -0.05
        
        # บีบให้รีบระบายคนออกจากลิฟต์
        penalty -= 0.1 * waiting_inside # 🌟 เพิ่มจาก -0.5 เป็น -1.0 ไปเลย! โดนทุกวินาทีต้องรีบส่งแน่

        self.current_step += 1
        truncated = self.current_step >= self.max_steps
        reward = specialReward + penalty

        return self._get_observation(), float(reward), False, truncated, {}

    def _get_observation(self):
        # 🌟 ใส่ "นาฬิกา" ให้ AI แบบวนลูป เพื่อเตรียมทำลิฟต์ 24 ชั่วโมง
        # looped_step = self.current_step % self.max_steps
        # time_fraction = np.array([looped_step / self.max_steps], dtype=np.float32)
        
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
            direction = np.random.choice([0, 1])
            if floor == self.num_floors - 1: direction = 1
            elif floor == 0: direction = 0

            if direction == 0: self.hall_calls[floor] += 1
            else: self.hall_calls[floor + self.num_floors] += 1

    def _clear_serviced_calls(self, action):
        specialReward = 0
        total_waiting_outside = np.sum(self.hall_calls)

        for i, pos in enumerate(self.elevator_positions):
            floor = int(pos)
            current_passengers = int(np.sum(self.car_calls[i]))
            
            # 🌟 กฎใหม่: ถ้าในตู้มีคนจะลงชั้นนี้ "เปิดประตูให้อัตโนมัติ" ไม่ต้องรอ AI สั่ง
            is_dest = self.car_calls[i][floor] > 0
            
            # หรือถ้า AI สั่งจอด (action 1)
            is_ai_open = (action[i] == 1)

            if is_dest or is_ai_open:
                success_action = False

                # 1. ส่งคนลง (ได้โบนัสเสมอถ้ามาถึงชั้นที่คนจะลง)
                getting_off = self.car_calls[i][floor]
                if getting_off > 0:
                    specialReward += (20.0 * getting_off)
                    self.car_calls[i][floor] = 0
                    current_passengers -= getting_off
                    success_action = True

                # 2. รับคน (เฉพาะตอนที่ AI สั่งจอด Action 1 หรือจงใจมาส่งคน)
                # การทำแบบนี้จะช่วยให้ลิฟต์ไม่แวะรับคนมั่วซั่วตอนกำลังทำความเร็ว
                if is_ai_open:
                    # รับคนขึ้น
                    while self.hall_calls[floor] > 0 and current_passengers < 4:
                        specialReward += 2.0 
                        self.hall_calls[floor] -= 1
                        current_passengers += 1
                        success_action = True
                        if floor < self.num_floors - 1:
                            self.car_calls[i][np.random.randint(floor + 1, self.num_floors)] += 1

                    # รับคนลง
                    idx_down = floor + self.num_floors
                    while self.hall_calls[idx_down] > 0 and current_passengers < 4:
                        specialReward += 2.0  
                        self.hall_calls[idx_down] -= 1
                        current_passengers += 1
                        success_action = True
                        if floor > 0:
                            self.car_calls[i][np.random.randint(0, floor)] += 1

                # หักคะแนนถ้าสั่งเปิดประตู (Action 1) แต่ไม่มีคนเข้าหรือออกเลย
                if is_ai_open and not success_action:
                    specialReward -= 0.1

        return specialReward