"""
Lógica de Agendamento para Barbearia
"""

import datetime
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.settings import SCHEDULING_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Appointment:
    """Classe para representar um agendamento"""
    id: str
    client_name: str
    client_phone: str
    date: datetime.date
    time: datetime.time
    service: str
    status: str  # 'confirmed', 'cancelled', 'completed', 'pending'
    created_at: datetime.datetime
    updated_at: datetime.datetime

@dataclass
class TimeSlot:
    """Classe para representar um horário disponível"""
    time: datetime.time
    available: bool
    appointment_id: Optional[str] = None

class BarberScheduler:
    """Classe principal para gerenciar agendamentos"""
    
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.working_hours = SCHEDULING_CONFIG["working_hours"]
        self.appointment_duration = SCHEDULING_CONFIG["appointment_duration"]
        self.buffer_time = SCHEDULING_CONFIG["buffer_time"]
        self.advance_booking_days = SCHEDULING_CONFIG["advance_booking_days"]
        
    def is_working_day(self, date: datetime.date) -> bool:
        """Verifica se é um dia de trabalho"""
        weekday = date.strftime("%A").lower()
        return weekday in self.working_hours
    
    def get_working_hours_for_date(self, date: datetime.date) -> Tuple[datetime.time, datetime.time]:
        """Retorna horário de início e fim para uma data específica"""
        weekday = date.strftime("%A").lower()
        if weekday in self.working_hours:
            start_str = self.working_hours[weekday]["start"]
            end_str = self.working_hours[weekday]["end"]
            start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
            return start_time, end_time
        return None, None
    
    def generate_time_slots(self, date: datetime.date) -> List[TimeSlot]:
        """Gera todos os horários possíveis para uma data"""
        start_time, end_time = self.get_working_hours_for_date(date)
        if not start_time or not end_time:
            return []
        
        slots = []
        current_time = start_time
        
        while current_time < end_time:
            # Verifica se o horário não está ocupado
            available = self.is_time_slot_available(date, current_time)
            appointment_id = self.get_appointment_id_for_time(date, current_time)
            
            slot = TimeSlot(
                time=current_time,
                available=available,
                appointment_id=appointment_id
            )
            slots.append(slot)
            
            # Avança para o próximo horário (incluindo buffer)
            current_minutes = current_time.hour * 60 + current_time.minute
            next_minutes = current_minutes + self.appointment_duration + self.buffer_time
            current_time = datetime.time(
                hour=next_minutes // 60,
                minute=next_minutes % 60
            )
        
        return slots
    
    def is_time_slot_available(self, date: datetime.date, time: datetime.time) -> bool:
        """Verifica se um horário específico está disponível"""
        for appointment in self.appointments.values():
            if (appointment.date == date and 
                appointment.time == time and 
                appointment.status == 'confirmed'):
                return False
        return True
    
    def get_appointment_id_for_time(self, date: datetime.date, time: datetime.time) -> Optional[str]:
        """Retorna o ID do agendamento para um horário específico"""
        for appointment in self.appointments.values():
            if (appointment.date == date and 
                appointment.time == time and 
                appointment.status == 'confirmed'):
                return appointment.id
        return None
    
    def get_available_slots(self, date: datetime.date) -> List[TimeSlot]:
        """Retorna apenas os horários disponíveis para uma data"""
        all_slots = self.generate_time_slots(date)
        return [slot for slot in all_slots if slot.available]
    
    def can_book_advance(self, date: datetime.date) -> bool:
        """Verifica se pode agendar com antecedência"""
        today = datetime.date.today()
        max_date = today + datetime.timedelta(days=self.advance_booking_days)
        return date <= max_date
    
    def create_appointment(self, client_name: str, client_phone: str, 
                         date: datetime.date, time: datetime.time, 
                         service: str = "Corte") -> Tuple[bool, str, Optional[str]]:
        """
        Cria um novo agendamento
        
        Returns:
            Tuple[bool, str, Optional[str]]: (sucesso, mensagem, appointment_id)
        """
        try:
            # Validações
            if not self.is_working_day(date):
                return False, "Desculpe, não trabalhamos neste dia da semana.", None
            
            if not self.can_book_advance(date):
                return False, f"Desculpe, só aceitamos agendamentos com até {self.advance_booking_days} dias de antecedência.", None
            
            if not self.is_time_slot_available(date, time):
                return False, "Desculpe, este horário não está mais disponível.", None
            
            # Cria o agendamento
            appointment_id = f"apt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{client_phone[-4:]}"
            
            appointment = Appointment(
                id=appointment_id,
                client_name=client_name,
                client_phone=client_phone,
                date=date,
                time=time,
                service=service,
                status='confirmed',
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            
            self.appointments[appointment_id] = appointment
            logger.info(f"Agendamento criado: {appointment_id} para {client_name} em {date} às {time}")
            
            return True, "Agendamento realizado com sucesso!", appointment_id
            
        except Exception as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            return False, "Desculpe, ocorreu um erro ao criar o agendamento. Tente novamente.", None
    
    def cancel_appointment(self, appointment_id: str) -> Tuple[bool, str]:
        """Cancela um agendamento existente"""
        try:
            if appointment_id not in self.appointments:
                return False, "Agendamento não encontrado."
            
            appointment = self.appointments[appointment_id]
            if appointment.status == 'cancelled':
                return False, "Este agendamento já foi cancelado."
            
            appointment.status = 'cancelled'
            appointment.updated_at = datetime.datetime.now()
            
            logger.info(f"Agendamento cancelado: {appointment_id}")
            return True, "Agendamento cancelado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao cancelar agendamento: {str(e)}")
            return False, "Desculpe, ocorreu um erro ao cancelar o agendamento."
    
    def reschedule_appointment(self, appointment_id: str, new_date: datetime.date, 
                             new_time: datetime.time) -> Tuple[bool, str]:
        """Remarca um agendamento existente"""
        try:
            if appointment_id not in self.appointments:
                return False, "Agendamento não encontrado."
            
            appointment = self.appointments[appointment_id]
            if appointment.status == 'cancelled':
                return False, "Não é possível remarcar um agendamento cancelado."
            
            # Verifica se o novo horário está disponível
            if not self.is_time_slot_available(new_date, new_time):
                return False, "Desculpe, este horário não está disponível."
            
            # Atualiza o agendamento
            old_date = appointment.date
            old_time = appointment.time
            
            appointment.date = new_date
            appointment.time = new_time
            appointment.updated_at = datetime.datetime.now()
            
            logger.info(f"Agendamento remarcado: {appointment_id} de {old_date} {old_time} para {new_date} {new_time}")
            return True, "Agendamento remarcado com sucesso!"
            
        except Exception as e:
            logger.error(f"Erro ao remarcar agendamento: {str(e)}")
            return False, "Desculpe, ocorreu um erro ao remarcar o agendamento."
    
    def get_appointment_by_client(self, client_phone: str) -> List[Appointment]:
        """Retorna todos os agendamentos de um cliente"""
        return [
            apt for apt in self.appointments.values() 
            if apt.client_phone == client_phone and apt.status != 'cancelled'
        ]
    
    def get_appointment_by_date(self, date: datetime.date) -> List[Appointment]:
        """Retorna todos os agendamentos de uma data específica"""
        return [
            apt for apt in self.appointments.values() 
            if apt.date == date and apt.status == 'confirmed'
        ]
    
    def get_upcoming_appointments(self, hours_ahead: int = 24) -> List[Appointment]:
        """Retorna agendamentos próximos (próximas X horas)"""
        now = datetime.datetime.now()
        cutoff_time = now + datetime.timedelta(hours=hours_ahead)
        
        upcoming = []
        for appointment in self.appointments.values():
            if appointment.status != 'confirmed':
                continue
                
            appointment_datetime = datetime.datetime.combine(appointment.date, appointment.time)
            if now <= appointment_datetime <= cutoff_time:
                upcoming.append(appointment)
        
        return sorted(upcoming, key=lambda x: (x.date, x.time))
    
    def get_appointment_statistics(self) -> Dict:
        """Retorna estatísticas dos agendamentos"""
        total = len(self.appointments)
        confirmed = len([apt for apt in self.appointments.values() if apt.status == 'confirmed'])
        cancelled = len([apt for apt in self.appointments.values() if apt.status == 'cancelled'])
        completed = len([apt for apt in self.appointments.values() if apt.status == 'completed'])
        
        return {
            'total': total,
            'confirmed': confirmed,
            'cancelled': cancelled,
            'completed': completed,
            'occupancy_rate': (confirmed / total * 100) if total > 0 else 0
        }
    
    def cleanup_old_appointments(self, days_to_keep: int = 90):
        """Remove agendamentos antigos para limpeza do sistema"""
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days_to_keep)
        
        to_remove = []
        for appointment_id, appointment in self.appointments.items():
            if appointment.date < cutoff_date:
                to_remove.append(appointment_id)
        
        for appointment_id in to_remove:
            del self.appointments[appointment_id]
        
        logger.info(f"Removidos {len(to_remove)} agendamentos antigos")
        return len(to_remove)

# Instância global do scheduler
scheduler = BarberScheduler()