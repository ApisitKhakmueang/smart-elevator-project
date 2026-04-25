import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from enviroment_final import SmartElevatorEnv # 🌟 ตรวจสอบชื่อไฟล์ให้ตรง

def test_elevator():
    # 1. สร้าง Environment สำหรับทดสอบ
    base_env = SmartElevatorEnv()
    env = DummyVecEnv([lambda: base_env])

    # 2. โหลด VecNormalize (แว่นตาปรับสเกล)
    stats_path = "vec_normalize_final.pkl"
    try:
        env = VecNormalize.load(stats_path, env)
        env.training = False    # ปิดการเรียนรู้
        env.norm_reward = False # โชว์รางวัลจริงๆ
        print(f"✅ โหลดค่าสถิติจาก {stats_path} เรียบร้อย")
    except:
        print("⚠️ ไม่พบไฟล์ VecNormalize ผลการทดสอบอาจคลาดเคลื่อน")

    # 3. โหลดสมอง AI
    model_path = "ppo_smart_elevator_final"
    try:
        model = PPO.load(model_path)
        print(f"✅ โหลดโมเดล {model_path} เรียบร้อย")
    except:
        print(f"❌ ไม่พบไฟล์โมเดล {model_path} กรุณาเช็กชื่อไฟล์อีกครั้ง")
        return

    # 4. เริ่มการจำลอง
    obs = env.reset()
    total_score = 0
    
    print("\n🏢 --- เริ่มการทดสอบลิฟต์อัจฉริยะ (Simulation Start) ---")

    # รัน 200 step ตาม max_steps
    for step in range(200):
        # สั่งให้ AI ตัดสินใจแบบแม่นยำที่สุด
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, infos = env.step(action)
        
        info = infos[0] # ดึงข้อมูลจากตึก
        total_score += reward[0]

        # ปรินต์สถานะทุกๆ 10 วินาที
        if step % 10 == 0:
            raw_env = env.envs[0]
            print(f"⏰ วินาทีที่ {step:03d} | คะแนนสะสม: {total_score:.1f}")
            print(f"   📍 ตำแหน่งลิฟต์: {raw_env.elevator_positions}")
            print(f"   👥 รอหน้าลิฟต์: {int(np.sum(raw_env.hall_calls))} คน | ในลิฟต์: {int(np.sum(raw_env.car_calls))} คน")
            # 🌟 ดึงค่าสะสมจาก info มาโชว์ได้เลย
            print(f"   📥 ส่งสำเร็จสะสม: {info['total_delivered']} คน | ⚡ พลังงานที่ใช้: {info['total_energy']}")
            print("-" * 50)

        if done[0]:
            break

    # 5. สรุปผลรายงาน (ดึงค่าจาก info ของก้าวสุดท้ายได้เลย)
    final_info = infos[0]
    total_d = final_info['total_delivered']
    total_e = final_info['total_energy']
    
    print("\n" + "="*50)
    print("📊 สรุปผลการทำงานของ AI ใน 1 Episode (200 สเต็ป)")
    print("="*50)
    print(f"✅ ส่งผู้โดยสารสำเร็จ (Total Delivered): {total_d} คน")
    print(f"⚡ พลังงานที่ใช้ (Energy Consumption): {total_e} หน่วยขยับ")
    print(f"⌛ เวลารอเฉลี่ย (Average Wait Time): {final_info['avg_wait_time']:.2f} วินาที/คน")
    print(f"📦 คนตกค้างในตึก (Unserviced People): {final_info['unserviced_people']} คน")
    print("-" * 50)
    print(f"🏆 คะแนน Reward รวมสุทธิ: {total_score:.2f}")
    print(f"📈 ประสิทธิภาพ (ส่งคน/พลังงาน): {(total_d/total_e if total_e > 0 else 0):.2f}")
    print("="*50)

if __name__ == "__main__":
    test_elevator()