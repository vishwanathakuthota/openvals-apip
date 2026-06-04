"use client";

import { Cell, RadialBar, RadialBarChart, ResponsiveContainer } from "recharts";

import type { RealityIndexItem } from "@/types/api";

const colors = ["#7cf2ba", "#e8cf6a", "#8ec5ff", "#ff8170"];

export function RealityIndexChart({ items }: { items: RealityIndexItem[] }) {
  const data = items.map((item) => ({
    name: item.entity_type,
    value: item.score,
    label: item.label
  }));

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart innerRadius="24%" outerRadius="92%" data={data} startAngle={180} endAngle={-180}>
          <RadialBar dataKey="value" background cornerRadius={8}>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={colors[index % colors.length]} />
            ))}
          </RadialBar>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
}
