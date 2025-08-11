.PHONY: help install test lint format security clean deploy

# Default target
help:
	@echo "🚀 Sistema ERP - Comandos Disponíveis"
	@echo ""
	@echo "📦 Instalação:"
	@echo "  install     - Instalar dependências"
	@echo "  install-dev - Instalar dependências de desenvolvimento"
	@echo ""
	@echo "🧪 Testes:"
	@echo "  test        - Executar testes"
	@echo "  test-cov    - Executar testes com coverage"
	@echo "  test-watch  - Executar testes em modo watch"
	@echo ""
	@echo "🔍 Qualidade de Código:"
	@echo "  lint        - Executar linting"
	@echo "  format      - Formatar código"
	@echo "  check       - Executar todos os checks"
	@echo ""
	@echo "🔒 Segurança:"
	@echo "  security    - Executar security scan"
	@echo "  audit       - Auditoria de dependências"
	@echo ""
	@echo "🚀 Deploy:"
	@echo "  deploy      - Deploy local"
	@echo "  deploy-prod - Deploy para produção"
	@echo ""
	@echo "🧹 Limpeza:"
	@echo "  clean       - Limpar arquivos temporários"
	@echo "  clean-all   - Limpeza completa"

# Instalação
install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Instalando dependências de desenvolvimento..."
	pip install -e ".[dev]"

# Testes
test:
	@echo "🧪 Executando testes..."
	pytest

test-cov:
	@echo "🧪 Executando testes com coverage..."
	pytest --cov=app --cov-report=html --cov-report=term

test-watch:
	@echo "🧪 Executando testes em modo watch..."
	pytest-watch

# Qualidade de código
lint:
	@echo "🔍 Executando linting..."
	flake8 app/ scripts/ tools/
	black --check app/ scripts/ tools/

format:
	@echo "🎨 Formatando código..."
	black app/ scripts/ tools/
	isort app/ scripts/ tools/

check: lint test security
	@echo "✅ Todos os checks passaram!"

# Segurança
security:
	@echo "🔒 Executando security scan..."
	bandit -r app/ -f json -o bandit-report.json || true
	bandit -r app/ -f txt -o bandit-report.txt || true
	safety check --json --output safety-report.json || true
	safety check --output safety-report.txt || true
	@echo "📊 Relatórios de segurança gerados:"
	@echo "  - bandit-report.json"
	@echo "  - bandit-report.txt"
	@echo "  - safety-report.json"
	@echo "  - safety-report.txt"

audit:
	@echo "🔍 Executando auditoria de dependências..."
	pip-audit --format json --output pip-audit-report.json || true
	pip-audit --format text --output pip-audit-report.txt || true

# Deploy
deploy:
	@echo "🚀 Iniciando deploy local..."
	python app.py

deploy-prod:
	@echo "🚀 Deploy para produção via GitHub Actions..."
	gh workflow run deploy-proxmox.yml

# Limpeza
clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f *.log

clean-all: clean
	@echo "🧹 Limpeza completa..."
	rm -rf venv/
	rm -rf .venv/
	rm -rf build/
	rm -rf dist/
	rm -f *.tar.gz
	rm -f bandit-report.*
	rm -f safety-report.*
	rm -f pip-audit-report.*

# Desenvolvimento
dev:
	@echo "🚀 Iniciando servidor de desenvolvimento..."
	export FLASK_ENV=development
	export FLASK_DEBUG=1
	python app.py

# Banco de dados
db-init:
	@echo "🗄️ Inicializando banco de dados..."
	python init_db.py

db-migrate:
	@echo "🔄 Executando migrações..."
	python scripts/migrations/migrate_categories.py
	python scripts/migrations/migrate_email_unique.py
	python scripts/migrations/migrate_instagram.py

# Utilitários
backup:
	@echo "💾 Criando backup..."
	tar -czf erp-backup-$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude='.git' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='venv' \
		--exclude='.venv' \
		--exclude='instance' \
		.

status:
	@echo "📊 Status do sistema:"
	@echo "  Python: $(shell python --version)"
	@echo "  Pip: $(shell pip --version)"
	@echo "  Flask: $(shell python -c 'import flask; print(flask.__version__)' 2>/dev/null || echo 'Não instalado')"
	@echo "  Pytest: $(shell python -c 'import pytest; print(pytest.__version__)' 2>/dev/null || echo 'Não instalado')"

# Docker (se aplicável)
docker-build:
	@echo "🐳 Construindo imagem Docker..."
	docker build -t erp-system .

docker-run:
	@echo "🐳 Executando container Docker..."
	docker run -p 5000:5000 erp-system

# GitHub
gh-status:
	@echo "📊 Status do GitHub:"
	gh workflow list
	gh run list --limit 5

gh-deploy:
	@echo "🚀 Triggering deploy via GitHub Actions..."
	gh workflow run deploy-proxmox.yml

# Proxmox
proxmox-upload:
	@echo "📤 Preparando upload para Proxmox..."
	./scripts/proxmox/proxmox_upload.sh

proxmox-install:
	@echo "📥 Instalando no Proxmox..."
	./scripts/proxmox/install_proxmox.sh
