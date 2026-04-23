// app/page.tsx
'use client';

import React from 'react';
import ElevatorShaft, { ElevatorData } from '../components/ElevatorShaft';
import { useElevatorWebsocket } from '../hook/useElevatorWebsocket';

const NUM_ELEVATORS = 6;
const TOTAL_FLOORS = 10;

export default function ElevatorDashboard() {
  const { data, isConnected } = useElevatorWebsocket('ws://127.0.0.1:8000/ws/step');

  const step = data?.step ?? 0;
  const totalScore = data?.total_score ?? 0;
  const currentReward = data?.reward ?? 0;
  
  const elevatorsList = data?.elevators ?? Array(NUM_ELEVATORS).fill(0);
  const directionsList = data?.directions ?? Array(NUM_ELEVATORS).fill(0);
  
  // ดึงข้อมูล hall_calls และ car_calls (ป้องกัน Error หากข้อมูลยังไม่มา)
  const hallCalls = data?.hall_calls ?? Array(20).fill(0);
  const carCalls = data?.car_calls ?? Array(NUM_ELEVATORS).fill(Array(TOTAL_FLOORS).fill(0));

  return (
    <div className="min-h-screen bg-[#181818] text-zinc-200 font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
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
                {currentReward.toFixed(4)}
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

        {/* พื้นที่แสดงผลหลัก แบ่งเป็น 2 ส่วน */}
        <div className="flex gap-8 items-start">
          
          {/* แผงแสดง Hall Calls (ซ้ายมือ) */}
          <aside className="w-40 bg-[#1c1c1c] border border-zinc-800 rounded-lg p-3 py-4.5 flex flex-col shadow-lg shrink-0">
            <div className="text-center text-xs font-bold text-zinc-500 mb-3 tracking-widest">HALL CALLS</div>
            <div className="flex flex-col space-y-1.5">
              {/* วนลูปสร้างชั้น 10 ลงมา 1 */}
              {Array.from({ length: TOTAL_FLOORS }).reverse().map((_, i) => {
                const floorIndex = TOTAL_FLOORS - 1 - i; // 9 ถึง 0
                const displayFloor = floorIndex + 1;
                const upCount = hallCalls[floorIndex]; // 10 ตัวแรก
                const downCount = hallCalls[floorIndex + 10]; // 10 ตัวหลัง

                return (
                  <div key={displayFloor} className="flex items-center justify-between bg-[#232323] p-1.5 rounded border border-zinc-800/50 h-13">
                    <span className="text-xs font-mono font-bold text-zinc-400 w-4">{displayFloor}</span>
                    <div className="flex space-x-1">
                      {/* ปุ่ม UP */}
                      <div className={`flex flex-col items-center justify-center w-7 h-7 rounded border ${
                        upCount > 0 ? 'bg-blue-500/10 border-blue-500/50 text-blue-400' : 'bg-zinc-900 border-zinc-800 text-zinc-700'
                      }`}>
                        <span className="text-[8px] leading-none mb-0.5">▲</span>
                        <span className="text-[10px] font-mono leading-none">{upCount}</span>
                      </div>
                      {/* ปุ่ม DOWN */}
                      <div className={`flex flex-col items-center justify-center w-7 h-7 rounded border ${
                        downCount > 0 ? 'bg-orange-500/10 border-orange-500/50 text-orange-400' : 'bg-zinc-900 border-zinc-800 text-zinc-700'
                      }`}>
                        <span className="text-[10px] font-mono leading-none mb-0.5">{downCount}</span>
                        <span className="text-[8px] leading-none">▼</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </aside>

          {/* กริตแสดงลิฟต์ทั้ง 6 ตัว (ขวามือ) */}
          <main className="flex-1 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {elevatorsList.map((floor, index) => {
              const dir = directionsList[index];
              let action: 'IDLE' | 'UP' | 'DOWN' = 'IDLE';
              if (dir > 0) action = 'UP';
              else if (dir < 0) action = 'DOWN';

              const elevatorData: ElevatorData = {
                id: index + 1,
                floor: floor,
                action: action,
                reward: currentReward,
                carCalls: carCalls[index], // ส่ง array ความต้องการไปแต่ละชั้นของลิฟต์ตัวนี้
              };

              return <ElevatorShaft key={elevatorData.id} elevator={elevatorData} />;
            })}
          </main>

        </div>
      </div>
    </div>
  );
}