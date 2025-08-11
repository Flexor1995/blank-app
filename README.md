# 🤖 Sistema de Agendamento de Barbearia com SuperAgentes + Make

Sistema inteligente para automatizar agendamentos de barbearia através de WhatsApp, integrando SuperAgentes (IA conversacional) com Make (automação de workflows).

## 🎯 Funcionalidades Principais

### 📅 Gestão de Agendamentos
- **Criar agendamento**: Processa solicitações e confirma horários
- **Verificar disponibilidade**: Consulta agenda em tempo real
- **Cancelar agendamento**: Processa cancelamentos com confirmação
- **Remarcar agendamento**: Permite alteração de data/horário
- **Confirmação automática**: Envia lembretes e confirmações

### 🤖 Inteligência Artificial
- **Processamento de linguagem natural**: Entende intenções do cliente
- **Contexto conversacional**: Mantém histórico da conversa
- **Respostas personalizadas**: Adapta-se ao estilo do cliente
- **Fallback inteligente**: Redireciona para atendimento humano quando necessário

### 🔄 Automação com Make
- **Workflows inteligentes**: Roteamento automático de mensagens
- **Notificações agendadas**: Lembretes automáticos
- **Integração com sistemas**: CRM, agenda, pagamentos
- **Monitoramento em tempo real**: Métricas e alertas

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   SuperAgentes  │    │      Make       │
│   Business API  │◄──►│   (IA Agent)    │◄──►│   (Workflows)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Python Backend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Webhook   │  │   Webhook   │  │   Webhook   │            │
│  │SuperAgentes │  │    Make     │  │  WhatsApp   │            │
│  │   Port 5000 │  │  Port 5001  │  │  Port 5002  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Agente    │  │ Agendamento │  │   Banco     │            │
│  │  Principal  │  │   Logic     │  │   Dados     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estrutura do Projeto

```
barbearia-scheduling/
├── agents/                          # Agentes de IA
│   ├── barber_agent.py             # Agente principal
│   ├── scheduling_logic.py         # Lógica de agendamento
│   └── whatsapp_handler.py         # Handler do WhatsApp
├── config/                          # Configurações
│   ├── settings.py                 # Configurações principais
│   └── prompts.py                  # Prompts de IA
├── workflows/                       # Fluxos de trabalho
│   ├── make_scenarios/             # Cenários do Make
│   │   └── barber_scheduling_scenario.json
│   └── webhooks/                   # Webhooks
│       ├── superagentes_webhook.py # Webhook SuperAgentes
│       ├── make_webhook.py         # Webhook Make
│       ├── webhook_config.py       # Config webhooks
│       └── main.py                 # Gerenciador webhooks
├── utils/                           # Utilitários
├── logs/                            # Logs do sistema
├── .env.example                     # Exemplo de variáveis
├── requirements.txt                 # Dependências Python
├── start_system.py                  # Script de inicialização
└── README.md                        # Esta documentação
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.8+
- PostgreSQL
- Redis
- Conta no SuperAgentes
- Conta no Make
- WhatsApp Business API

### 2. Clone e Instalação
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd barbearia-scheduling

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 3. Configuração das Variáveis
```bash
# SuperAgentes
SUPERAGENTES_API_KEY=sua_chave_api
SUPERAGENTES_AGENT_ID=seu_agent_id

# Make
MAKE_API_KEY=sua_chave_make
MAKE_SCENARIO_ID=seu_cenario_id

# WhatsApp
WHATSAPP_ACCESS_TOKEN=seu_token_whatsapp
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id

# Banco de Dados
DATABASE_HOST=localhost
DATABASE_NAME=barbearia_scheduling
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha
```

## 🎮 Como Usar

### Iniciar o Sistema
```bash
# Inicia todos os serviços
python start_system.py start

# Verifica status
python start_system.py status

# Para o sistema
python start_system.py stop
```

### Comandos Disponíveis
- `start` - Inicia todos os serviços
- `stop` - Para todos os serviços
- `restart` - Reinicia todos os serviços
- `status` - Mostra status atual
- `health` - Verifica saúde do sistema
- `help` - Mostra ajuda

## 🔧 Configuração do Make

### 1. Criar Cenário
1. Acesse [Make.com](https://www.make.com)
2. Crie um novo cenário
3. Configure o webhook de entrada
4. Adicione roteamento por intenção
5. Configure ações de agendamento

### 2. Estrutura do Cenário
```json
{
  "trigger": "webhook",
  "router": "intent_classification",
  "actions": {
    "schedule": "create_appointment",
    "check_availability": "query_calendar",
    "cancel": "cancel_appointment",
    "reschedule": "update_appointment"
  }
}
```

### 3. Webhook de Entrada
- **URL**: `https://seudominio.com/webhook/make`
- **Método**: POST
- **Headers**: `Authorization: Bearer <seu_token>`
- **Body**: JSON com dados da mensagem

## 📱 Configuração do WhatsApp

### 1. WhatsApp Business API
1. Configure sua conta no Meta for Developers
2. Obtenha o Access Token
3. Configure o Phone Number ID
4. Configure o webhook de verificação

### 2. Webhook de Verificação
- **URL**: `https://seudominio.com/webhook/whatsapp`
- **Verify Token**: Token personalizado para verificação
- **Campos**: `messages`, `message_status`

## 🤖 Configuração do SuperAgentes

### 1. Criar Agente
1. Acesse [SuperAgentes.com](https://superagentes.com)
2. Crie um novo agente
3. Configure a personalidade usando os prompts
4. Configure o webhook de saída

### 2. Webhook de Saída
- **URL**: `https://seudominio.com/webhook/superagentes`
- **Método**: POST
- **Headers**: `Authorization: Bearer <seu_token>`
- **Body**: JSON com resposta do agente

## 📊 Monitoramento e Logs

### Logs do Sistema
- **Localização**: `logs/`
- **Formato**: Estruturado com timestamp
- **Níveis**: INFO, WARNING, ERROR, DEBUG

### Métricas Disponíveis
- Taxa de resposta
- Tempo de processamento
- Taxa de erro
- Conexões ativas
- Uso de memória

### Endpoints de Status
- `/webhook/superagentes/status` - Status SuperAgentes
- `/webhook/make/status` - Status Make
- `/webhook/whatsapp/status` - Status WhatsApp

## 🔒 Segurança

### Autenticação
- Tokens Bearer para webhooks
- Verificação de origem das requisições
- Rate limiting por IP/endpoint

### CORS
- Configuração restritiva
- Origens permitidas configuráveis
- Headers de segurança

### Rate Limiting
- Limite por minuto configurável
- Burst size configurável
- Armazenamento em Redis

## 🧪 Testes

### Testes Automatizados
```bash
# Executa todos os testes
pytest

# Testes com cobertura
pytest --cov=.

# Testes específicos
pytest tests/test_webhooks.py
```

### Testes Manuais
```bash
# Testa webhook SuperAgentes
curl -X POST http://localhost:5000/webhook/superagentes/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "message"}'

# Testa webhook Make
curl -X POST http://localhost:5001/webhook/make/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "schedule"}'
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Webhook não responde
```bash
# Verifica se o serviço está rodando
python start_system.py status

# Verifica logs
tail -f logs/webhooks_main.log

# Testa conectividade
curl http://localhost:5000/webhook/superagentes/status
```

#### 2. Erro de conexão com banco
```bash
# Verifica se PostgreSQL está rodando
sudo systemctl status postgresql

# Testa conexão
psql -h localhost -U postgres -d barbearia_scheduling
```

#### 3. Erro de autenticação
```bash
# Verifica variáveis de ambiente
cat .env | grep -E "(API_KEY|TOKEN)"

# Testa token
curl -H "Authorization: Bearer <seu_token>" \
  http://localhost:5000/webhook/superagentes/status
```

### Logs de Debug
```bash
# Ativa logs detalhados
export LOG_LEVEL=DEBUG

# Reinicia sistema
python start_system.py restart
```

## 📈 Escalabilidade

### Estratégias de Escala
- **Load Balancing**: Múltiplas instâncias
- **Cache Redis**: Sessões e dados frequentes
- **Fila de Processamento**: Redis + Celery
- **Microserviços**: Separação por funcionalidade

### Monitoramento em Produção
- **Prometheus**: Métricas do sistema
- **Grafana**: Dashboards visuais
- **AlertManager**: Notificações automáticas
- **ELK Stack**: Logs centralizados

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Padrões de Código
- **Python**: PEP 8
- **Documentação**: Docstrings em português
- **Testes**: Cobertura mínima de 80%
- **Commits**: Conventional Commits

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

### Canais de Suporte
- **Issues**: GitHub Issues
- **Documentação**: Este README
- **Comunidade**: Discord/Slack (se disponível)

### Recursos Adicionais
- [Documentação SuperAgentes](https://docs.superagentes.com)
- [Documentação Make](https://www.make.com/en/help)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

## 🎉 Agradecimentos

- Equipe SuperAgentes pela plataforma de IA
- Make.com pela automação de workflows
- Meta pelo WhatsApp Business API
- Comunidade Python pelo ecossistema robusto

---

**Desenvolvido com ❤️ para automatizar agendamentos de barbearia**
