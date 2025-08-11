"""
Agente Principal de Agendamento para Barbearia
Integração com SuperAgentes e Make
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, time, timedelta
from dataclasses import asdict

from config.settings import SUPERAGENTES_CONFIG, MESSAGE_TEMPLATES
from config.prompts import (
    SYSTEM_PROMPT, APPOINTMENT_CREATION_PROMPT, AVAILABILITY_CHECK_PROMPT,
    APPOINTMENT_CANCELLATION_PROMPT, APPOINTMENT_RESCHEDULING_PROMPT,
    CONFIRMATION_PROMPT, PERSONALITY_PROMPT, ERROR_HANDLING_PROMPT, CLOSING_PROMPT
)
from agents.scheduling_logic import scheduler, Appointment
from agents.whatsapp_handler import whatsapp_handler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BarberAgent:
    """
    Agente principal para gerenciar agendamentos de barbearia
    Integra com SuperAgentes e Make para automação completa
    """
    
    def __init__(self):
        self.scheduler = scheduler
        self.whatsapp = whatsapp_handler
        self.conversation_context = {}
        self.pending_appointments = {}
        
        # Estados da conversa
        self.conversation_states = {
            'idle': self._handle_idle_state,
            'waiting_for_date': self._handle_date_input,
            'waiting_for_time': self._handle_time_input,
            'waiting_for_name': self._handle_name_input,
            'waiting_for_phone': self._handle_phone_input,
            'waiting_for_confirmation': self._handle_confirmation_input,
            'waiting_for_cancellation_confirmation': self._handle_cancellation_confirmation,
            'waiting_for_reschedule_date': self._handle_reschedule_date_input,
            'waiting_for_reschedule_time': self._handle_reschedule_time_input
        }
    
    def process_message(self, message: str, phone_number: str, 
                       conversation_id: str = None) -> Tuple[str, Dict]:
        """
        Processa mensagem recebida e retorna resposta
        
        Args:
            message: Mensagem recebida
            phone_number: Número do telefone do cliente
            conversation_id: ID da conversa
            
        Returns:
            Tuple[str, Dict]: (resposta, contexto atualizado)
        """
        try:
            # Inicializa contexto se necessário
            if conversation_id not in self.conversation_context:
                self.conversation_context[conversation_id] = {
                    'state': 'idle',
                    'phone_number': phone_number,
                    'current_appointment': None,
                    'pending_data': {},
                    'last_interaction': datetime.now()
                }
            
            context = self.conversation_context[conversation_id]
            context['last_interaction'] = datetime.now()
            
            # Processa a mensagem baseado no estado atual
            current_state = context['state']
            
            if current_state in self.conversation_states:
                response, updated_context = self.conversation_states[current_state](
                    message, context, conversation_id
                )
            else:
                response, updated_context = self._handle_unknown_state(message, context)
            
            # Atualiza o contexto
            self.conversation_context[conversation_id].update(updated_context)
            
            # Envia resposta via WhatsApp
            self.whatsapp.send_message(phone_number, response)
            
            return response, updated_context
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            error_response = "Desculpe, ocorreu um erro inesperado. Pode tentar novamente?"
            self.whatsapp.send_message(phone_number, error_response)
            return error_response, {}
    
    def _handle_idle_state(self, message: str, context: Dict, 
                          conversation_id: str) -> Tuple[str, Dict]:
        """Processa mensagem no estado ocioso"""
        message_lower = message.lower()
        
        # Identifica intenção do usuário
        if any(word in message_lower for word in ['agendar', 'marcar', 'horário', 'corte']):
            context['state'] = 'waiting_for_date'
            return "📅 Perfeito! Para qual data você gostaria de agendar?", context
        
        elif any(word in message_lower for word in ['verificar', 'disponível', 'horários', 'livre']):
            context['state'] = 'waiting_for_date'
            context['intent'] = 'check_availability'
            return "📅 Claro! Para qual data você gostaria de verificar a disponibilidade?", context
        
        elif any(word in message_lower for word in ['cancelar', 'cancelamento']):
            context['state'] = 'waiting_for_cancellation_confirmation'
            return "❌ Entendo que quer cancelar. Qual é o seu número de telefone para eu localizar o agendamento?", context
        
        elif any(word in message_lower for word in ['remarcar', 'mudar', 'alterar']):
            context['state'] = 'waiting_for_cancellation_confirmation'
            context['intent'] = 'reschedule'
            return "🔄 Entendo que quer remarcar. Qual é o seu número de telefone para eu localizar o agendamento?", context
        
        elif any(word in message_lower for word in ['ajuda', 'help', 'o que pode fazer']):
            return MESSAGE_TEMPLATES["help"], context
        
        else:
            # Mensagem não reconhecida, envia menu principal
            return self._send_main_menu(context), context
    
    def _handle_date_input(self, message: str, context: Dict, 
                          conversation_id: str) -> Tuple[str, Dict]:
        """Processa entrada de data"""
        try:
            # Tenta extrair data da mensagem
            parsed_date = self._parse_date_input(message)
            
            if not parsed_date:
                return "📅 Não consegui entender a data. Pode informar no formato DD/MM/AAAA ou 'amanhã', 'hoje'?", context
            
            context['pending_data']['date'] = parsed_date
            
            # Verifica se é para agendamento ou verificação
            if context.get('intent') == 'check_availability':
                return self._handle_availability_check(parsed_date, context)
            else:
                # É para agendamento
                context['state'] = 'waiting_for_time'
                available_slots = self.scheduler.get_available_slots(parsed_date)
                
                if not available_slots:
                    return "😔 Não há horários disponíveis para esta data. Gostaria de ver outras datas?", context
                
                # Envia horários disponíveis
                return self._format_available_times(available_slots, parsed_date), context
                
        except Exception as e:
            logger.error(f"Erro ao processar data: {str(e)}")
            return "📅 Desculpe, tive um problema ao processar a data. Pode tentar novamente?", context
    
    def _handle_time_input(self, message: str, context: Dict, 
                          conversation_id: str) -> Tuple[str, Dict]:
        """Processa entrada de horário"""
        try:
            # Tenta extrair horário da mensagem
            parsed_time = self._parse_time_input(message)
            
            if not parsed_time:
                return "🕐 Não consegui entender o horário. Pode informar no formato HH:MM (ex: 14:30)?", context
            
            context['pending_data']['time'] = parsed_time
            
            # Verifica se o horário ainda está disponível
            date_obj = context['pending_data']['date']
            if not self.scheduler.is_time_slot_available(date_obj, parsed_time):
                return "😔 Este horário não está mais disponível. Gostaria de ver outros horários?", context
            
            context['state'] = 'waiting_for_name'
            return "👤 Perfeito! Qual é o seu nome completo?", context
            
        except Exception as e:
            logger.error(f"Erro ao processar horário: {str(e)}")
            return "🕐 Desculpe, tive um problema ao processar o horário. Pode tentar novamente?", context
    
    def _handle_name_input(self, message: str, context: Dict, 
                          conversation_id: str) -> Tuple[str, Dict]:
        """Processa entrada do nome"""
        if len(message.strip()) < 2:
            return "👤 O nome deve ter pelo menos 2 caracteres. Pode informar novamente?", context
        
        context['pending_data']['name'] = message.strip()
        context['state'] = 'waiting_for_phone'
        return "📱 Ótimo! Agora preciso do seu número de telefone (com DDD).", context
    
    def _handle_phone_input(self, message: str, context: Dict, 
                           conversation_id: str) -> Tuple[str, Dict]:
        """Processa entrada do telefone"""
        # Limpa o número do telefone
        phone = ''.join(filter(str.isdigit, message))
        
        if len(phone) < 10:
            return "📱 O número deve ter pelo menos 10 dígitos (com DDD). Pode informar novamente?", context
        
        context['pending_data']['phone'] = phone
        context['state'] = 'waiting_for_confirmation'
        
        # Monta resumo para confirmação
        date_str = context['pending_data']['date'].strftime("%d/%m/%Y")
        time_str = context['pending_data']['time'].strftime("%H:%M")
        name = context['pending_data']['name']
        
        confirmation_text = f"""
✅ Confirma os dados do agendamento?

📅 Data: {date_str}
🕐 Horário: {time_str}
👤 Nome: {name}
📱 Telefone: {phone}

Responda com:
✅ - Sim, confirmar
❌ - Não, cancelar
🔄 - Quero alterar
        """.strip()
        
        return confirmation_text, context
    
    def _handle_confirmation_input(self, message: str, context: Dict, 
                                 conversation_id: str) -> Tuple[str, Dict]:
        """Processa confirmação do agendamento"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['sim', 'confirmar', '✅', 'confirmo']):
            # Cria o agendamento
            success, message_text, appointment_id = self.scheduler.create_appointment(
                client_name=context['pending_data']['name'],
                client_phone=context['pending_data']['phone'],
                date=context['pending_data']['date'],
                time=context['pending_data']['time']
            )
            
            if success:
                # Limpa dados pendentes e volta ao estado ocioso
                context['state'] = 'idle'
                context['pending_data'] = {}
                context['current_appointment'] = appointment_id
                
                # Envia confirmação via WhatsApp
                date_str = context['pending_data']['date'].strftime("%d/%m/%Y")
                time_str = context['pending_data']['time'].strftime("%H:%M")
                
                self.whatsapp.send_confirmation_message(
                    context['phone_number'],
                    date_str,
                    time_str
                )
                
                return "🎉 Agendamento realizado com sucesso! Enviei uma confirmação no WhatsApp.", context
            else:
                return f"❌ {message_text}", context
        
        elif any(word in message_lower for word in ['não', 'cancelar', '❌']):
            context['state'] = 'idle'
            context['pending_data'] = {}
            return "😔 Agendamento cancelado. Se precisar de mais alguma coisa, é só chamar!", context
        
        elif any(word in message_lower for word in ['alterar', '🔄']):
            context['state'] = 'waiting_for_date'
            context['pending_data'] = {}
            return "🔄 Sem problemas! Vamos começar novamente. Para qual data você gostaria de agendar?", context
        
        else:
            return "🤔 Não entendi sua resposta. Pode responder com 'sim', 'não' ou 'alterar'?", context
    
    def _handle_cancellation_confirmation(self, message: str, context: Dict, 
                                        conversation_id: str) -> Tuple[str, Dict]:
        """Processa confirmação de cancelamento/remarcação"""
        # Extrai número do telefone da mensagem
        phone = ''.join(filter(str.isdigit, message))
        
        if len(phone) < 10:
            return "📱 Preciso do seu número de telefone para localizar o agendamento. Pode informar novamente?", context
        
        # Busca agendamentos do cliente
        client_appointments = self.scheduler.get_appointment_by_client(phone)
        
        if not client_appointments:
            return "😔 Não encontrei agendamentos para este número. Pode verificar se o número está correto?", context
        
        # Se há apenas um agendamento, usa ele diretamente
        if len(client_appointments) == 1:
            appointment = client_appointments[0]
            context['current_appointment'] = appointment.id
            
            if context.get('intent') == 'reschedule':
                context['state'] = 'waiting_for_reschedule_date'
                return "🔄 Encontrei seu agendamento! Para qual nova data você gostaria de remarcar?", context
            else:
                # É cancelamento
                context['state'] = 'waiting_for_cancellation_confirmation'
                date_str = appointment.date.strftime("%d/%m/%Y")
                time_str = appointment.time.strftime("%H:%M")
                
                return f"❌ Encontrei seu agendamento para {date_str} às {time_str}. Confirma o cancelamento?", context
        
        # Se há múltiplos agendamentos, pede para escolher
        context['pending_data']['phone'] = phone
        context['state'] = 'waiting_for_appointment_selection'
        
        appointments_text = "📋 Encontrei os seguintes agendamentos:\n\n"
        for i, apt in enumerate(client_appointments, 1):
            date_str = apt.date.strftime("%d/%m/%Y")
            time_str = apt.time.strftime("%H:%M")
            appointments_text += f"{i}. {date_str} às {time_str}\n"
        
        appointments_text += "\nQual você gostaria de cancelar/remarcar? Responda com o número."
        
        return appointments_text, context
    
    def _handle_reschedule_date_input(self, message: str, context: Dict, 
                                    conversation_id: str) -> Tuple[str, Dict]:
        """Processa nova data para remarcação"""
        parsed_date = self._parse_date_input(message)
        
        if not parsed_date:
            return "📅 Não consegui entender a data. Pode informar no formato DD/MM/AAAA?", context
        
        context['pending_data']['new_date'] = parsed_date
        context['state'] = 'waiting_for_reschedule_time'
        
        # Verifica disponibilidade para a nova data
        available_slots = self.scheduler.get_available_slots(parsed_date)
        
        if not available_slots:
            return "😔 Não há horários disponíveis para esta data. Gostaria de ver outras datas?", context
        
        return self._format_available_times(available_slots, parsed_date, "remarcação"), context
    
    def _handle_reschedule_time_input(self, message: str, context: Dict, 
                                    conversation_id: str) -> Tuple[str, Dict]:
        """Processa novo horário para remarcação"""
        parsed_time = self._parse_time_input(message)
        
        if not parsed_time:
            return "🕐 Não consegui entender o horário. Pode informar no formato HH:MM?", context
        
        # Executa a remarcação
        appointment_id = context['current_appointment']
        new_date = context['pending_data']['new_date']
        
        success, message_text = self.scheduler.reschedule_appointment(
            appointment_id, new_date, parsed_time
        )
        
        if success:
            context['state'] = 'idle'
            context['pending_data'] = {}
            context['current_appointment'] = None
            
            # Envia confirmação via WhatsApp
            old_appointment = self.scheduler.appointments[appointment_id]
            old_date_str = old_appointment.date.strftime("%d/%m/%Y")
            old_time_str = old_appointment.time.strftime("%H:%M")
            new_date_str = new_date.strftime("%d/%m/%Y")
            new_time_str = parsed_time.strftime("%H:%M")
            
            self.whatsapp.send_reschedule_confirmation(
                context['phone_number'],
                old_date_str,
                old_time_str,
                new_date_str,
                new_time_str
            )
            
            return "🔄 Agendamento remarcado com sucesso! Enviei uma confirmação no WhatsApp.", context
        else:
            return f"❌ {message_text}", context
    
    def _handle_availability_check(self, check_date: date, context: Dict) -> Tuple[str, Dict]:
        """Processa verificação de disponibilidade"""
        available_slots = self.scheduler.get_available_slots(check_date)
        
        if not available_slots:
            context['state'] = 'idle'
            return "😔 Não há horários disponíveis para esta data. Gostaria de ver outras datas?", context
        
        # Formata horários disponíveis
        response = self._format_available_times(available_slots, check_date)
        
        # Volta ao estado ocioso
        context['state'] = 'idle'
        context['intent'] = None
        
        return response, context
    
    def _format_available_times(self, available_slots: List, date_obj: date, 
                               context: str = "agendamento") -> str:
        """Formata horários disponíveis para exibição"""
        date_str = date_obj.strftime("%d/%m/%Y")
        
        if context == "remarcação":
            response = f"🕐 Horários disponíveis para {date_str}:\n\n"
        else:
            response = f"🕐 Horários disponíveis para {date_str}:\n\n"
        
        # Mostra até 10 horários
        for i, slot in enumerate(available_slots[:10], 1):
            time_str = slot.time.strftime("%H:%M")
            response += f"{i}. {time_str}\n"
        
        if len(available_slots) > 10:
            response += f"\n... e mais {len(available_slots) - 10} horários disponíveis."
        
        if context == "agendamento":
            response += "\n\nEscolha um horário ou digite o horário desejado (ex: 14:30)."
        elif context == "remarcação":
            response += "\n\nEscolha um horário para remarcar ou digite o horário desejado."
        
        return response
    
    def _handle_unknown_state(self, message: str, context: Dict) -> Tuple[str, Dict]:
        """Processa mensagem em estado desconhecido"""
        logger.warning(f"Estado desconhecido: {context.get('state')}")
        context['state'] = 'idle'
        return "Desculpe, tive um problema técnico. Como posso ajudá-lo?", context
    
    def _send_main_menu(self, context: Dict) -> str:
        """Envia menu principal"""
        return MESSAGE_TEMPLATES["welcome"]
    
    def _parse_date_input(self, message: str) -> Optional[date]:
        """Extrai data da mensagem do usuário"""
        message_lower = message.lower().strip()
        
        # Casos especiais
        if message_lower in ['hoje', 'agora']:
            return date.today()
        elif message_lower == 'amanhã':
            return date.today() + timedelta(days=1)
        elif message_lower == 'depois de amanhã':
            return date.today() + timedelta(days=2)
        
        # Padrões de data
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/AAAA
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-AAAA
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.AAAA
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                day, month, year = map(int, match.groups())
                try:
                    return date(year, month, day)
                except ValueError:
                    continue
        
        return None
    
    def _parse_time_input(self, message: str) -> Optional[time]:
        """Extrai horário da mensagem do usuário"""
        message_clean = message.strip()
        
        # Padrões de horário
        patterns = [
            r'(\d{1,2}):(\d{2})',  # HH:MM
            r'(\d{1,2})h(\d{2})?',  # HHh ou HHhMM
            r'(\d{1,2})\.(\d{2})',  # HH.MM
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_clean)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                
                # Validações básicas
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return time(hour, minute)
        
        return None
    
    def send_reminder_notifications(self):
        """Envia lembretes para agendamentos próximos"""
        try:
            # Busca agendamentos nas próximas 24 horas
            upcoming = self.scheduler.get_upcoming_appointments(24)
            
            for appointment in upcoming:
                # Verifica se deve enviar lembrete
                appointment_datetime = datetime.combine(appointment.date, appointment.time)
                now = datetime.now()
                
                # Envia lembrete 24h antes
                if (appointment_datetime - now).total_seconds() <= 24 * 3600:
                    date_str = appointment.date.strftime("%d/%m/%Y")
                    time_str = appointment.time.strftime("%H:%M")
                    
                    self.whatsapp.send_reminder_message(
                        appointment.client_phone,
                        date_str,
                        time_str
                    )
                    
                    logger.info(f"Lembrete enviado para {appointment.client_name} - {date_str} {time_str}")
        
        except Exception as e:
            logger.error(f"Erro ao enviar lembretes: {str(e)}")
    
    def get_conversation_stats(self) -> Dict:
        """Retorna estatísticas das conversas"""
        total_conversations = len(self.conversation_context)
        active_conversations = len([
            conv for conv in self.conversation_context.values()
            if conv['state'] != 'idle'
        ])
        
        return {
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'idle_conversations': total_conversations - active_conversations
        }

# Instância global do agente
barber_agent = BarberAgent()