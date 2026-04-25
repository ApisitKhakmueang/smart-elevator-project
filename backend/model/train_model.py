from typing import Callable
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
from enviroment_final import SmartElevatorEnv

# 🌟 1. สร้าง Callback เพื่อดึง Metrics จาก info มาแสดงผลบนหน้าจอ
class ElevatorMetricsCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(ElevatorMetricsCallback, self).__init__(verbose)
        self.rollout_delivered = []

    def _on_step(self) -> bool:
        # ดึงค่า 'delivered' จากทุก env มาสะสมไว้
        for info in self.locals['infos']:
            if 'delivered' in info:
                self.rollout_delivered.append(info['delivered'])
        
        # ทุกๆ 2048 steps (หรือตามระยะที่ต้องการ) ให้แสดงค่าเฉลี่ย
        if self.n_calls % 1024 == 0:
            avg_delivered = np.mean(self.rollout_delivered) if self.rollout_delivered else 0
            print(f"--- 📊 Step {self.num_timesteps} | Avg Delivered: {avg_delivered:.2f} people/step ---")
            self.rollout_delivered = [] # Reset ค่า
        return True

def linear_schedule(initial_value: float) -> Callable[[float], float]:
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func

if __name__ == '__main__':
    # 2. ตั้งค่า Environment
    # เพิ่ม n_envs เป็น 12 เพื่อความเร็วถ้า CPU ไหว
    num_envs = 8
    env = make_vec_env(lambda: SmartElevatorEnv(), n_envs=num_envs, vec_env_cls=SubprocVecEnv)
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=100.0)

    # 3. ตั้งค่าโมเดล PPO
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="./ppo_elevator_tensorboard/", # 🌟 เปิดใช้งาน TensorBoard
        device="cpu", 
        policy_kwargs=dict(net_arch=dict(pi=[128, 128], vf=[128, 128])),
        
        n_steps=1024,
        batch_size=512,
        n_epochs=15,
        
        learning_rate=linear_schedule(3e-4),
        ent_coef=0.01,
        target_kl=0.02,
        
        gae_lambda=0.95,
        gamma=0.99,
        clip_range=0.2
    )

    # 4. สร้าง Callbacks (รวมทั้ง Checkpoint และ Metrics)
    checkpoint_callback = CheckpointCallback(
        save_freq=max(100000 // num_envs, 1), 
        save_path='./models_backup/',
        name_prefix='elevator_model'
    )
    
    metrics_callback = ElevatorMetricsCallback()

    print("🚀 เริ่มเทรนโมเดล 3,000,000 สเต็ป พร้อมระบบวัดผลละเอียด...")
    
    # 5. เริ่มการเรียนรู้
    model.learn(
        total_timesteps=3000000, 
        callback=[checkpoint_callback, metrics_callback], # 🌟 ใส่คู่กัน
        tb_log_name="run_final_version"
    )

    # 6. เซฟผลลัพธ์
    model.save("ppo_smart_elevator_final")
    env.save("vec_normalize_final.pkl")
    print("✅ เทรนเสร็จสิ้นและเซฟไฟล์เรียบร้อย!")