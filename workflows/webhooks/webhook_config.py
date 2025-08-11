#!/usr/bin/env python3
"""
Configuração dos Webhooks para integração SuperAgentes <-> Make
"""

import os
from typing import Dict, Any

# Configurações dos Webhooks
WEBHOOK_CONFIG = {
    "superagentes": {
        "port": int(os.getenv("SUPERAGENTES_WEBHOOK_PORT", 5000)),
        "host": os.getenv("SUPERAGENTES_WEBHOOK_HOST", "0.0.0.0"),
        "endpoint": "/webhook/superagentes",
        "verify_token": os.getenv("SUPERAGENTES_VERIFY_TOKEN", "default_verify_token"),
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": {
            "requests_per_minute": 60,
            "burst_size": 10
        }
    },
    "make": {
        "port": int(os.getenv("MAKE_WEBHOOK_PORT", 5001)),
        "host": os.getenv("MAKE_WEBHOOK_HOST", "0.0.0.0"),
        "endpoint": "/webhook/make",
        "webhook_token": os.getenv("MAKE_WEBHOOK_TOKEN", "default_make_token"),
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": {
            "requests_per_minute": 100,
            "burst_size": 20
        }
    },
    "whatsapp": {
        "port": int(os.getenv("WHATSAPP_WEBHOOK_PORT", 5002)),
        "host": os.getenv("WHATSAPP_WEBHOOK_HOST", "0.0.0.0"),
        "endpoint": "/webhook/whatsapp",
        "verify_token": os.getenv("WHATSAPP_VERIFY_TOKEN", "default_whatsapp_token"),
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": {
            "requests_per_minute": 50,
            "burst_size": 5
        }
    }
}

# Configurações de Segurança
SECURITY_CONFIG = {
    "cors": {
        "enabled": True,
        "allowed_origins": [
            "https://superagentes.com",
            "https://make.com",
            "https://webhook.site"
        ],
        "allowed_methods": ["GET", "POST", "OPTIONS"],
        "allowed_headers": ["Content-Type", "Authorization"]
    },
    "rate_limiting": {
        "enabled": True,
        "storage": "redis",  # ou "memory"
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379")
    },
    "authentication": {
        "enabled": True,
        "methods": ["bearer_token", "api_key"],
        "token_expiry": 3600  # 1 hora
    }
}

# Configurações de Logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": {
        "enabled": True,
        "path": "logs/webhooks.log",
        "max_size": "10MB",
        "backup_count": 5
    },
    "console": {
        "enabled": True,
        "colored": True
    }
}

# Configurações de Monitoramento
MONITORING_CONFIG = {
    "enabled": True,
    "metrics": {
        "enabled": True,
        "endpoint": "/metrics",
        "collectors": [
            "request_count",
            "response_time",
            "error_rate",
            "active_connections"
        ]
    },
    "health_check": {
        "enabled": True,
        "endpoint": "/health",
        "check_interval": 30,
        "timeout": 5
    },
    "alerts": {
        "enabled": True,
        "webhook_url": os.getenv("ALERT_WEBHOOK_URL"),
        "thresholds": {
            "error_rate": 0.05,
            "response_time": 5000,
            "memory_usage": 0.8
        }
    }
}

# Configurações de Banco de Dados para Webhooks
DATABASE_CONFIG = {
    "webhook_logs": {
        "enabled": True,
        "table": "webhook_logs",
        "fields": [
            "id",
            "timestamp",
            "source",
            "endpoint",
            "method",
            "status_code",
            "response_time",
            "payload_size",
            "error_message"
        ]
    },
    "rate_limit_data": {
        "enabled": True,
        "table": "rate_limit_data",
        "fields": [
            "ip_address",
            "endpoint",
            "request_count",
            "window_start",
            "window_end"
        ]
    }
}

# Configurações de Retry e Fallback
RETRY_CONFIG = {
    "enabled": True,
    "max_attempts": 3,
    "backoff_factor": 2,
    "max_delay": 60,
    "retryable_status_codes": [408, 429, 500, 502, 503, 504],
    "fallback": {
        "enabled": True,
        "message": "Serviço temporariamente indisponível. Tente novamente em alguns instantes.",
        "action": "queue_for_later"
    }
}

# Configurações de Fila para Processamento Assíncrono
QUEUE_CONFIG = {
    "enabled": True,
    "backend": "redis",  # ou "celery", "rq"
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "queues": {
        "high_priority": {
            "name": "high_priority",
            "max_workers": 5,
            "timeout": 30
        },
        "default": {
            "name": "default",
            "max_workers": 10,
            "timeout": 60
        },
        "low_priority": {
            "name": "low_priority",
            "max_workers": 3,
            "timeout": 120
        }
    }
}

# Configurações de Cache
CACHE_CONFIG = {
    "enabled": True,
    "backend": "redis",
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "default_ttl": 300,  # 5 minutos
    "patterns": {
        "webhook_verification": {
            "ttl": 3600,  # 1 hora
            "key_pattern": "webhook:verify:{token}"
        },
        "rate_limit": {
            "ttl": 60,  # 1 minuto
            "key_pattern": "rate_limit:{ip}:{endpoint}"
        },
        "session_data": {
            "ttl": 1800,  # 30 minutos
            "key_pattern": "session:{session_id}"
        }
    }
}

# Configurações de Notificações
NOTIFICATION_CONFIG = {
    "enabled": True,
    "channels": {
        "email": {
            "enabled": True,
            "smtp_server": os.getenv("SMTP_SERVER"),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("FROM_EMAIL")
        },
        "slack": {
            "enabled": True,
            "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
            "channel": "#webhooks"
        },
        "telegram": {
            "enabled": True,
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID")
        }
    },
    "triggers": {
        "webhook_failure": {
            "enabled": True,
            "threshold": 3,
            "channels": ["email", "slack"]
        },
        "rate_limit_exceeded": {
            "enabled": True,
            "threshold": 10,
            "channels": ["slack"]
        },
        "high_error_rate": {
            "enabled": True,
            "threshold": 0.1,
            "channels": ["email", "slack", "telegram"]
        }
    }
}

# Configurações de Teste
TEST_CONFIG = {
    "enabled": True,
    "endpoints": {
        "superagentes": "/webhook/superagentes/test",
        "make": "/webhook/make/test",
        "whatsapp": "/webhook/whatsapp/test"
    },
    "test_data": {
        "valid_message": {
            "text": "Olá, gostaria de agendar um horário",
            "from": "5511999999999",
            "conversation_id": "test_123"
        },
        "valid_appointment": {
            "phone_number": "5511999999999",
            "date": "2024-01-15",
            "time": "14:00",
            "client_name": "João Silva"
        }
    },
    "mocking": {
        "enabled": True,
        "external_apis": True,
        "database": True,
        "whatsapp": True
    }
}

def get_webhook_config(webhook_type: str) -> Dict[str, Any]:
    """Retorna configuração específica de um webhook"""
    return WEBHOOK_CONFIG.get(webhook_type, {})

def get_all_configs() -> Dict[str, Any]:
    """Retorna todas as configurações"""
    return {
        "webhooks": WEBHOOK_CONFIG,
        "security": SECURITY_CONFIG,
        "logging": LOGGING_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "database": DATABASE_CONFIG,
        "retry": RETRY_CONFIG,
        "queue": QUEUE_CONFIG,
        "cache": CACHE_CONFIG,
        "notifications": NOTIFICATION_CONFIG,
        "test": TEST_CONFIG
    }

def validate_config() -> bool:
    """Valida se todas as configurações obrigatórias estão presentes"""
    required_env_vars = [
        "SUPERAGENTES_API_KEY",
        "MAKE_API_KEY",
        "WHATSAPP_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
        return False
    
    print("✅ Todas as configurações estão válidas")
    return True

if __name__ == "__main__":
    # Valida configurações ao executar o arquivo
    validate_config()
    
    # Exibe configurações atuais
    configs = get_all_configs()
    print("\n📋 Configurações dos Webhooks:")
    for section, config in configs.items():
        print(f"\n🔧 {section.upper()}:")
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")