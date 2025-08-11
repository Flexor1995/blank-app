import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: "increase" | "decrease";
  };
  icon: LucideIcon;
  className?: string;
}

export function KpiCard({ title, value, change, icon: Icon, className }: KpiCardProps) {
  return (
    <Card className={cn("bg-card/50 backdrop-blur-sm", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <p className={cn(
            "text-xs",
            change.type === "increase" ? "text-green-600" : "text-red-600"
          )}>
            {change.type === "increase" ? "+" : "-"}{Math.abs(change.value)}%
          </p>
        )}
      </CardContent>
    </Card>
  );
}