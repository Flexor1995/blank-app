"""
Gerenciador de WhatsApp para Comunicação com Clientes
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config.settings import WHATSAPP_CONFIG, MESSAGE_TEMPLATES
from agents.scheduling_logic import scheduler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppHandler:
    """Classe para gerenciar comunicação via WhatsApp"""
    
    def __init__(self):
        self.access_token = WHATSAPP_CONFIG["access_token"]
        self.phone_number_id = WHATSAPP_CONFIG["phone_number_id"]
        self.base_url = "https://graph.facebook.com/v17.0"
        
    def send_message(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Envia uma mensagem via WhatsApp
        
        Args:
            phone_number: Número do telefone (formato: 5511999999999)
            message: Mensagem a ser enviada
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem de resposta)
        """
        try:
            # Formata o número do telefone
            formatted_phone = self._format_phone_number(phone_number)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone_number}: {message[:50]}...")
                return True, "Mensagem enviada com sucesso"
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False, f"Erro ao enviar mensagem: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Exceção ao enviar mensagem: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    def send_template_message(self, phone_number: str, template_name: str, 
                            parameters: List[Dict] = None) -> Tuple[bool, str]:
        """
        Envia uma mensagem de template via WhatsApp
        
        Args:
            phone_number: Número do telefone
            template_name: Nome do template
            parameters: Parâmetros do template
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem de resposta)
        """
        try:
            formatted_phone = self._format_phone_number(phone_number)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "pt_BR"}
                }
            }
            
            if parameters:
                payload["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": parameters
                    }
                ]
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Template enviado para {phone_number}: {template_name}")
                return True, "Template enviado com sucesso"
            else:
                logger.error(f"Erro ao enviar template: {response.status_code} - {response.text}")
                return False, f"Erro ao enviar template: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Exceção ao enviar template: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    def send_quick_reply(self, phone_number: str, message: str, 
                         quick_replies: List[Dict]) -> Tuple[bool, str]:
        """
        Envia mensagem com botões de resposta rápida
        
        Args:
            phone_number: Número do telefone
            message: Mensagem principal
            quick_replies: Lista de botões de resposta rápida
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem de resposta)
        """
        try:
            formatted_phone = self._format_phone_number(phone_number)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {
                        "buttons": quick_replies
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Quick reply enviado para {phone_number}")
                return True, "Quick reply enviado com sucesso"
            else:
                logger.error(f"Erro ao enviar quick reply: {response.status_code} - {response.text}")
                return False, f"Erro ao enviar quick reply: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Exceção ao enviar quick reply: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    def send_list_message(self, phone_number: str, message: str, 
                         sections: List[Dict]) -> Tuple[bool, str]:
        """
        Envia mensagem com lista de opções
        
        Args:
            phone_number: Número do telefone
            message: Mensagem principal
            sections: Lista de seções com opções
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem de resposta)
        """
        try:
            formatted_phone = self._format_phone_number(phone_number)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": message},
                    "action": {
                        "button": "Ver opções",
                        "sections": sections
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Lista enviada para {phone_number}")
                return True, "Lista enviada com sucesso"
            else:
                logger.error(f"Erro ao enviar lista: {response.status_code} - {response.text}")
                return False, f"Erro ao enviar lista: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Exceção ao enviar lista: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Formata o número do telefone para o formato do WhatsApp"""
        # Remove caracteres especiais
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Adiciona código do país se não existir
        if not cleaned.startswith('55'):
            cleaned = '55' + cleaned
            
        return cleaned
    
    # Métodos específicos para agendamento
    
    def send_welcome_message(self, phone_number: str) -> Tuple[bool, str]:
        """Envia mensagem de boas-vindas"""
        message = MESSAGE_TEMPLATES["welcome"]
        return self.send_quick_reply(phone_number, message, [
            {
                "type": "reply",
                "reply": {
                    "id": "schedule",
                    "title": "📅 Fazer Agendamento"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "check",
                    "title": "🔍 Verificar Horários"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "cancel",
                    "title": "❌ Cancelar Agendamento"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "help",
                    "title": "❓ Ajuda"
                }
            }
        ])
    
    def send_availability_message(self, phone_number: str, date: str, 
                                available_slots: List) -> Tuple[bool, str]:
        """Envia mensagem com horários disponíveis"""
        if not available_slots:
            message = MESSAGE_TEMPLATES["no_availability"].format(date=date)
            return self.send_message(phone_number, message)
        
        # Formata os horários disponíveis
        time_list = []
        for i, slot in enumerate(available_slots[:10]):  # Máximo 10 horários
            time_str = slot.time.strftime("%H:%M")
            time_list.append(f"🕐 {time_str}")
        
        times_text = "\n".join(time_list)
        message = MESSAGE_TEMPLATES["time_suggestion"].format(
            date=date, 
            times=times_text
        )
        
        # Cria botões para os horários mais populares
        quick_replies = []
        for i, slot in enumerate(available_slots[:3]):  # Máximo 3 botões
            time_str = slot.time.strftime("%H:%M")
            quick_replies.append({
                "type": "reply",
                "reply": {
                    "id": f"time_{time_str.replace(':', '')}",
                    "title": time_str
                }
            })
        
        quick_replies.append({
            "type": "reply",
            "reply": {
                "id": "other_time",
                "title": "🕐 Outro horário"
            }
        })
        
        return self.send_quick_reply(phone_number, message, quick_replies)
    
    def send_confirmation_message(self, phone_number: str, date: str, 
                                time: str) -> Tuple[bool, str]:
        """Envia mensagem de confirmação de agendamento"""
        message = MESSAGE_TEMPLATES["appointment_confirmed"].format(
            date=date, 
            time=time
        )
        
        return self.send_quick_reply(phone_number, message, [
            {
                "type": "reply",
                "reply": {
                    "id": "confirm",
                    "title": "✅ Confirmar"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "reschedule",
                    "title": "🔄 Remarcar"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "cancel",
                    "title": "❌ Cancelar"
                }
            }
        ])
    
    def send_reminder_message(self, phone_number: str, date: str, 
                            time: str) -> Tuple[bool, str]:
        """Envia mensagem de lembrete"""
        message = MESSAGE_TEMPLATES["reminder"].format(time=time)
        
        return self.send_quick_reply(phone_number, message, [
            {
                "type": "reply",
                "reply": {
                    "id": "confirm_attendance",
                    "title": "✅ Sim, vou comparecer"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "cancel_appointment",
                    "title": "❌ Não, preciso cancelar"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "reschedule_appointment",
                    "title": "🔄 Quero remarcar"
                }
            }
        ])
    
    def send_cancellation_confirmation(self, phone_number: str, date: str, 
                                     time: str) -> Tuple[bool, str]:
        """Envia confirmação de cancelamento"""
        message = MESSAGE_TEMPLATES["appointment_cancelled"].format(
            date=date, 
            time=time
        )
        
        return self.send_quick_reply(phone_number, message, [
            {
                "type": "reply",
                "reply": {
                    "id": "reschedule",
                    "title": "🔄 Fazer novo agendamento"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "help",
                    "title": "❓ Ajuda"
                }
            }
        ])
    
    def send_reschedule_confirmation(self, phone_number: str, old_date: str, 
                                   old_time: str, new_date: str, 
                                   new_time: str) -> Tuple[bool, str]:
        """Envia confirmação de remarcação"""
        message = MESSAGE_TEMPLATES["appointment_rescheduled"].format(
            date=new_date, 
            time=new_time
        )
        
        return self.send_quick_reply(phone_number, message, [
            {
                "type": "reply",
                "reply": {
                    "id": "confirm",
                    "title": "✅ Confirmar"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "help",
                    "title": "❓ Ajuda"
                }
            }
        ])
    
    def send_help_message(self, phone_number: str) -> Tuple[bool, str]:
        """Envia mensagem de ajuda"""
        message = MESSAGE_TEMPLATES["help"]
        return self.send_message(phone_number, message)

# Instância global do handler
whatsapp_handler = WhatsAppHandler()