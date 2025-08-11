"use client";

import { Bar, BarChart as RechartsBarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCurrency } from "@/lib/formatters";

interface ConversionData {
  channel: string;
  revenue: number;
  conversions: number;
}

interface BarChartProps {
  data: ConversionData[];
}

export function BarChart({ data }: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RechartsBarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="channel" 
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
          tickFormatter={(value) => formatCurrency(value)}
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
            name === "revenue" ? formatCurrency(value) : value.toLocaleString(),
            name === "revenue" ? "Receita" : "Conversões"
          ]}
        />
        <Bar 
          dataKey="revenue" 
          fill="#3B82F6" 
          radius={[4, 4, 0, 0]}
          name="Receita"
        />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}