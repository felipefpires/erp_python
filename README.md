# 🚀 Sistema ERP - Sistema de Gestão Empresarial

Um sistema ERP completo desenvolvido em Python/Flask para gerenciamento de empresas, incluindo CRM, finanças, estoque e agendamentos.

## 📁 Estrutura do Projeto

```
erp-project/
├── 📁 app/                    # Aplicação principal
│   ├── models/               # Modelos de dados
│   ├── routes/               # Rotas da aplicação
│   └── templates/            # Templates HTML
├── 📁 scripts/               # Scripts de automação
│   ├── deploy/               # Scripts de deploy
│   ├── proxmox/              # Scripts para Proxmox
│   ├── tests/                # Scripts de teste
│   └── migrations/           # Scripts de migração
├── 📁 docs/                  # Documentação
│   ├── installation/         # Guias de instalação
│   ├── troubleshooting/      # Solução de problemas
│   └── templates/            # Documentação de templates
├── 📁 tools/                 # Ferramentas de manutenção
│   ├── backup/               # Ferramentas de backup
│   └── maintenance/          # Ferramentas de manutenção
├── 📁 instance/              # Banco de dados SQLite
├── 📁 erros/                 # Relatórios de erros
├── app.py                    # Arquivo principal da aplicação
├── wsgi.py                   # Configuração WSGI
├── config.py                 # Configurações
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

## 🚀 Instalação Rápida

### **Para Desenvolvimento Local**
```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd erp-project

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp config.env .env
# Editar .env com suas configurações

# 5. Inicializar banco de dados
python init_db.py

# 6. Executar aplicação
python app.py
```

### **Para Proxmox (Produção)**
```bash
# 1. Executar script de upload
./scripts/proxmox/proxmox_upload.sh

# 2. Na VM Ubuntu, executar instalação
./scripts/proxmox/install_proxmox.sh
```

## 📚 Documentação

### **Guias de Instalação**
- [📖 Instalação no Proxmox](docs/installation/README_PROXMOX.md)
- [📖 Guia de Deploy](docs/installation/DEPLOY.md)
- [📖 Instalação Manual](docs/installation/INSTALACAO.md)
- [📖 Como Executar](docs/installation/EXECUTAR.md)

### **Solução de Problemas**
- [🔧 Resumo de Sessão CRM](docs/troubleshooting/RESUMO_SESSAO_CRM.md)
- [🔧 Correção de Erro Dashboard](docs/troubleshooting/CORRECAO_ERRO_DASHBOARD.md)

### **Templates**
- [📋 Templates Completos](docs/templates/TEMPLATES_COMPLETOS.md)

## 🔧 Scripts Disponíveis

### **Scripts de Deploy**
- `scripts/deploy/deploy.sh` - Deploy automático
- `scripts/deploy/deploy_manual.sh` - Deploy manual
- `scripts/deploy/manage.sh` - Gerenciamento do sistema

### **Scripts para Proxmox**
- `scripts/proxmox/install_proxmox.sh` - Instalação automática no Proxmox
- `scripts/proxmox/proxmox_upload.sh` - Upload para Proxmox

### **Scripts de Teste**
- `scripts/tests/` - Todos os scripts de teste do sistema

### **Scripts de Migração**
- `scripts/migrations/` - Scripts para migração de dados

## 🤖 Automação GitHub

### **Workflows Automatizados**
- **CI/CD Pipeline** - Testes, builds e deploys automáticos
- **Security Scanning** - Escaneamento de vulnerabilidades
- **Dependabot** - Atualizações automáticas de dependências
- **Code Quality** - Verificação de qualidade de código

### **Comandos Rápidos**
```bash
# Ver todos os comandos disponíveis
make help

# Instalar dependências de desenvolvimento
make install-dev

# Executar todos os checks
make check

# Deploy para produção
make deploy-prod

# Security scan
make security
```

### **Documentação Completa**
- [📖 Guia de Automação](docs/automation/GITHUB_AUTOMATION.md)

## 🛠️ Ferramentas de Manutenção

### **Ferramentas de Backup**
- `tools/backup/` - Ferramentas para backup do sistema

### **Ferramentas de Manutenção**
- `tools/maintenance/` - Ferramentas para manutenção e verificação

## 🌐 Acesso ao Sistema

Após a instalação, o sistema estará disponível em:
- **Desenvolvimento:** `http://localhost:5000`
- **Produção:** `http://IP_DO_SERVIDOR`

## 🔧 Gerenciamento (Produção)

Se instalado via script Proxmox, use o comando `erp-manage`:

```bash
erp-manage status      # Ver status
erp-manage logs        # Ver logs
erp-manage restart     # Reiniciar
erp-manage backup      # Fazer backup
erp-manage update      # Atualizar
erp-manage info        # Informações do sistema
```

## 📊 Módulos do Sistema

- **🏢 CRM** - Gestão de clientes e vendas
- **💰 Finanças** - Controle financeiro e transações
- **📦 Estoque** - Gestão de produtos e inventário
- **📅 Agendamentos** - Calendário e eventos
- **👤 Usuários** - Gestão de usuários e permissões

## 🔒 Segurança

- ✅ Autenticação de usuários
- ✅ Controle de acesso por módulos
- ✅ Validação de dados
- ✅ Proteção contra SQL Injection
- ✅ Headers de segurança (produção)

## 🆘 Suporte

### **Problemas Comuns**
1. **Verifique os logs:** `erp-manage logs` (produção)
2. **Verifique o status:** `erp-manage status` (produção)
3. **Consulte a documentação:** `docs/` 
4. **Verifique troubleshooting:** `docs/troubleshooting/`

### **Desenvolvimento**
- Use os scripts em `scripts/tests/` para testar funcionalidades
- Consulte `docs/templates/` para informações sobre templates
- Use `tools/maintenance/` para verificações do sistema

## 📝 Licença

Este projeto é desenvolvido para uso interno e educacional.

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Teste suas mudanças
4. Envie um pull request

---

**📞 Para suporte adicional:** Consulte a documentação em `docs/` ou entre em contato com a equipe de desenvolvimento.


