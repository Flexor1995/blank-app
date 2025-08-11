import { DashboardHeader } from "@/components/dashboard/header";
import { KpiCard } from "@/components/ui/kpi-card";
import { ChartCard } from "@/components/ui/chart-card";
import { AreaChart } from "@/components/dashboard/area-chart";
import { BarChart } from "@/components/dashboard/bar-chart";
import { RecentTable } from "@/components/dashboard/recent-table";
import { DollarSign, ShoppingCart, TrendingUp, Users } from "lucide-react";
import { trafficData, conversionData, recentActivity } from "@/lib/mock-data";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <DashboardHeader />

        {/* KPIs */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Receita Total"
            value="R$ 1.250.000"
            change={{ value: 12.5, type: "increase" }}
            icon={DollarSign}
          />
          <KpiCard
            title="Total de Pedidos"
            value="12.500"
            change={{ value: 8.2, type: "increase" }}
            icon={ShoppingCart}
          />
          <KpiCard
            title="Taxa de Conversão"
            value="3.2%"
            change={{ value: 2.1, type: "increase" }}
            icon={TrendingUp}
          />
          <KpiCard
            title="Ticket Médio"
            value="R$ 100"
            change={{ value: 1.8, type: "decrease" }}
            icon={Users}
          />
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartCard
            title="Tráfego Mensal"
            description="Evolução do número de visitantes nos últimos 12 meses"
            className="lg:col-span-2"
          >
            <AreaChart data={trafficData} />
          </ChartCard>

          <ChartCard
            title="Conversões por Canal"
            description="Receita gerada por canal de marketing"
          >
            <BarChart data={conversionData} />
          </ChartCard>
        </div>

        {/* Tabela de Atividades Recentes */}
        <div className="bg-slate-800 rounded-lg border border-slate-700">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Atividades Recentes</h3>
            <p className="text-slate-400 text-sm mb-4">
              Últimas ações dos usuários no sistema
            </p>
          </div>
          <RecentTable data={recentActivity} />
        </div>
      </div>
    </div>
  );
}