import sys
import numpy as np
# แก้ปัญหา ModuleNotFoundError: No module named 'numpy._core.numeric'
sys.modules['numpy._core'] = np.core 

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import uvicorn
import asyncio
from model.enviroment import SmartElevatorEnv # ตรวจสอบ path ให้ตรงกับโปรเจกต์ของคุณด้วยนะครับ

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

vec_path = BASE_DIR / "model" / "vec_normalize_final.pkl"
model_path = BASE_DIR / "model" / "ppo_smart_elevator_final"

app = FastAPI()

# CORS ยังจำเป็นต้องมีหากมีการเรียกใช้หน้าเว็บจาก domain อื่น
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# 1. สร้างตึกจำลองใหม่
env = DummyVecEnv([lambda: SmartElevatorEnv()])

# 2. โหลดแว่นตา (VecNormalize) ที่ใช้ตอนฝึกกลับมา
try:
    env = VecNormalize.load(vec_path, env)
    # ปิดการอัปเดตสเกล เพราะเราแค่อยากทดสอบ ไม่ได้ฝึกเพิ่ม
    env.training = False
    # ปิดการแปลงคะแนน เพื่อให้โชว์คะแนนดิบๆ (+2, +5, -0.1) ออกมาให้เราเห็น
    env.norm_reward = False
except:
    print("⚠️ ไม่พบไฟล์ vec_normalize_final.pkl ใช้ Env ธรรมดาแทน (ผลลัพธ์อาจแกว่งนิดหน่อย)")

# 3. โหลดสมอง AI ที่เทรนเสร็จแล้ว
model = PPO.load(model_path)

# --- WebSocket Endpoint ---
@app.websocket("/ws/step")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Client connected")
    
    # รีเซ็ตสภาพแวดล้อมเมื่อเริ่มเชื่อมต่อใหม่
    obs = env.reset()
    total_score = 0
    step = 0
    
    print("🏢 เริ่มการจำลองการทำงานของลิฟต์ AI...")
    
    try:
        while True:
            # --- AI คิดและ Step Logic ---
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            
            # ดึงข้อมูลดิบจาก Environment
            raw_env = env.envs[0]
            
            # รวมคะแนนสะสม
            total_score += reward[0]
            
            # --- ปรินต์ดูสถานะในฝั่ง Server ---
            print(f"⏰ วินาทีที่ {step:03d} | คะแนนสะสม: {total_score:.1f}")
            print(f"   ตำแหน่งลิฟต์: {raw_env.elevator_positions}")
            print(f"   จำนวนคนที่รอหน้าลิฟต์: {int(np.sum(raw_env.hall_calls))} คน | ในลิฟต์: {int(np.sum(raw_env.car_calls))} คน")
            print("-" * 40)
            print(f"   จำนวนคนที่รอหน้าลิฟต์: {raw_env.hall_calls} คน")
            print("-" * 40)
            print(f"   จำนวนคนที่รอในลิฟต์:\n{raw_env.car_calls} คน")
            print("-" * 40)
            print(f"   คำสั่ง: {action}")
            print("-" * 60)
            
            # เตรียมข้อมูลส่งกลับไปให้ฝั่ง Frontend (หน้าเว็บ)
            data = {
                "step": step,
                "total_score": float(total_score),
                "elevators": raw_env.elevator_positions.tolist(),
                "directions": raw_env.elevator_directions.tolist(),
                "hall_calls": raw_env.hall_calls.tolist(),
                "car_calls": [call.tolist() for call in raw_env.car_calls],
                "action": action.tolist(), # เผื่ออยากแสดง action บนเว็บ
                "reward": float(reward[0]),
                "done": bool(done[0])
            }
            
            # ส่งข้อมูลไปยัง Frontend ผ่าน WebSocket
            await websocket.send_json(data)
            
            # ถ้าจบเกม/จบวัน ให้ Reset ตัวแปรทั้งหมดใหม่
            if done[0]:
                print(f"✅ จบวัน! คะแนนรวมสุทธิที่ AI ทำได้: {total_score:.2f} คะแนน")
                print("🔄 กำลังเริ่มจำลองวันใหม่...\n")
                obs = env.reset()
                total_score = 0
                step = 0
            else:
                step += 1
            
            # หน่วงเวลา 5 วินาที (หากตอนทดสอบรู้สึกว่าช้าไป ปรับลดเหลือ 1 หรือ 0.5 วินาทีได้นะครับ)
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        print("🔴 Client disconnected")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)