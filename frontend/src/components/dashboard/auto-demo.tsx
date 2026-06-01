"use client";
import { useEffect } from "react";
import { api } from "@/lib/api";




export function AutoDemo() {
  useEffect(() => {
    api.torcsStart({ mode: "simulated", total_laps: 58 });
    return () => { api.torcsStop(); };
  }, []);
  return null;
}
