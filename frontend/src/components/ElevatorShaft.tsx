// components/ElevatorShaft.tsx
import React from 'react';

export type ElevatorData = {
  id: number;
  floor: number;
  action: 'IDLE' | 'UP' | 'DOWN';
  reward: number;
  carCalls: number[]; // อาเรย์ 10 ตัวบอกจำนวนคนที่จะไปแต่ละชั้น
};

interface Props {
  elevator: ElevatorData;
}

const TOTAL_FLOORS = 10;

export default function ElevatorShaft({ elevator }: Props) {
  const displayFloor = elevator.floor + 1; 
  const bottomPosition = ((displayFloor - 1) / TOTAL_FLOORS) * 100;

  // กรองหาเฉพาะชั้นที่มีคนกดปุ่ม (car_calls > 0)
  const activeCarCalls = elevator.carCalls
    .map((count, index) => ({ floor: index + 1, count }))
    .filter((call) => call.count > 0);

  return (
    <div className="flex flex-col items-center w-full">
      {/* Header ของลิฟต์ */}
      <div className="text-zinc-400 text-[10px] font-bold tracking-[0.2em] mb-4">
        ELEVATOR {elevator.id}
      </div>

      {/* ช่องลิฟต์ (Shaft) */}
      <div className="relative w-full h-120 bg-[#141414] border border-zinc-800 rounded-md overflow-hidden flex flex-col-reverse shadow-inner">
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
          className="absolute left-0 right-0 mx-auto w-[80%] flex items-center justify-center bg-[#3ECF8E] border-2 border-[#1c1c1c] rounded-sm transition-all duration-300 ease-out shadow-[0_0_10px_rgba(62,207,142,0.3)]"
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

      {/* แผงแสดง Action และ Car Calls */}
      <div className="w-full bg-[#1c1c1c] border border-zinc-800 rounded-lg p-3 mt-4 flex flex-col space-y-3">
        
        {/* Action Status */}
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wide">Action</span>
          <span
            className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${
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

        {/* Car Calls (Destinations) */}
        <div className="flex flex-col border-t border-zinc-800 pt-2">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wide mb-1.5">Passengers Target</span>
          <div className="flex flex-wrap gap-1 min-h-6">
            {activeCarCalls.length > 0 ? (
              activeCarCalls.map((call) => (
                <span 
                  key={call.floor} 
                  className="flex items-center gap-1 text-[9px] bg-[#232323] text-zinc-300 px-1.5 py-0.5 rounded border border-zinc-700"
                >
                  Fl {call.floor}
                  <span className="text-[#3ECF8E] font-bold">({call.count})</span>
                </span>
              ))
            ) : (
              <span className="text-[10px] text-zinc-600 italic">No passengers</span>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}