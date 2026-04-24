import { useState, useEffect, useMemo } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

interface CarCalls {
  car_call: number[]
}

export interface ElevatorState {
  step: number;
  total_score: number;
  elevators: number[];
  directions: number[];
  hall_calls: number[]
  car_calls: CarCalls[]
  reward: number;
  done: boolean;
}

export function useElevatorWebsocket() {
  const [data, setData] = useState<ElevatorState | null>(null);

  const wsUrl = useMemo(() => {
    return `${process.env.NEXT_PUBLIC_BACKEND_WEBSOCKET}/step`
  }, [])

  // 🌟 1. ใช้ useWebSocket แทน WebSocket API แบบเดิม
  const { lastJsonMessage, readyState } = useWebSocket(wsUrl, {
    shouldReconnect: () => true,
    reconnectAttempts: 20,
    reconnectInterval: 3000, // พยายามเชื่อมต่อใหม่ทุกๆ 3 วินาที หากเซิร์ฟเวอร์หลุด
  });

  // 🌟 2. จัดการข้อมูลจาก WebSocket
  useEffect(() => {
    if (lastJsonMessage !== null) {
      // เนื่องจาก JSON ของ Elevator ไม่ได้ครอบด้วย type เหมือนระบบ Booking 
      // เราสามารถนำ lastJsonMessage มาระบุ type เป็น ElevatorState ได้เลย
      const message = lastJsonMessage as ElevatorState;
      
      if (message) {
        setData(message);
      }
    }
  }, [lastJsonMessage]);

  // 🌟 3. ตรวจสอบสถานะการเชื่อมต่อเพื่อส่งกลับไปแสดงผลที่ UI
  const isConnected = readyState === ReadyState.OPEN;

  return { data, isConnected };
}