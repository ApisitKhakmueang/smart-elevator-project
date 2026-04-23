// app/page.tsx
'use client';

import React from 'react';
import ElevatorShaft, { ElevatorData } from '../components/ElevatorShaft';
import { useElevatorWebsocket } from '../hook/useElevatorWebsocket';

const NUM_ELEVATORS = 6;

export default function ElevatorDashboard() {
  // 🌟 1. เรียกใช้งาน Custom Hook แทนการเขียน WebSocket เองทั้งหมด
  const { data, isConnected } = useElevatorWebsocket('ws://127.0.0.1:8000/ws/step');

  // 🌟 2. เตรียมข้อมูลสำหรับแสดงผล (ถ้า data ยังไม่มาให้ใช้ค่าเริ่มต้นไปก่อน)
  const step = data?.step ?? 0;
  const totalScore = data?.total_score ?? 0;
  const elevatorsList = data?.elevators ?? Array(NUM_ELEVATORS).fill(0);
  const directionsList = data?.directions ?? Array(NUM_ELEVATORS).fill(0);
  const currentReward = data?.reward ?? 0;

  return (
    <div className="min-h-screen bg-[#181818] text-zinc-200 font-sans p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header แผงควบคุม */}
        <header className="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div>
            <h1 className="text-2xl font-semibold text-white flex items-center gap-3">
              <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-[#3ECF8E] animate-pulse' : 'bg-red-500'}`}></span>
              RL Elevator Simulation
            </h1>
            <div className="flex gap-4 mt-2 text-sm text-zinc-400">
              <p>Step: <span className="font-mono text-zinc-200">{step}</span></p>
              <p>Total Score: <span className={`font-mono ${totalScore >= 0 ? 'text-[#3ECF8E]' : 'text-red-400'}`}>
                {totalScore.toFixed(4)}
              </span></p>
              <p>Step Reward: <span className={`font-mono ${currentReward >= 0 ? 'text-[#3ECF8E]' : 'text-red-400'}`}>
                {currentReward  .toFixed(4)}
              </span></p>
            </div>
          </div>
          <div className="bg-[#232323] border border-zinc-800 px-4 py-2 rounded-md">
            <span className="text-xs text-zinc-500 mr-3">WS STATUS</span>
            <span className={`text-sm font-mono ${isConnected ? 'text-[#3ECF8E]' : 'text-red-500'}`}>
              {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
        </header>

        {/* กริตแสดงลิฟต์ทั้ง 6 ตัว */}
        <main className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
          {elevatorsList.map((floor, index) => {
            // แปลงข้อมูล Action จากทิศทาง (Directions)
            const dir = directionsList[index];
            let action: 'IDLE' | 'UP' | 'DOWN' = 'IDLE';
            if (dir > 0) action = 'UP';
            else if (dir < 0) action = 'DOWN';

            // สร้าง Object ข้อมูลลิฟต์ส่งให้ Component
            const elevatorData: ElevatorData = {
              id: index + 1,
              floor: floor,
              action: action,
              reward: currentReward,
            };

            return <ElevatorShaft key={elevatorData.id} elevator={elevatorData} />;
          })}
        </main>

      </div>
    </div>
  );
}