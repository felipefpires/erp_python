# 🚀 Deploy Automático do Sistema ERP

Este guia explica como configurar um sistema de deploy automático para o ERP System usando GitHub Actions e um servidor dedicado.

## 📋 Pré-requisitos

- Servidor Ubuntu/Debian dedicado
- Repositório GitHub do projeto
- Acesso root ao servidor
- Domínio configurado (opcional, para SSL)

## 🔧 Configuração Inicial do Servidor

### 1. Preparar o Servidor

Execute o script de instalação no servidor:

```bash
# Conectar ao servidor
ssh root@SEU_SERVIDOR_IP

# Baixar o projeto
git clone https://github.com/SEU_USUARIO/erp-project.git
cd erp-project

# Executar instalação
chmod +x scripts/deploy/install.sh
./scripts/deploy/install.sh
```

O script irá:
- ✅ Instalar todas as dependências
- ✅ Configurar ambiente Python
- ✅ Criar usuário dedicado (erp)
- ✅ Configurar Nginx como proxy reverso
- ✅ Configurar systemd service
- ✅ Configurar firewall
- ✅ Configurar backup automático
- ✅ Inicializar banco de dados

### 2. Configurar SSH Key para GitHub Actions

```bash
# Gerar chave SSH no servidor
ssh-keygen -t rsa -b 4096 -C "erp@seudominio.com"

# Mostrar chave pública
cat ~/.ssh/id_rsa.pub
```

### 3. Configurar Secrets no GitHub

No seu repositório GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

- `SERVER_HOST`: IP do seu servidor
- `SERVER_USER`: erp
- `SERVER_SSH_KEY`: Conteúdo da chave privada SSH
- `SERVER_PORT`: 22

## 🔄 Deploy Automático

### Como Funciona

1. **Push para main/master**: Quando você fizer push para o branch principal
2. **GitHub Actions**: Executa o workflow automaticamente
3. **Deploy**: Conecta ao servidor e atualiza o sistema
4. **Restart**: Reinicia o serviço com as novas mudanças

### Workflow do GitHub Actions

O arquivo `.github/workflows/deploy.yml` contém:

```yaml
name: Deploy to Production Server

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: ${{ secrets.SERVER_PORT }}
        script: |
          cd /opt/erp-system
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          python init_db.py
          sudo systemctl restart erp-system
```

## 🛠️ Gerenciamento do Sistema

### Comandos Úteis

```bash
# Ver status do sistema
sudo /opt/erp-system/scripts/deploy/manage.sh status

# Ver logs
sudo /opt/erp-system/scripts/deploy/manage.sh logs

# Reiniciar sistema
sudo /opt/erp-system/scripts/deploy/manage.sh restart

# Fazer backup manual
sudo /opt/erp-system/scripts/deploy/manage.sh backup

# Restaurar backup
sudo /opt/erp-system/scripts/deploy/manage.sh restore /caminho/do/backup.db

# Verificar saúde do sistema
sudo /opt/erp-system/scripts/deploy/manage.sh health

# Limpar logs e cache
sudo /opt/erp-system/scripts/deploy/manage.sh clean
```

### Estrutura de Diretórios

```
/opt/erp-system/          # Aplicação principal
├── app/                  # Código da aplicação
├── instance/             # Banco de dados SQLite
├── venv/                 # Ambiente virtual Python
├── scripts/deploy/       # Scripts de deploy
└── .env                  # Configurações

/opt/backups/erp/         # Backups automáticos
/etc/systemd/system/      # Serviço systemd
/etc/nginx/sites-available/ # Configuração Nginx
```

## 🔒 Configuração SSL (Opcional)

Para configurar HTTPS com Let's Encrypt:

```bash
# Executar script SSL
sudo /opt/erp-system/scripts/deploy/ssl_setup.sh
```

O script irá:
- ✅ Instalar Certbot
- ✅ Configurar certificado SSL
- ✅ Configurar renovação automática
- ✅ Configurar redirecionamento HTTP → HTTPS

## 📊 Monitoramento

### Logs do Sistema

```bash
# Logs do serviço ERP
journalctl -u erp-system -f

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup Automático

- **Frequência**: Diário
- **Localização**: `/opt/backups/erp/`
- **Retenção**: 7 dias
- **Formato**: `erp_YYYYMMDD_HHMMSS.db`

## 🔧 Manutenção

### Atualização Manual

```bash
# Atualizar código
cd /opt/erp-system
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar serviço
sudo systemctl restart erp-system
```

### Troubleshooting

#### Serviço não inicia
```bash
# Verificar logs
sudo journalctl -u erp-system -n 50

# Verificar permissões
sudo chown -R erp:erp /opt/erp-system

# Verificar configuração
sudo systemctl status erp-system
```

#### Nginx não funciona
```bash
# Testar configuração
sudo nginx -t

# Verificar status
sudo systemctl status nginx

# Verificar portas
sudo netstat -tlnp | grep :80
```

#### Banco de dados corrompido
```bash
# Restaurar último backup
sudo /opt/erp-system/scripts/deploy/manage.sh restore /opt/backups/erp/ultimo_backup.db
```

## 🚨 Segurança

### Firewall Configurado

- ✅ SSH (porta 22)
- ✅ HTTP (porta 80)
- ✅ HTTPS (porta 443)
- ❌ Todas as outras portas bloqueadas

### Usuário Dedicado

- ✅ Usuário `erp` sem privilégios root
- ✅ Aplicação roda com permissões mínimas
- ✅ Isolamento de processos

### Backup Automático

- ✅ Backup diário automático
- ✅ Retenção de 7 dias
- ✅ Localização segura

## 📞 Suporte

### Informações do Sistema

```bash
# Versão do sistema
cat /opt/erp-system/version.txt

# Status completo
sudo /opt/erp-system/scripts/deploy/manage.sh health

# Informações do servidor
uname -a
df -h
free -h
```

### Contatos

- **Documentação**: `/opt/erp-system/docs/`
- **Logs**: `/var/log/`
- **Backups**: `/opt/backups/erp/`
- **Configurações**: `/opt/erp-system/.env`

---

## ✅ Checklist de Deploy

- [ ] Servidor Ubuntu/Debian configurado
- [ ] Script de instalação executado
- [ ] SSH key configurada
- [ ] Secrets do GitHub configurados
- [ ] Primeiro deploy testado
- [ ] SSL configurado (opcional)
- [ ] Backup funcionando
- [ ] Monitoramento ativo

**🎉 Sistema pronto para produção!**
