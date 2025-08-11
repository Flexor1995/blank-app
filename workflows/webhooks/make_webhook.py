#!/usr/bin/env python3
"""
Webhook para integração com Make
Recebe mensagens processadas e executa ações de agendamento
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from config.settings import MAKE_CONFIG, WHATSAPP_CONFIG
from agents.barber_agent import barber_agent
from agents.whatsapp_handler import whatsapp_handler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MakeWebhook:
    """Gerencia webhooks do Make"""
    
    def __init__(self):
        self.make_config = MAKE_CONFIG
        self.whatsapp_config = WHATSAPP_CONFIG
        self.barber_agent = barber_agent
        
    def verify_webhook(self, token: str) -> bool:
        """Verifica token do webhook do Make"""
        return token == self.make_config.get("webhook_token", "default_token")
    
    def process_make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição recebida do Make"""
        try:
            # Extrai dados da mensagem
            message = request_data.get("message", {})
            
            if not message:
                raise ValueError("Dados da mensagem não encontrados")
            
            # Processa via agente
            result = self.barber_agent.process_message(
                message=message.get("text", ""),
                phone_number=message.get("from", ""),
                conversation_id=message.get("conversation_id", "")
            )
            
            logger.info(f"Mensagem processada pelo agente: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição do Make: {e}")
            raise
    
    def send_whatsapp_response(self, phone_number: str, message: str, quick_replies: Optional[list] = None) -> bool:
        """Envia resposta via WhatsApp"""
        try:
            if quick_replies:
                success = whatsapp_handler.send_quick_reply(phone_number, message, quick_replies)
            else:
                success = whatsapp_handler.send_message(phone_number, message)
            
            if success:
                logger.info(f"Resposta enviada para {phone_number}")
                return True
            else:
                logger.error(f"Falha ao enviar resposta para {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar resposta WhatsApp: {e}")
            return False
    
    def handle_scheduling_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de agendamento"""
        try:
            phone_number = data.get("phone_number")
            date = data.get("date")
            time = data.get("time")
            client_name = data.get("client_name")
            
            if not all([phone_number, date, time, client_name]):
                return {
                    "success": False,
                    "error": "Dados incompletos para agendamento"
                }
            
            # Cria agendamento via agente
            appointment = self.barber_agent.scheduler.create_appointment(
                client_name=client_name,
                client_phone=phone_number,
                date=date,
                time=time,
                service="Corte de Cabelo"
            )
            
            if appointment:
                # Envia confirmação
                confirmation_msg = f"✅ Agendamento confirmado!\n\n📅 Data: {date}\n🕐 Horário: {time}\n👤 Nome: {client_name}\n\n⏰ Lembrete: Chegue 10 minutos antes do horário."
                
                self.send_whatsapp_response(
                    phone_number,
                    confirmation_msg,
                    [
                        {"id": "confirm", "title": "✅ Confirmado"},
                        {"id": "reschedule", "title": "🔄 Remarcar"},
                        {"id": "cancel", "title": "❌ Cancelar"}
                    ]
                )
                
                return {
                    "success": True,
                    "appointment_id": appointment.id,
                    "message": "Agendamento criado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Falha ao criar agendamento"
                }
                
        except Exception as e:
            logger.error(f"Erro no agendamento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_availability_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa verificação de disponibilidade"""
        try:
            date = data.get("date")
            phone_number = data.get("phone_number")
            
            if not date:
                return {
                    "success": False,
                    "error": "Data não informada"
                }
            
            # Busca horários disponíveis
            available_slots = self.barber_agent.scheduler.get_available_slots(date)
            
            if available_slots:
                # Formata horários disponíveis
                time_list = "\n".join([f"• {slot.time}" for slot in available_slots[:10]])
                
                availability_msg = f"🕐 Horários disponíveis para {date}:\n\n{time_list}"
                
                if len(available_slots) > 10:
                    availability_msg += f"\n\n... e mais {len(available_slots) - 10} horários disponíveis."
                
                # Adiciona botões de ação
                availability_msg += "\n\nO que gostaria de fazer?"
                
                self.send_whatsapp_response(
                    phone_number,
                    availability_msg,
                    [
                        {"id": "schedule", "title": "📅 Fazer Agendamento"},
                        {"id": "check_other_date", "title": "🔍 Ver Outra Data"},
                        {"id": "help", "title": "❓ Ajuda"}
                    ]
                )
                
                return {
                    "success": True,
                    "available_slots": len(available_slots),
                    "message": "Disponibilidade verificada com sucesso"
                }
            else:
                # Nenhum horário disponível
                no_availability_msg = f"😔 Não há horários disponíveis para {date}.\n\nGostaria de ver outras datas?"
                
                self.send_whatsapp_response(
                    phone_number,
                    no_availability_msg,
                    [
                        {"id": "check_other_date", "title": "🔍 Ver Outra Data"},
                        {"id": "schedule_later", "title": "📅 Agendar Mais Tarde"},
                        {"id": "help", "title": "❓ Ajuda"}
                    ]
                )
                
                return {
                    "success": True,
                    "available_slots": 0,
                    "message": "Nenhum horário disponível"
                }
                
        except Exception as e:
            logger.error(f"Erro na verificação de disponibilidade: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_cancellation_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de cancelamento"""
        try:
            phone_number = data.get("phone_number")
            appointment_id = data.get("appointment_id")
            
            if not phone_number:
                return {
                    "success": False,
                    "error": "Número de telefone não informado"
                }
            
            if appointment_id:
                # Cancela agendamento específico
                success = self.barber_agent.scheduler.cancel_appointment(appointment_id)
                
                if success:
                    cancellation_msg = "❌ Agendamento cancelado com sucesso!\n\nGostaria de fazer um novo agendamento?"
                    
                    self.send_whatsapp_response(
                        phone_number,
                        cancellation_msg,
                        [
                            {"id": "new_appointment", "title": "📅 Novo Agendamento"},
                            {"id": "help", "title": "❓ Ajuda"}
                        ]
                    )
                    
                    return {
                        "success": True,
                        "message": "Agendamento cancelado com sucesso"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Falha ao cancelar agendamento"
                    }
            else:
                # Busca agendamentos do cliente
                appointments = self.barber_agent.scheduler.get_appointment_by_client(phone_number)
                
                if appointments:
                    # Lista agendamentos para cancelamento
                    appointments_list = "📋 Seus agendamentos:\n\n"
                    for i, apt in enumerate(appointments, 1):
                        appointments_list += f"{i}. {apt.date} às {apt.time}\n"
                    
                    appointments_list += "\nQual você gostaria de cancelar? Responda com o número."
                    
                    self.send_whatsapp_response(phone_number, appointments_list)
                    
                    return {
                        "success": True,
                        "appointments_count": len(appointments),
                        "message": "Agendamentos listados para cancelamento"
                    }
                else:
                    no_appointments_msg = "😔 Não encontrei agendamentos para este número.\n\nPode verificar se o número está correto?"
                    
                    self.send_whatsapp_response(
                        phone_number,
                        no_appointments_msg,
                        [
                            {"id": "check_number", "title": "🔍 Verificar Número"},
                            {"id": "help", "title": "❓ Ajuda"}
                        ]
                    )
                    
                    return {
                        "success": True,
                        "appointments_count": 0,
                        "message": "Nenhum agendamento encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"Erro no cancelamento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_reschedule_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de remarcação"""
        try:
            phone_number = data.get("phone_number")
            appointment_id = data.get("appointment_id")
            new_date = data.get("new_date")
            new_time = data.get("new_time")
            
            if not phone_number:
                return {
                    "success": False,
                    "error": "Número de telefone não informado"
                }
            
            if appointment_id and new_date and new_time:
                # Executa remarcação
                success = self.barber_agent.scheduler.reschedule_appointment(
                    appointment_id, new_date, new_time
                )
                
                if success:
                    reschedule_msg = f"🔄 Agendamento remarcado com sucesso!\n\n📅 Nova data: {new_date}\n🕐 Novo horário: {new_time}\n\n⏰ Lembrete: Chegue 10 minutos antes do horário."
                    
                    self.send_whatsapp_response(
                        phone_number,
                        reschedule_msg,
                        [
                            {"id": "confirm", "title": "✅ Confirmado"},
                            {"id": "help", "title": "❓ Ajuda"}
                        ]
                    )
                    
                    return {
                        "success": True,
                        "message": "Agendamento remarcado com sucesso"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Falha ao remarcar agendamento"
                    }
            else:
                # Busca agendamentos para remarcação
                appointments = self.barber_agent.scheduler.get_appointment_by_client(phone_number)
                
                if appointments:
                    # Lista agendamentos para remarcação
                    appointments_list = "📋 Seus agendamentos:\n\n"
                    for i, apt in enumerate(appointments, 1):
                        appointments_list += f"{i}. {apt.date} às {apt.time}\n"
                    
                    appointments_list += "\nQual você gostaria de remarcar? Responda com o número."
                    
                    self.send_whatsapp_response(phone_number, appointments_list)
                    
                    return {
                        "success": True,
                        "appointments_count": len(appointments),
                        "message": "Agendamentos listados para remarcação"
                    }
                else:
                    no_appointments_msg = "😔 Não encontrei agendamentos para este número.\n\nPode verificar se o número está correto?"
                    
                    self.send_whatsapp_response(
                        phone_number,
                        no_appointments_msg,
                        [
                            {"id": "check_number", "title": "🔍 Verificar Número"},
                            {"id": "help", "title": "❓ Ajuda"}
                        ]
                    )
                    
                    return {
                        "success": True,
                        "appointments_count": 0,
                        "message": "Nenhum agendamento encontrado"
                    }
                    
        except Exception as e:
            logger.error(f"Erro na remarcação: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Instância global
make_webhook = MakeWebhook()

@app.route('/webhook/make', methods=['POST'])
def make_webhook():
    """Endpoint principal do webhook do Make"""
    
    try:
        # Verifica token de autenticação
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token de autenticação inválido"}), 401
        
        token = auth_header.split(' ')[1]
        if not make_webhook.verify_webhook(token):
            return jsonify({"error": "Token inválido"}), 401
        
        # Recebe dados do Make
        data = request.get_json()
        logger.info(f"Webhook do Make recebido: {data}")
        
        # Identifica tipo de ação
        action_type = data.get("action_type", "process_message")
        
        if action_type == "schedule_appointment":
            result = make_webhook.handle_scheduling_request(data)
        elif action_type == "check_availability":
            result = make_webhook.handle_availability_check(data)
        elif action_type == "cancel_appointment":
            result = make_webhook.handle_cancellation_request(data)
        elif action_type == "reschedule_appointment":
            result = make_webhook.handle_reschedule_request(data)
        else:
            # Processa mensagem padrão
            result = make_webhook.process_make_request(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no webhook do Make: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/make/status', methods=['GET'])
def make_webhook_status():
    """Endpoint para verificar status do webhook do Make"""
    return jsonify({
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "make",
        "endpoints": {
            "webhook": "/webhook/make",
            "status": "/webhook/make/status"
        },
        "supported_actions": [
            "schedule_appointment",
            "check_availability", 
            "cancel_appointment",
            "reschedule_appointment",
            "process_message"
        ]
    })

@app.route('/webhook/make/test', methods=['POST'])
def test_make_webhook():
    """Endpoint para testar o webhook do Make"""
    try:
        data = request.get_json()
        test_type = data.get("test_type", "message")
        
        if test_type == "schedule":
            result = make_webhook.handle_scheduling_request({
                "phone_number": "5511999999999",
                "date": "2024-01-15",
                "time": "14:00",
                "client_name": "João Silva"
            })
        elif test_type == "availability":
            result = make_webhook.handle_availability_check({
                "phone_number": "5511999999999",
                "date": "2024-01-15"
            })
        else:
            result = make_webhook.process_make_request({
                "message": {
                    "text": "Olá, gostaria de agendar um horário",
                    "from": "5511999999999",
                    "conversation_id": "test_123"
                }
            })
        
        return jsonify({
            "status": "success",
            "test_type": test_type,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)