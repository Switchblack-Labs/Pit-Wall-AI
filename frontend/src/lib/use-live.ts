"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { Telemetry } from "./types";

const WS_URL =
  process.env.NEXT_PUBLIC_BACKEND_WS?.replace(/\/$/, "") || "ws://127.0.0.1:8000";

type Status = "connecting" | "live" | "offline";

export function useLiveTelemetry(_intervalMs = 200) {
  const [data, setData] = useState<Telemetry | null>(null);
  const [status, setStatus] = useState<Status>("connecting");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let killed = false;

    api.telemetry().then((snapshot) => {
      if (!killed && snapshot) setData(snapshot);
    });

    try {
      const ws = new WebSocket(`${WS_URL}/ws/live`);
      wsRef.current = ws;
      ws.onopen = () => { if (!killed) setStatus("live"); };
      ws.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data);
          
          
          
          if (parsed?.type === "telemetry" && parsed.data) {
            setData(parsed.data as Telemetry);
          } else if (parsed?.type === "torcs" && parsed.data) {
            
            
            setData((prev) => ({
              ...(prev ?? { speed: 0, rpm: 0, gear: 0, throttle: 0, brake: 0,
                            steering_angle: 0, track_position: 0, lap: 0,
                            fuel: 0, tire_wear: 0, timestamp: "" }),
              ...parsed.data,
            } as Telemetry));
          }
        } catch {  }
      };
      ws.onerror = () => { if (!killed) setStatus("offline"); };
      ws.onclose = () => { if (!killed) setStatus("offline"); };
    } catch {
      setStatus("offline");
    }

    return () => {
      killed = true;
      wsRef.current?.close();
    };
  }, []);

  return { data, status };
}
