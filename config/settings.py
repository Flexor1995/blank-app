"""
Configurações do Sistema de Agendamento para Barbeiros
"""

import os
from typing import Dict, List

# Configurações do SuperAgentes
SUPERAGENTES_CONFIG = {
    "api_key": os.getenv("SUPERAGENTES_API_KEY", ""),
    "base_url": os.getenv("SUPERAGENTES_BASE_URL", "https://api.superagentes.com"),
    "agent_id": os.getenv("SUPERAGENTES_AGENT_ID", ""),
    "webhook_url": os.getenv("SUPERAGENTES_WEBHOOK_URL", "")
}

# Configurações do Make
MAKE_CONFIG = {
    "api_key": os.getenv("MAKE_API_KEY", ""),
    "base_url": os.getenv("MAKE_BASE_URL", "https://eu1.make.com"),
    "scenario_id": os.getenv("MAKE_SCENARIO_ID", ""),
    "webhook_url": os.getenv("MAKE_WEBHOOK_URL", "")
}

# Configurações do WhatsApp Business
WHATSAPP_CONFIG = {
    "access_token": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
    "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
    "verify_token": os.getenv("WHATSAPP_VERIFY_TOKEN", ""),
    "webhook_url": os.getenv("WHATSAPP_WEBHOOK_URL", "")
}

# Configurações do Banco de Dados
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "barber_scheduling"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

# Configurações de Horários
SCHEDULING_CONFIG = {
    "working_hours": {
        "monday": {"start": "08:00", "end": "18:00"},
        "tuesday": {"start": "08:00", "end": "18:00"},
        "wednesday": {"start": "08:00", "end": "18:00"},
        "thursday": {"start": "08:00", "end": "18:00"},
        "friday": {"start": "08:00", "end": "18:00"},
        "saturday": {"start": "08:00", "end": "16:00"},
        "sunday": {"start": "09:00", "end": "14:00"}
    },
    "appointment_duration": 30,  # minutos
    "buffer_time": 15,  # minutos entre agendamentos
    "advance_booking_days": 30,  # dias para agendamento antecipado
    "reminder_hours": [24, 2]  # horas antes do agendamento para lembrete
}

# Configurações de Mensagens
MESSAGE_TEMPLATES = {
    "welcome": "Olá! Sou o assistente virtual da barbearia. Como posso ajudá-lo hoje?",
    "appointment_confirmed": "✅ Agendamento confirmado para {date} às {time}. Aguardamos você!",
    "appointment_cancelled": "❌ Seu agendamento para {date} às {time} foi cancelado.",
    "appointment_rescheduled": "🔄 Seu agendamento foi remarcado para {date} às {time}.",
    "reminder": "⏰ Lembrete: Você tem agendamento amanhã às {time}. Confirma que vai comparecer?",
    "availability_request": "📅 Para qual data você gostaria de agendar?",
    "time_suggestion": "🕐 Horários disponíveis para {date}: {times}",
    "no_availability": "😔 Não há horários disponíveis para {date}. Gostaria de ver outras datas?",
    "confirmation_request": "🤔 Confirma que vai comparecer ao agendamento de {date} às {time}?",
    "help": "💡 Posso ajudá-lo com:\n• Agendamento\n• Verificar disponibilidade\n• Cancelar agendamento\n• Remarcar horário\n• Confirmação de presença"
}

# Configurações de Log
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "barber_scheduling.log"
}

# Configurações de Segurança
SECURITY_CONFIG = {
    "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
    "jwt_expiration": 3600,  # 1 hora
    "max_attempts": 3,  # tentativas máximas de login
    "rate_limit": 100  # requisições por hora
}

# Configurações de Notificações
NOTIFICATION_CONFIG = {
    "email_enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
    "sms_enabled": os.getenv("SMS_ENABLED", "false").lower() == "true",
    "whatsapp_enabled": os.getenv("WHATSAPP_ENABLED", "true").lower() == "true",
    "notification_hours": [9, 12, 15, 18]  # horários para envio de notificações
}

# Configurações de Cache
CACHE_CONFIG = {
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "ttl": 300,  # 5 minutos
    "max_size": 1000
}

# Configurações de Monitoramento
MONITORING_CONFIG = {
    "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
    "metrics_endpoint": "/metrics",
    "health_check_endpoint": "/health",
    "alert_threshold": 0.95  # 95% de disponibilidade
}