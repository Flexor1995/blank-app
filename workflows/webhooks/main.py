#!/usr/bin/env python3
"""
Sistema Principal de Webhooks para Agendamento de Barbearia
Executa todos os webhooks necessários para integração SuperAgentes <-> Make
"""

import os
import sys
import time
import signal
import logging
import threading
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import SUPERAGENTES_CONFIG, MAKE_CONFIG, WHATSAPP_CONFIG
from workflows.webhooks.webhook_config import (
    get_webhook_config, 
    validate_config, 
    get_all_configs
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhooks_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebhookManager:
    """Gerencia todos os webhooks do sistema"""
    
    def __init__(self):
        self.webhooks = {}
        self.threads = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Valida configurações
        if not validate_config():
            raise ValueError("Configurações inválidas")
        
        # Carrega configurações
        self.configs = get_all_configs()
        logger.info("✅ Configurações carregadas com sucesso")
    
    def start_webhook(self, webhook_type: str) -> bool:
        """Inicia um webhook específico"""
        try:
            config = get_webhook_config(webhook_type)
            if not config:
                logger.error(f"❌ Configuração não encontrada para {webhook_type}")
                return False
            
            # Importa e inicia o webhook
            if webhook_type == "superagentes":
                from workflows.webhooks.superagentes_webhook import app as superagentes_app
                self.webhooks[webhook_type] = superagentes_app
                
            elif webhook_type == "make":
                from workflows.webhooks.make_webhook import app as make_app
                self.webhooks[webhook_type] = make_app
                
            elif webhook_type == "whatsapp":
                # Webhook do WhatsApp será implementado posteriormente
                logger.info(f"⚠️ Webhook {webhook_type} não implementado ainda")
                return False
            
            # Inicia o webhook em uma thread separada
            thread = threading.Thread(
                target=self._run_webhook,
                args=(webhook_type, config),
                daemon=True
            )
            thread.start()
            self.threads[webhook_type] = thread
            
            logger.info(f"✅ Webhook {webhook_type} iniciado na porta {config['port']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar webhook {webhook_type}: {e}")
            return False
    
    def _run_webhook(self, webhook_type: str, config: Dict[str, Any]):
        """Executa um webhook em uma thread separada"""
        try:
            app = self.webhooks[webhook_type]
            app.run(
                host=config['host'],
                port=config['port'],
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"❌ Erro na execução do webhook {webhook_type}: {e}")
    
    def start_all_webhooks(self) -> bool:
        """Inicia todos os webhooks configurados"""
        logger.info("🚀 Iniciando todos os webhooks...")
        
        webhook_types = ["superagentes", "make"]  # WhatsApp será adicionado posteriormente
        
        success_count = 0
        for webhook_type in webhook_types:
            if self.start_webhook(webhook_type):
                success_count += 1
                time.sleep(1)  # Pequena pausa entre inícios
        
        if success_count == len(webhook_types):
            logger.info(f"✅ Todos os {success_count} webhooks iniciados com sucesso")
            self.running = True
            return True
        else:
            logger.error(f"❌ Apenas {success_count}/{len(webhook_types)} webhooks iniciados")
            return False
    
    def stop_webhook(self, webhook_type: str) -> bool:
        """Para um webhook específico"""
        try:
            if webhook_type in self.threads:
                thread = self.threads[webhook_type]
                if thread.is_alive():
                    # Envia sinal de parada (implementação básica)
                    logger.info(f"🛑 Parando webhook {webhook_type}...")
                    del self.threads[webhook_type]
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao parar webhook {webhook_type}: {e}")
            return False
    
    def stop_all_webhooks(self):
        """Para todos os webhooks"""
        logger.info("🛑 Parando todos os webhooks...")
        
        for webhook_type in list(self.threads.keys()):
            self.stop_webhook(webhook_type)
        
        self.running = False
        logger.info("✅ Todos os webhooks parados")
    
    def get_webhook_status(self) -> Dict[str, Any]:
        """Retorna status de todos os webhooks"""
        status = {
            "running": self.running,
            "webhooks": {},
            "timestamp": time.time()
        }
        
        for webhook_type, thread in self.threads.items():
            status["webhooks"][webhook_type] = {
                "active": thread.is_alive(),
                "port": get_webhook_config(webhook_type).get("port", "N/A")
            }
        
        return status
    
    def health_check(self) -> Dict[str, Any]:
        """Executa verificação de saúde dos webhooks"""
        health_status = {
            "overall": "healthy",
            "webhooks": {},
            "timestamp": time.time()
        }
        
        try:
            import requests
            
            for webhook_type, thread in self.threads.items():
                config = get_webhook_config(webhook_type)
                port = config.get("port")
                
                if thread.is_alive() and port:
                    try:
                        # Testa endpoint de status
                        response = requests.get(
                            f"http://localhost:{port}/webhook/{webhook_type}/status",
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            health_status["webhooks"][webhook_type] = "healthy"
                        else:
                            health_status["webhooks"][webhook_type] = "unhealthy"
                            health_status["overall"] = "degraded"
                            
                    except Exception as e:
                        health_status["webhooks"][webhook_type] = "unreachable"
                        health_status["overall"] = "unhealthy"
                        logger.error(f"Erro no health check do {webhook_type}: {e}")
                else:
                    health_status["webhooks"][webhook_type] = "inactive"
                    health_status["overall"] = "degraded"
            
        except ImportError:
            logger.warning("⚠️ Requests não disponível para health check")
            health_status["overall"] = "unknown"
        
        return health_status
    
    def monitor_webhooks(self, interval: int = 30):
        """Monitora webhooks em intervalos regulares"""
        logger.info(f"📊 Iniciando monitoramento com intervalo de {interval}s")
        
        while self.running:
            try:
                # Executa health check
                health = self.health_check()
                
                # Loga status
                if health["overall"] == "healthy":
                    logger.info("✅ Status geral: Saudável")
                elif health["overall"] == "degraded":
                    logger.warning("⚠️ Status geral: Degradado")
                else:
                    logger.error("❌ Status geral: Não saudável")
                
                # Loga status individual
                for webhook_type, status in health["webhooks"].items():
                    logger.info(f"🔧 {webhook_type}: {status}")
                
                # Aguarda próximo check
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(interval)
    
    def graceful_shutdown(self, signum, frame):
        """Desligamento gracioso do sistema"""
        logger.info(f"🛑 Recebido sinal {signum}, iniciando desligamento gracioso...")
        self.stop_all_webhooks()
        self.executor.shutdown(wait=True)
        logger.info("✅ Sistema desligado com sucesso")
        sys.exit(0)

def main():
    """Função principal"""
    try:
        # Cria diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)
        
        logger.info("🤖 Iniciando Sistema de Webhooks para Agendamento de Barbearia")
        
        # Cria e inicia o gerenciador de webhooks
        manager = WebhookManager()
        
        # Configura handlers de sinal para desligamento gracioso
        signal.signal(signal.SIGINT, manager.graceful_shutdown)
        signal.signal(signal.SIGTERM, manager.graceful_shutdown)
        
        # Inicia todos os webhooks
        if not manager.start_all_webhooks():
            logger.error("❌ Falha ao iniciar webhooks, encerrando...")
            sys.exit(1)
        
        # Inicia monitoramento em thread separada
        monitor_thread = threading.Thread(
            target=manager.monitor_webhooks,
            daemon=True
        )
        monitor_thread.start()
        
        logger.info("🎉 Sistema de webhooks iniciado com sucesso!")
        logger.info("📊 Monitoramento ativo")
        logger.info("🛑 Pressione Ctrl+C para parar")
        
        # Mantém o programa rodando
        while manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção do usuário detectada")
    except Exception as e:
        logger.error(f"❌ Erro fatal no sistema: {e}")
        sys.exit(1)
    finally:
        if 'manager' in locals():
            manager.stop_all_webhooks()

if __name__ == "__main__":
    main()