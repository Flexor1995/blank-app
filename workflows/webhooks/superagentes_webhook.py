#!/usr/bin/env python3
"""
Webhook para integração com SuperAgentes
Recebe mensagens do WhatsApp via SuperAgentes e encaminha para o Make
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from config.settings import SUPERAGENTES_CONFIG, MAKE_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SuperAgentesWebhook:
    """Gerencia webhooks do SuperAgentes"""
    
    def __init__(self):
        self.superagentes_config = SUPERAGENTES_CONFIG
        self.make_config = MAKE_CONFIG
        
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verifica webhook do SuperAgentes"""
        if mode == "subscribe" and token == self.superagentes_config["verify_token"]:
            logger.info("Webhook verificado com sucesso")
            return challenge
        return None
    
    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem recebida do SuperAgentes"""
        try:
            # Extrai informações da mensagem
            message = {
                "id": message_data.get("id"),
                "from": message_data.get("from"),
                "timestamp": message_data.get("timestamp"),
                "type": message_data.get("type"),
                "text": message_data.get("text", {}).get("body", ""),
                "conversation_id": message_data.get("conversation", {}).get("id"),
                "source": "superagentes"
            }
            
            # Validações básicas
            if not message["from"] or not message["text"]:
                raise ValueError("Dados da mensagem incompletos")
            
            logger.info(f"Mensagem processada: {message['id']} de {message['from']}")
            return message
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            raise
    
    def forward_to_make(self, message: Dict[str, Any]) -> bool:
        """Encaminha mensagem para o Make"""
        try:
            # Prepara payload para o Make
            make_payload = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "superagentes_webhook"
            }
            
            # Envia para webhook do Make
            response = requests.post(
                self.make_config["webhook_url"],
                json=make_payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.make_config['api_key']}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Mensagem encaminhada para Make: {message['id']}")
                return True
            else:
                logger.error(f"Erro ao enviar para Make: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao encaminhar para Make: {e}")
            return False
    
    def send_response(self, phone_number: str, message: str) -> bool:
        """Envia resposta via SuperAgentes"""
        try:
            response_data = {
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(
                f"{self.superagentes_config['base_url']}/messages",
                json=response_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.superagentes_config['api_key']}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Resposta enviada para {phone_number}")
                return True
            else:
                logger.error(f"Erro ao enviar resposta: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar resposta: {e}")
            return False

# Instância global
webhook_handler = SuperAgentesWebhook()

@app.route('/webhook/superagentes', methods=['GET', 'POST'])
def superagentes_webhook():
    """Endpoint principal do webhook do SuperAgentes"""
    
    if request.method == 'GET':
        # Verificação do webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token and challenge:
            result = webhook_handler.verify_webhook(mode, token, challenge)
            if result:
                return result
            else:
                return "Forbidden", 403
        
        return "Bad Request", 400
    
    elif request.method == 'POST':
        try:
            # Recebe dados do webhook
            data = request.get_json()
            logger.info(f"Webhook recebido: {data}")
            
            # Verifica se é uma mensagem válida
            if 'entry' not in data or 'changes' not in data['entry'][0]:
                return jsonify({"status": "ignored", "reason": "Formato inválido"}), 200
            
            # Processa cada mudança
            for entry in data['entry']:
                for change in entry['changes']:
                    if change.get('value', {}).get('messages'):
                        for message in change['value']['messages']:
                            # Processa mensagem
                            processed_message = webhook_handler.process_message(message)
                            
                            # Encaminha para Make
                            if webhook_handler.forward_to_make(processed_message):
                                # Envia confirmação de recebimento
                                webhook_handler.send_response(
                                    processed_message['from'],
                                    "✅ Mensagem recebida! Estou processando sua solicitação..."
                                )
                            else:
                                logger.error("Falha ao encaminhar para Make")
                                # Envia mensagem de erro
                                webhook_handler.send_response(
                                    processed_message['from'],
                                    "❌ Desculpe, estou com dificuldades técnicas. Tente novamente em alguns instantes."
                                )
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logger.error(f"Erro no webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook/superagentes/status', methods=['GET'])
def webhook_status():
    """Endpoint para verificar status do webhook"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "superagentes",
        "endpoints": {
            "webhook": "/webhook/superagentes",
            "status": "/webhook/superagentes/status"
        }
    })

@app.route('/webhook/superagentes/test', methods=['POST'])
def test_webhook():
    """Endpoint para testar o webhook"""
    try:
        data = request.get_json()
        test_message = {
            "id": "test_123",
            "from": data.get("phone_number", "5511999999999"),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "text",
            "text": data.get("message", "Teste do webhook"),
            "conversation_id": "test_conversation",
            "source": "test"
        }
        
        # Testa encaminhamento para Make
        success = webhook_handler.forward_to_make(test_message)
        
        return jsonify({
            "status": "success" if success else "error",
            "message": "Teste executado com sucesso" if success else "Falha no teste",
            "test_data": test_message
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)