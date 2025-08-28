#!/usr/bin/env python3
"""
Script optimizado para iniciar el servidor FastAPI con configuración mejorada
"""

import os
import sys
import uvicorn
from pathlib import Path

# Configurar variables de entorno para TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reducir logs de TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Deshabilitar optimizaciones que causan warnings

def main():
    """Función principal para iniciar el servidor"""
    
    # Configuración del servidor
    config = {
        "app": "main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "reload_dirs": ["."],
        "workers": 1,  # Un solo worker para evitar problemas de multiprocesamiento
        "log_level": "info",
        "access_log": True,
        "use_colors": True,
        "loop": "asyncio",
        "http": "httptools",
        "ws": "websockets",
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "limit_concurrency": 1000,
        "limit_max_requests": 1000,
        "timeout_keep_alive": 5,
        "timeout_graceful_shutdown": 30,
    }
    
    print("🚀 Iniciando servidor FastAPI con configuración optimizada...")
    print(f"📍 URL: http://{config['host']}:{config['port']}")
    print(f"📚 Documentación: http://{config['host']}:{config['port']}/docs")
    print(f"🔄 Modo reload: {'Activado' if config['reload'] else 'Desactivado'}")
    print("=" * 60)
    
    try:
        # Iniciar el servidor
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
