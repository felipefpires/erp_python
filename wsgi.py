#!/usr/bin/env python3
"""
Arquivo WSGI para produção
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
