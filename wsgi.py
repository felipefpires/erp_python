#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
from app import create_app

# Configurar ambiente de produção
os.environ['FLASK_ENV'] = 'production'

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    app.run()
