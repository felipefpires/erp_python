# 🤖 Automação GitHub - Sistema ERP

Este documento explica como configurar e usar a automação completa do GitHub para o Sistema ERP.

## 📋 Visão Geral

A automação do GitHub inclui:

- ✅ **CI/CD Pipeline** - Testes, builds e deploys automáticos
- ✅ **Security Scanning** - Escaneamento de vulnerabilidades
- ✅ **Dependabot** - Atualizações automáticas de dependências
- ✅ **Templates** - Templates para issues e pull requests
- ✅ **Code Quality** - Verificação de qualidade de código

## 🚀 Workflows Configurados

### **1. CI/CD Pipeline (`ci.yml`)**

**Triggers:**
- Push para `main` e `develop`
- Pull requests para `main` e `develop`

**Jobs:**
- **Test** - Testes em múltiplas versões do Python
- **Security** - Escaneamento de segurança
- **Build** - Criação de pacote de deploy
- **Deploy** - Deploy automático (staging/production)

### **2. Deploy Proxmox (`deploy-proxmox.yml`)**

**Triggers:**
- Push para `main`
- Manual dispatch

**Funcionalidades:**
- Deploy automático para VM Proxmox
- Backup automático antes do deploy
- Verificação pós-deploy
- Rollback em caso de falha

### **3. Security Scan (`security-scan.yml`)**

**Triggers:**
- Agendado (toda segunda-feira)
- Push para `main` e `develop`
- Pull requests

**Ferramentas:**
- **Bandit** - Análise estática de segurança
- **Safety** - Verificação de vulnerabilidades conhecidas
- **pip-audit** - Auditoria de dependências

## 🔧 Configuração

### **1. Secrets do GitHub**

Configure os seguintes secrets no seu repositório:

```bash
# Para deploy no Proxmox
PROXMOX_HOST=192.168.1.100
PROXMOX_USER=ubuntu
PROXMOX_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
PROXMOX_PORT=22

# Para notificações (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### **2. Environments**

Configure os environments no GitHub:

**Staging:**
- Protection rules: Require reviewers
- Deployment branches: `develop`

**Production:**
- Protection rules: Require reviewers, wait timer
- Deployment branches: `main`

### **3. Branch Protection**

Configure proteção para as branches principais:

**main:**
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes that create files

**develop:**
- Require pull request reviews
- Require status checks to pass

## 📊 Dependabot

### **Configuração**

O Dependabot está configurado para:

- **Python (pip)** - Atualizações semanais
- **GitHub Actions** - Atualizações semanais
- **Docker** - Atualizações semanais (se aplicável)

### **Ignorar Atualizações**

Dependências críticas são protegidas contra atualizações major:

```yaml
ignore:
  - dependency-name: "flask"
    update-types: ["version-update:semver-major"]
  - dependency-name: "sqlalchemy"
    update-types: ["version-update:semver-major"]
```

## 🧪 Testes Automatizados

### **Execução Local**

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Executar com coverage
pytest --cov=app --cov-report=html

# Executar linting
flake8
black --check .

# Executar security scan
bandit -r app/
safety check
```

### **Configuração de Testes**

- **pytest** - Framework de testes
- **pytest-cov** - Cobertura de código
- **black** - Formatação de código
- **flake8** - Linting
- **bandit** - Segurança

## 🔒 Segurança

### **Escaneamento Automático**

**Ferramentas:**
- **Bandit** - Vulnerabilidades Python
- **Safety** - Dependências vulneráveis
- **pip-audit** - Auditoria de pacotes

**Frequência:**
- Semanal (agendado)
- A cada push/PR
- Manual (via workflow dispatch)

### **Relatórios**

Os relatórios de segurança são:
- Salvos como artifacts
- Comentados em PRs
- Disponíveis para download

## 📝 Templates

### **Issue Templates**

- **Bug Report** - Para reportar bugs
- **Feature Request** - Para solicitar features

### **Pull Request Template**

Template completo com:
- Descrição das mudanças
- Checklist de qualidade
- Informações de deploy
- Impacto das mudanças

## 🚀 Deploy Automático

### **Fluxo de Deploy**

1. **Push para `develop`** → Deploy para staging
2. **Push para `main`** → Deploy para production
3. **Manual dispatch** → Deploy sob demanda

### **Processo de Deploy**

1. **Backup** - Backup automático da instalação atual
2. **Stop Services** - Parar serviços em execução
3. **Deploy** - Instalar nova versão
4. **Update Dependencies** - Atualizar dependências Python
5. **Restart Services** - Reiniciar serviços
6. **Verify** - Verificar se tudo está funcionando

### **Rollback**

Em caso de falha:
- Backup é mantido
- Serviços podem ser restaurados
- Logs detalhados são gerados

## 📈 Monitoramento

### **Status Checks**

- ✅ Testes passando
- ✅ Cobertura de código
- ✅ Security scan limpo
- ✅ Linting aprovado

### **Notificações**

- Status de deploy
- Falhas de segurança
- Atualizações de dependências
- Pull requests pendentes

## 🔧 Comandos Úteis

### **GitHub CLI**

```bash
# Ver workflows
gh workflow list

# Executar workflow manualmente
gh workflow run deploy-proxmox.yml

# Ver logs de workflow
gh run list
gh run view <run-id>

# Ver artifacts
gh run download <run-id>
```

### **Local Development**

```bash
# Setup completo
pip install -e ".[dev]"
pre-commit install

# Executar todos os checks
make check

# Executar testes
make test

# Executar security scan
make security
```

## 🆘 Troubleshooting

### **Problemas Comuns**

**1. Workflow falha nos testes**
- Verifique logs detalhados
- Execute testes localmente
- Verifique dependências

**2. Deploy falha**
- Verifique secrets do GitHub
- Verifique conectividade SSH
- Verifique logs do servidor

**3. Security scan encontra vulnerabilidades**
- Atualize dependências vulneráveis
- Revise código com problemas
- Configure exceções se necessário

### **Logs e Debug**

- **GitHub Actions** - Logs detalhados em cada job
- **Servidor** - Logs do supervisor e nginx
- **Aplicação** - Logs da aplicação Flask

## 📚 Recursos Adicionais

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Security Best Practices](https://docs.github.com/en/code-security)
- [Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

---

**🎯 Resultado:** Automação completa do ciclo de desenvolvimento, desde commit até deploy em produção!
