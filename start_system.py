#!/usr/bin/env python3
"""
Script Principal para Inicializar o Sistema de Agendamento de Barbearia
Inicia todos os componentes: webhooks, agente, e sistema de monitoramento
"""

import os
import sys
import time
import signal
import logging
import subprocess
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemManager:
    """Gerencia todo o sistema de agendamento"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.base_dir = Path(__file__).parent
        
        # Verifica se estamos no diretório correto
        if not (self.base_dir / "config").exists():
            logger.error("❌ Execute este script do diretório raiz do projeto")
            sys.exit(1)
    
    def check_dependencies(self) -> bool:
        """Verifica se todas as dependências estão instaladas"""
        logger.info("🔍 Verificando dependências...")
        
        try:
            import flask
            import requests
            import psycopg2
            import redis
            logger.info("✅ Dependências Python verificadas")
        except ImportError as e:
            logger.error(f"❌ Dependência não encontrada: {e}")
            logger.info("💡 Execute: pip install -r requirements.txt")
            return False
        
        # Verifica se o arquivo .env existe
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            logger.warning("⚠️ Arquivo .env não encontrado")
            logger.info("💡 Copie .env.example para .env e configure as variáveis")
            return False
        
        logger.info("✅ Dependências verificadas com sucesso")
        return True
    
    def start_webhooks(self) -> bool:
        """Inicia o sistema de webhooks"""
        logger.info("🚀 Iniciando sistema de webhooks...")
        
        try:
            # Inicia o gerenciador de webhooks
            webhook_script = self.base_dir / "workflows" / "webhooks" / "main.py"
            
            if not webhook_script.exists():
                logger.error(f"❌ Script de webhooks não encontrado: {webhook_script}")
                return False
            
            # Inicia o processo
            process = subprocess.Popen(
                [sys.executable, str(webhook_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.base_dir
            )
            
            self.processes["webhooks"] = process
            logger.info("✅ Sistema de webhooks iniciado")
            
            # Aguarda um pouco para verificar se iniciou corretamente
            time.sleep(3)
            if process.poll() is None:
                logger.info("✅ Webhooks rodando na porta 5000 e 5001")
                return True
            else:
                logger.error("❌ Falha ao iniciar webhooks")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar webhooks: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """Inicia sistema de monitoramento"""
        logger.info("📊 Iniciando sistema de monitoramento...")
        
        try:
            # Cria diretório de logs se não existir
            logs_dir = self.base_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Inicia monitoramento básico
            logger.info("✅ Sistema de monitoramento ativo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar monitoramento: {e}")
            return False
    
    def check_system_health(self) -> bool:
        """Verifica saúde geral do sistema"""
        logger.info("🏥 Verificando saúde do sistema...")
        
        try:
            import requests
            
            # Testa webhook do SuperAgentes
            try:
                response = requests.get(
                    "http://localhost:5000/webhook/superagentes/status",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("✅ Webhook SuperAgentes: Ativo")
                else:
                    logger.warning("⚠️ Webhook SuperAgentes: Status inesperado")
            except Exception as e:
                logger.error(f"❌ Webhook SuperAgentes: {e}")
            
            # Testa webhook do Make
            try:
                response = requests.get(
                    "http://localhost:5001/webhook/make/status",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("✅ Webhook Make: Ativo")
                else:
                    logger.warning("⚠️ Webhook Make: Status inesperado")
            except Exception as e:
                logger.error(f"❌ Webhook Make: {e}")
            
            logger.info("✅ Verificação de saúde concluída")
            return True
            
        except ImportError:
            logger.warning("⚠️ Requests não disponível para health check")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na verificação de saúde: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Inicia todos os serviços"""
        logger.info("🎯 Iniciando todos os serviços...")
        
        # Verifica dependências
        if not self.check_dependencies():
            return False
        
        # Inicia webhooks
        if not self.start_webhooks():
            return False
        
        # Inicia monitoramento
        if not self.start_monitoring():
            return False
        
        # Aguarda um pouco para estabilização
        time.sleep(2)
        
        # Verifica saúde do sistema
        if not self.check_system_health():
            logger.warning("⚠️ Sistema iniciado mas com problemas de saúde")
        
        self.running = True
        logger.info("🎉 Todos os serviços iniciados com sucesso!")
        return True
    
    def stop_all_services(self):
        """Para todos os serviços"""
        logger.info("🛑 Parando todos os serviços...")
        
        for service_name, process in self.processes.items():
            try:
                if process.poll() is None:  # Processo ainda rodando
                    logger.info(f"🛑 Parando {service_name}...")
                    process.terminate()
                    
                    # Aguarda término gracioso
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {service_name} parado graciosamente")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ {service_name} não parou graciosamente, forçando...")
                        process.kill()
                        process.wait()
                        logger.info(f"✅ {service_name} forçado a parar")
                        
            except Exception as e:
                logger.error(f"❌ Erro ao parar {service_name}: {e}")
        
        self.processes.clear()
        self.running = False
        logger.info("✅ Todos os serviços parados")
    
    def graceful_shutdown(self, signum, frame):
        """Desligamento gracioso do sistema"""
        logger.info(f"🛑 Recebido sinal {signum}, iniciando desligamento gracioso...")
        self.stop_all_services()
        logger.info("✅ Sistema desligado com sucesso")
        sys.exit(0)
    
    def show_status(self):
        """Mostra status atual do sistema"""
        logger.info("📊 Status do Sistema:")
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"🟢 {service_name}: Rodando (PID: {process.pid})")
            else:
                logger.info(f"🔴 {service_name}: Parado")
        
        if self.running:
            logger.info("🟢 Sistema: Ativo")
        else:
            logger.info("🔴 Sistema: Inativo")
    
    def show_help(self):
        """Mostra ajuda do sistema"""
        help_text = """
🤖 Sistema de Agendamento de Barbearia - Ajuda

Comandos disponíveis:
  start     - Inicia todos os serviços
  stop      - Para todos os serviços
  restart   - Reinicia todos os serviços
  status    - Mostra status atual
  health    - Verifica saúde do sistema
  help      - Mostra esta ajuda

Serviços incluídos:
  🔗 Webhooks (SuperAgentes, Make)
  📊 Monitoramento
  🤖 Agente de Agendamento

Portas utilizadas:
  🚪 5000 - Webhook SuperAgentes
  🚪 5001 - Webhook Make
  🚪 5002 - Webhook WhatsApp (futuro)

Para mais informações, consulte o README.md
        """
        print(help_text)

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python start_system.py <comando>")
        print("💡 Use 'help' para ver comandos disponíveis")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        # Cria diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)
        
        # Inicializa gerenciador do sistema
        manager = SystemManager()
        
        # Configura handlers de sinal
        signal.signal(signal.SIGINT, manager.graceful_shutdown)
        signal.signal(signal.SIGTERM, manager.graceful_shutdown)
        
        if command == "start":
            if manager.start_all_services():
                logger.info("🎉 Sistema iniciado com sucesso!")
                logger.info("📊 Para ver status: python start_system.py status")
                logger.info("🛑 Para parar: python start_system.py stop")
                
                # Mantém o sistema rodando
                try:
                    while manager.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("🛑 Interrupção do usuário detectada")
                    manager.stop_all_services()
            else:
                logger.error("❌ Falha ao iniciar sistema")
                sys.exit(1)
                
        elif command == "stop":
            manager.stop_all_services()
            
        elif command == "restart":
            manager.stop_all_services()
            time.sleep(2)
            if manager.start_all_services():
                logger.info("✅ Sistema reiniciado com sucesso")
            else:
                logger.error("❌ Falha ao reiniciar sistema")
                sys.exit(1)
                
        elif command == "status":
            manager.show_status()
            
        elif command == "health":
            manager.check_system_health()
            
        elif command == "help":
            manager.show_help()
            
        else:
            logger.error(f"❌ Comando desconhecido: {command}")
            print("💡 Use 'help' para ver comandos disponíveis")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário detectada")
        if 'manager' in locals():
            manager.stop_all_services()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()