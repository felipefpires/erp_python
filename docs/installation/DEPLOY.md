# 🚀 Guia de Deploy - Sistema ERP

Este guia explica como fazer o deploy do Sistema ERP em um servidor Ubuntu/Proxmox.

## 📋 Pré-requisitos

- Servidor Ubuntu 20.04+ ou similar
- Acesso SSH com privilégios sudo
- Python 3.8+
- Git (opcional, para atualizações)

## 🔧 Preparação do Servidor

### 1. Conectar ao Servidor

```bash
ssh usuario@seu-servidor.com
```

### 2. Atualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Transferir Código

**Opção A: Via SCP (recomendado para primeira vez)**
```bash
# No seu computador local
scp -r . usuario@seu-servidor.com:/tmp/erp-system/
```

**Opção B: Via Git**
```bash
# No servidor
cd /tmp
git clone https://github.com/seu-usuario/erp-system.git
```

## 🚀 Deploy Automático

### 1. Executar Script de Deploy

```bash
# No servidor
cd /tmp/erp-system
chmod +x deploy.sh
./deploy.sh
```

O script irá:
- ✅ Instalar dependências do sistema
- ✅ Criar usuário `erp` para a aplicação
- ✅ Configurar ambiente virtual Python
- ✅ Instalar dependências Python
- ✅ Configurar Nginx como proxy reverso
- ✅ Configurar Supervisor para gerenciar processos
- ✅ Inicializar banco de dados
- ✅ Iniciar serviços

### 2. Verificar Deploy

```bash
# Verificar status
sudo supervisorctl status erp-system
sudo systemctl status nginx

# Ver logs
tail -f /opt/erp-system/logs/error.log
```

## 🔧 Gerenciamento do Sistema

### Script de Gerenciamento

```bash
# Copiar script de gerenciamento
sudo cp manage.sh /usr/local/bin/erp-manage
sudo chmod +x /usr/local/bin/erp-manage

# Usar o script
erp-manage status    # Ver status
erp-manage logs      # Ver logs
erp-manage restart   # Reiniciar
erp-manage backup    # Fazer backup
```

### Comandos Úteis

```bash
# Ver status dos serviços
sudo supervisorctl status
sudo systemctl status nginx

# Ver logs em tempo real
tail -f /opt/erp-system/logs/access.log
tail -f /opt/erp-system/logs/error.log

# Reiniciar serviços
sudo supervisorctl restart erp-system
sudo systemctl reload nginx

# Fazer backup manual
sudo -u erp cp /opt/erp-system/instance/erp.db /opt/erp-system/backups/
```

## 🌐 Configuração de Domínio

### 1. Configurar DNS

Aponte seu domínio para o IP do servidor:
```
A    erp.seudominio.com    ->    IP_DO_SERVIDOR
```

### 2. Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d erp.seudominio.com

# Renovar automaticamente
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Atualizar Configuração Nginx

Editar `/etc/nginx/sites-available/erp-system`:
```nginx
server {
    listen 80;
    server_name erp.seudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.seudominio.com;
    
    ssl_certificate /etc/letsencrypt/live/erp.seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.seudominio.com/privkey.pem;
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/erp-system/erp-system.sock;
    }
    
    location /static {
        alias /opt/erp-system/app/static;
    }
    
    location /uploads {
        alias /opt/erp-system/uploads;
    }
}
```

## 🔒 Segurança

### 1. Firewall

```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2ban

```bash
# Instalar Fail2ban
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Atualizações Automáticas

```bash
# Instalar unattended-upgrades
sudo apt install unattended-upgrades

# Configurar
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📊 Monitoramento

### 1. Logs

```bash
# Ver logs de acesso
tail -f /opt/erp-system/logs/access.log

# Ver logs de erro
tail -f /opt/erp-system/logs/error.log

# Ver logs do sistema
sudo journalctl -u nginx -f
sudo journalctl -u supervisor -f
```

### 2. Métricas

```bash
# Ver uso de recursos
htop
df -h
free -h

# Ver processos
ps aux | grep gunicorn
ps aux | grep nginx
```

## 🔄 Atualizações

### 1. Atualização Automática

```bash
# Usar script de gerenciamento
erp-manage update
```

### 2. Atualização Manual

```bash
# Parar serviços
erp-manage stop

# Fazer backup
erp-manage backup

# Atualizar código
cd /opt/erp-system
sudo -u erp git pull origin main

# Atualizar dependências
sudo -u erp /opt/erp-system/venv/bin/pip install -r requirements.txt

# Executar migrações
sudo -u erp /opt/erp-system/venv/bin/flask db upgrade

# Reiniciar serviços
erp-manage start
```

## 🆘 Troubleshooting

### Problemas Comuns

**1. Serviço não inicia**
```bash
# Verificar logs
erp-manage logs
sudo journalctl -u supervisor -f

# Verificar permissões
ls -la /opt/erp-system/
sudo chown -R erp:erp /opt/erp-system/
```

**2. Erro 502 Bad Gateway**
```bash
# Verificar se o socket existe
ls -la /opt/erp-system/erp-system.sock

# Reiniciar serviços
erp-manage restart
```

**3. Erro de permissão**
```bash
# Corrigir permissões
sudo chown -R erp:erp /opt/erp-system/
sudo chmod -R 755 /opt/erp-system/
```

**4. Banco de dados corrompido**
```bash
# Restaurar backup
sudo -u erp cp /opt/erp-system/backups/erp_backup_YYYYMMDD_HHMMSS.db /opt/erp-system/instance/erp.db
erp-manage restart
```

## 📞 Suporte

Para problemas específicos:

1. Verificar logs: `erp-manage logs`
2. Verificar status: `erp-manage status`
3. Fazer backup antes de qualquer alteração
4. Documentar mudanças feitas

## 📝 Notas Importantes

- ✅ Sempre faça backup antes de atualizações
- ✅ Mantenha o sistema atualizado
- ✅ Monitore logs regularmente
- ✅ Configure alertas de monitoramento
- ✅ Teste em ambiente de desenvolvimento antes de produção
