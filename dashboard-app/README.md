# Dashboard Analytics - Next.js

Dashboard moderno e responsivo construído com Next.js, Tailwind CSS, shadcn/ui e Recharts.

## 🚀 Tecnologias

- **Next.js 14** - Framework React com App Router
- **Tailwind CSS** - Framework CSS utilitário
- **shadcn/ui** - Componentes UI reutilizáveis
- **Recharts** - Biblioteca de gráficos para React
- **Lucide React** - Ícones modernos
- **TypeScript** - Tipagem estática

## 🎨 Design System

- **Cores**: Fundo escuro (#0B0F1A), cards (#0F172A)
- **Tipografia**: Fonte Inter
- **Espaçamento**: Sistema 16/24
- **Bordas**: 16px radius
- **Tema**: Dark-by-default

## 📱 Funcionalidades

- **Header**: Logo, título e busca
- **KPIs**: 4 métricas principais com indicadores de mudança
- **Gráfico de Área**: Tráfego mensal (12 meses)
- **Gráfico de Barras**: Conversões por canal
- **Tabela**: Atividades recentes
- **Responsivo**: Grid adaptativo (1/2/4 colunas)

## 🛠️ Instalação

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar produção
npm start
```

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env.local` para configurar APIs:

```env
# Exemplo para conectar com API real
NEXT_PUBLIC_API_URL=https://api.exemplo.com
NEXT_PUBLIC_ANALYTICS_KEY=sua_chave_aqui
```

### Dados Mock
Os dados atuais estão em `src/lib/mock-data.ts`. Para conectar com API real:

1. Substitua as importações dos dados mock
2. Use `useEffect` ou Server Components para fetch
3. Implemente loading states com os componentes Skeleton
4. Adicione error boundaries para tratamento de erros

## 📊 Componentes

### KpiCard
Exibe métricas com ícone, valor e indicador de mudança.

### ChartCard
Wrapper para gráficos com título e descrição.

### AreaChart
Gráfico de área para dados temporais com gradiente e tooltip custom.

### BarChart
Gráfico de barras para comparações com tooltip informativo.

### RecentTable
Tabela de atividades com badges de status e formatação.

## 🎯 Acessibilidade

- **ARIA labels** em todos os gráficos
- **Contraste AA** garantido
- **Navegação por teclado** funcional
- **Screen readers** compatível
- **Ícones** com `aria-hidden="true"`

## 📱 Responsividade

- **Mobile**: 1 coluna
- **Tablet**: 2 colunas
- **Desktop**: 4 colunas para KPIs, 2 para gráficos

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm run build
vercel --prod
```

### Outros
```bash
npm run build
npm start
```

## 🔄 Atualizações

Para atualizar dependências:

```bash
npm update
npm audit fix
```

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
