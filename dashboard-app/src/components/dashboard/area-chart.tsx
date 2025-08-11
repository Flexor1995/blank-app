"use client";

import { Area, AreaChart as RechartsAreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCompactNumber } from "@/lib/formatters";

interface TrafficData {
  month: string;
  visitors: number;
  pageviews: number;
}

interface AreaChartProps {
  data: TrafficData[];
}

export function AreaChart({ data }: AreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RechartsAreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorVisitors" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
          </linearGradient>
          <linearGradient id="colorPageviews" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="month" 
          stroke="#94A3B8" 
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis 
          stroke="#94A3B8" 
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => formatCompactNumber(value)}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#0F172A",
            border: "1px solid #334155",
            borderRadius: "8px",
            color: "#ffffff"
          }}
          labelStyle={{ color: "#94A3B8" }}
          formatter={(value: number, name: string) => [
            formatCompactNumber(value),
            name === "visitors" ? "Visitantes" : "Visualizações"
          ]}
        />
        <Area
          type="monotone"
          dataKey="visitors"
          stroke="#3B82F6"
          fillOpacity={1}
          fill="url(#colorVisitors)"
          strokeWidth={2}
          dot={false}
        />
        <Area
          type="monotone"
          dataKey="pageviews"
          stroke="#10B981"
          fillOpacity={1}
          fill="url(#colorPageviews)"
          strokeWidth={2}
          dot={false}
        />
      </RechartsAreaChart>
    </ResponsiveContainer>
  );
}