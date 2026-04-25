import { useState, useMemo } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

interface CarCalls {
  car_call: number[]
}

export interface ElevatorState {
  step: number;
  total_score: number;
  elevators: number[];
  directions: number[];
  hall_calls: number[];
  car_calls: CarCalls[]; // หรือ number[][] ตามที่ Backend ส่งมา
  reward: number;
  done: boolean;
}

export function useElevatorWebsocket() {
  const [data, setData] = useState<ElevatorState | null>(null);

  const wsUrl = useMemo(() => {
    return `${process.env.NEXT_PUBLIC_BACKEND_WEBSOCKET}/step`;
  }, []);

  // 🌟 ใช้ onMessage จัดการข้อมูลโดยตรง แทนการใช้ useEffect
  const { readyState, getWebSocket } = useWebSocket(wsUrl, {
    shouldReconnect: () => true,
    reconnectAttempts: 20,
    reconnectInterval: 3000,
    onMessage: (event) => {
      try {
        // แปลงข้อมูล String จาก WebSocket ให้เป็น JSON
        const message: ElevatorState = JSON.parse(event.data);
        
        // 1. ตรวจสอบว่าครบ 200 step หรือยัง
        if (message.step >= 200) {
          console.log("🔄 Reached 200 steps. Forcing WebSocket reconnect...");
          getWebSocket()?.close(); // บังคับตัดการเชื่อมต่อ
          return; // หยุดการทำงานทันที ไม่ต้องเซ็ต State ต่อ
        }
        
        // 2. ถ้ายังไม่ถึง 200 ก็เซ็ตข้อมูลลง State ตามปกติ
        setData(message);
        
      } catch (error) {
        console.error("Failed to parse websocket message", error);
      }
    }
  });

  const isConnected = readyState === ReadyState.OPEN;

  return { data, isConnected };
}