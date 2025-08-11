import { Search, BarChart3 } from "lucide-react";
import { Input } from "@/components/ui/input";

export function DashboardHeader() {
  return (
    <header className="flex flex-col gap-6 pb-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <BarChart3 className="h-6 w-6 text-primary-foreground" aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard Analytics</h1>
          <p className="text-muted-foreground">
            Monitore suas métricas e performance em tempo real
          </p>
        </div>
      </div>
      
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
        <Input
          placeholder="Buscar métricas..."
          className="pl-10"
          aria-label="Buscar métricas do dashboard"
        />
      </div>
    </header>
  );
}