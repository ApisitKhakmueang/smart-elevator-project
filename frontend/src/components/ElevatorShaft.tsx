// components/ElevatorShaft.tsx
import React from 'react';

export type ElevatorData = {
  id: number;
  floor: number;
  action: 'IDLE' | 'UP' | 'DOWN';
  reward: number; // จะรับค่า Step Reward จาก JSON
};

interface Props {
  elevator: ElevatorData;
}

const TOTAL_FLOORS = 10;

export default function ElevatorShaft({ elevator }: Props) {
  // สมมติว่า floor จาก JSON เป็น 0-indexed (0-9) เราบวก 1 เพื่อให้แสดงเป็นชั้น 1-10
  // หาก JSON ส่งมาเป็น 1-10 อยู่แล้ว สามารถลบ +1 ออกได้ครับ
  const displayFloor = elevator.floor + 1; 
  const bottomPosition = ((displayFloor - 1) / TOTAL_FLOORS) * 100;

  return (
    <div className="flex flex-col items-center space-y-4 w-full">
      {/* Header ของลิฟต์ */}
      <div className="text-zinc-400 text-sm font-semibold tracking-wider">
        ELEVATOR {elevator.id}
      </div>

      {/* ช่องลิฟต์ (Shaft) */}
      <div className="relative w-20 h-96 bg-[#1c1c1c] border border-zinc-800 rounded-md overflow-hidden flex flex-col-reverse shadow-inner">
        {Array.from({ length: TOTAL_FLOORS }).map((_, i) => (
          <div
            key={i}
            className="flex-1 w-full border-t border-zinc-800/50 flex items-center justify-center opacity-30"
          >
            <span className="text-[10px] text-zinc-500">{i + 1}</span>
          </div>
        ))}

        {/* ตัวลิฟต์ (Car) */}
        <div
          className="absolute w-full flex items-center justify-center bg-[#3ECF8E] border-2 border-[#1c1c1c] rounded-sm transition-all duration-300 ease-out shadow-[0_0_10px_rgba(62,207,142,0.3)]"
          style={{
            height: `${100 / TOTAL_FLOORS}%`,
            bottom: `${bottomPosition}%`,
          }}
        >
          <span className="text-zinc-950 font-bold text-xs">
            {displayFloor}
          </span>
        </div>
      </div>

      {/* แผงแสดง Action และ Reward */}
      <div className="w-full bg-[#232323] border border-zinc-800 rounded-lg p-3 flex flex-col space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-xs text-zinc-500">Action</span>
          <span
            className={`text-[10px] font-mono font-medium px-2 py-0.5 rounded border ${
              elevator.action === 'UP'
                ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                : elevator.action === 'DOWN'
                ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                : 'bg-zinc-800 text-zinc-400 border-zinc-700'
            }`}
          >
            {elevator.action}
          </span>
        </div>
      </div>
    </div>
  );
}