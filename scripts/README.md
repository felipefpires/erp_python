# 📁 Scripts - Automação e Deploy

Esta pasta contém todos os scripts de automação, deploy e manutenção do Sistema ERP.

## 📂 Estrutura

### **📦 deploy/**
Scripts para deploy e gerenciamento do sistema em produção.

- `deploy.sh` - Script de deploy automático
- `deploy_manual.sh` - Script de deploy manual
- `manage.sh` - Script de gerenciamento do sistema

### **🚀 proxmox/**
Scripts específicos para instalação no Proxmox.

- `install_proxmox.sh` - Instalação automática no Proxmox
- `proxmox_upload.sh` - Upload do projeto para Proxmox

### **🧪 tests/**
Scripts de teste para verificar funcionalidades do sistema.

- `test_*.py` - Scripts de teste para diferentes módulos
- `test_customer_creation.py` - Teste de criação de clientes
- `test_dashboard.py` - Teste do dashboard
- `test_system.py` - Teste geral do sistema

### **🔄 migrations/**
Scripts para migração de dados e estrutura do banco.

- `migrate_*.py` - Scripts de migração específicos
- `migrate_categories.py` - Migração de categorias
- `migrate_email_unique.py` - Migração de emails únicos
- `migrate_instagram.py` - Migração de dados do Instagram

## 🚀 Como Usar

### **Para Deploy**
```bash
# Deploy automático
./scripts/deploy/deploy.sh

# Deploy manual
./scripts/deploy/deploy_manual.sh

# Gerenciar sistema
./scripts/deploy/manage.sh
```

### **Para Proxmox**
```bash
# Preparar upload
./scripts/proxmox/proxmox_upload.sh

# Na VM Ubuntu
./scripts/proxmox/install_proxmox.sh
```

### **Para Testes**
```bash
# Executar testes específicos
python scripts/tests/test_customer_creation.py
python scripts/tests/test_dashboard.py
```

### **Para Migrações**
```bash
# Executar migrações
python scripts/migrations/migrate_categories.py
python scripts/migrations/migrate_email_unique.py
```

## 📝 Notas

- Todos os scripts devem ser executados no diretório raiz do projeto
- Scripts de deploy requerem privilégios sudo
- Scripts de teste podem ser executados em ambiente de desenvolvimento
- Sempre faça backup antes de executar migrações
