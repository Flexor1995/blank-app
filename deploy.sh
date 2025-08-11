#!/bin/bash

# Script de Deploy Automatizado para Sistema de Agendamento de Barbearia
# Este script configura e inicia todo o ambiente

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
   exit 1
fi

# Verifica se Docker está instalado
check_docker() {
    log "Verificando instalação do Docker..."
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado"
        log "Instalando Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        success "Docker instalado com sucesso"
        warning "Reinicie o terminal ou execute: newgrp docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado"
        log "Instalando Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        success "Docker Compose instalado com sucesso"
    fi
    
    success "Docker e Docker Compose verificados"
}

# Verifica se Python está instalado
check_python() {
    log "Verificando instalação do Python..."
    if ! command -v python3 &> /dev/null; then
        error "Python 3 não está instalado"
        log "Instalando Python 3..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
        success "Python 3 instalado com sucesso"
    fi
    
    success "Python 3 verificado"
}

# Cria arquivo .env se não existir
setup_env() {
    log "Configurando variáveis de ambiente..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            warning "Arquivo .env criado a partir do exemplo"
            warning "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais antes de continuar"
            echo ""
            echo "Pressione ENTER após configurar o arquivo .env..."
            read
        else
            error "Arquivo .env.example não encontrado"
            exit 1
        fi
    else
        success "Arquivo .env já existe"
    fi
}

# Cria diretórios necessários
create_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p nginx/ssl
    
    success "Diretórios criados"
}

# Configura banco de dados
setup_database() {
    log "Configurando banco de dados..."
    
    # Cria arquivo de inicialização do banco
    cat > init-db.sql << 'EOF'
-- Script de inicialização do banco de dados
CREATE DATABASE IF NOT EXISTS barbearia_scheduling;
\c barbearia_scheduling;

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de serviços
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    duration INTEGER NOT NULL, -- em minutos
    price DECIMAL(10,2) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    service_id INTEGER REFERENCES services(id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, confirmed, cancelled, completed
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de horários disponíveis
CREATE TABLE IF NOT EXISTS available_slots (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de webhooks
CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time INTEGER,
    payload_size INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_client ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_available_slots_date ON available_slots(date);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_timestamp ON webhook_logs(timestamp);

-- Inserir dados iniciais
INSERT INTO services (name, duration, price) VALUES 
    ('Corte de Cabelo', 30, 25.00),
    ('Barba', 20, 15.00),
    ('Corte + Barba', 45, 35.00),
    ('Hidratação', 45, 40.00)
ON CONFLICT DO NOTHING;

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar timestamps
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOF

    success "Script de banco de dados criado"
}

# Configura monitoramento
setup_monitoring() {
    log "Configurando sistema de monitoramento..."
    
    # Configuração do Prometheus
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'barbearia-app'
    static_configs:
      - targets: ['barbearia-app:5000', 'barbearia-app:5001', 'barbearia-app:5002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF

    # Configuração do Grafana
    cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    success "Configuração de monitoramento criada"
}

# Configura Nginx
setup_nginx() {
    log "Configurando Nginx..."
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream barbearia_app {
        server barbearia-app:5000;
        server barbearia-app:5001;
        server barbearia-app:5002;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://barbearia_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

    success "Configuração do Nginx criada"
}

# Inicia os serviços
start_services() {
    log "Iniciando serviços com Docker Compose..."
    
    # Para serviços existentes se houver
    docker-compose down 2>/dev/null || true
    
    # Inicia todos os serviços
    docker-compose up -d
    
    success "Serviços iniciados com Docker Compose"
}

# Verifica status dos serviços
check_services() {
    log "Verificando status dos serviços..."
    
    # Aguarda um pouco para os serviços inicializarem
    sleep 10
    
    # Verifica se os containers estão rodando
    if docker-compose ps | grep -q "Up"; then
        success "Todos os serviços estão rodando"
        
        echo ""
        echo "🌐 URLs dos serviços:"
        echo "  📱 SuperAgentes Webhook: http://localhost:5000"
        echo "  🔄 Make Webhook: http://localhost:5001"
        echo "  💬 WhatsApp Webhook: http://localhost:5002"
        echo "  📊 Prometheus: http://localhost:9090"
        echo "  📈 Grafana: http://localhost:3000 (admin/admin123)"
        echo "  🗄️  PostgreSQL: localhost:5432"
        echo "  🔴 Redis: localhost:6379"
        
    else
        error "Alguns serviços não estão rodando"
        docker-compose ps
        exit 1
    fi
}

# Função principal
main() {
    echo ""
    echo "🚀 Sistema de Agendamento de Barbearia - Deploy Automatizado"
    echo "=========================================================="
    echo ""
    
    log "Iniciando processo de deploy..."
    
    # Verificações iniciais
    check_docker
    check_python
    
    # Configuração do ambiente
    setup_env
    create_directories
    setup_database
    setup_monitoring
    setup_nginx
    
    # Inicia serviços
    start_services
    check_services
    
    echo ""
    success "🎉 Deploy concluído com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "  1. Configure suas credenciais no arquivo .env"
    echo "  2. Configure o webhook no SuperAgentes"
    echo "  3. Configure o cenário no Make"
    echo "  4. Configure o webhook no WhatsApp Business"
    echo ""
    echo "🛑 Para parar os serviços: docker-compose down"
    echo "🔄 Para reiniciar: docker-compose restart"
    echo "📊 Para ver logs: docker-compose logs -f"
    echo ""
}

# Executa função principal
main "$@"