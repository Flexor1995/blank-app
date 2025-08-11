import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency } from "@/lib/formatters";
import { RecentActivity } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";

interface RecentTableProps {
  data: RecentActivity[];
}

function getStatusBadge(status: RecentActivity['status']) {
  const variants = {
    completed: "bg-green-100 text-green-800 border-green-200",
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    failed: "bg-red-100 text-red-800 border-red-200",
  };
  
  return (
    <Badge className={variants[status]}>
      {status === 'completed' && 'Concluído'}
      {status === 'pending' && 'Pendente'}
      {status === 'failed' && 'Falhou'}
    </Badge>
  );
}

export function RecentTable({ data }: RecentTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Usuário</TableHead>
          <TableHead>Ação</TableHead>
          <TableHead>Valor</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Data</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((activity) => (
          <TableRow key={activity.id}>
            <TableCell className="font-medium">{activity.user}</TableCell>
            <TableCell>{activity.action}</TableCell>
            <TableCell>
              {activity.amount ? formatCurrency(activity.amount) : '-'}
            </TableCell>
            <TableCell>{getStatusBadge(activity.status)}</TableCell>
            <TableCell>
              {new Date(activity.timestamp).toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}