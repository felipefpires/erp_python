# 🖥️ Instalação no Servidor Ubuntu

Este guia explica como instalar o Sistema ERP em um servidor Ubuntu dedicado.

## 📋 Pré-requisitos

- **Servidor Ubuntu 20.04+ ou Debian 11+**
- **Acesso root ao servidor**
- **Repositório GitHub do projeto**
- **Domínio configurado** (opcional, para SSL)

## 🚀 Instalação Rápida

### 1. Conectar ao Servidor

```bash
# Conectar via SSH
ssh root@SEU_SERVIDOR_IP
```

### 2. Baixar e Executar Instalador

```bash
# Baixar o instalador
wget https://raw.githubusercontent.com/felipefpires/erp_python/main/scripts/deploy/install_server.sh

# Tornar executável
chmod +x install_server.sh

# Executar instalação
./install_server.sh
```

O script irá:
- ✅ Instalar todas as dependências do sistema
- ✅ Configurar ambiente Python
- ✅ Criar usuário dedicado (erp)
- ✅ Clonar seu repositório
- ✅ Configurar Nginx como proxy reverso
- ✅ Configurar systemd service
- ✅ Configurar firewall
- ✅ Configurar backup automático
- ✅ Inicializar banco de dados

## 🔧 Configuração Manual (Alternativa)

Se preferir fazer manualmente:

### 1. Atualizar Sistema

```bash
apt update && apt upgrade -y
```

### 2. Instalar Dependências

```bash
apt install -y python3 python3-pip python3-venv git nginx supervisor
```

### 3. Criar Usuário

```bash
useradd -m -s /bin/bash erp
```

### 4. Clonar Repositório

```bash
cd /opt
git clone https://github.com/felipefpires/erp_python.git erp-system
chown -R erp:erp /opt/erp-system
```

### 5. Configurar Ambiente Python

```bash
cd /opt/erp-system
sudo -u erp python3 -m venv venv
sudo -u erp ./venv/bin/pip install -r requirements.txt
```

### 6. Configurar Aplicação

```bash
# Criar arquivo .env
cat > /opt/erp-system/.env << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:////opt/erp-system/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
EOF

chown erp:erp /opt/erp-system/.env

# Inicializar banco de dados
sudo -u erp ./venv/bin/python init_db.py
```

### 7. Configurar Systemd

```bash
cat > /etc/systemd/system/erp-system.service << EOF
[Unit]
Description=ERP System
After=network.target

[Service]
Type=simple
User=erp
Group=erp
WorkingDirectory=/opt/erp-system
Environment=PATH=/opt/erp-system/venv/bin
ExecStart=/opt/erp-system/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable erp-system
systemctl start erp-system
```

### 8. Configurar Nginx

```bash
cat > /etc/nginx/sites-available/erp-system << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /opt/erp-system/static;
    }
}
EOF

ln -sf /etc/nginx/sites-available/erp-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
```

### 9. Configurar Firewall

```bash
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable
```

## 🔑 Configurar SSH para GitHub Actions

### 1. Gerar Chave SSH

```bash
# No servidor
ssh-keygen -t rsa -b 4096 -C "erp@seudominio.com"
```

### 2. Mostrar Chave Pública

```bash
cat ~/.ssh/id_rsa.pub
```

### 3. Mostrar Chave Privada (para GitHub Secrets)

```bash
cat ~/.ssh/id_rsa
```

## ⚙️ Configurar GitHub Secrets

No seu repositório GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

- `SERVER_HOST`: IP do seu servidor
- `SERVER_USER`: erp
- `SERVER_SSH_KEY`: Conteúdo da chave privada SSH (todo o conteúdo do arquivo id_rsa)
- `SERVER_PORT`: 22

## 🧪 Testar Instalação

### 1. Verificar Status

```bash
# Ver status do serviço
systemctl status erp-system

# Ver status do Nginx
systemctl status nginx

# Ver logs
journalctl -u erp-system -f
```

### 2. Testar Acesso

```bash
# Testar localmente
curl http://localhost

# Verificar portas
netstat -tlnp | grep -E ':(80|5000)'
```

### 3. Acessar via Navegador

Acesse: `http://SEU_SERVIDOR_IP`

- **Usuário**: admin
- **Senha**: admin123

## 🔒 Configurar SSL (Opcional)

Para configurar HTTPS:

```bash
# Executar script SSL
sudo /opt/erp-system/scripts/deploy/ssl_setup.sh
```

## 🛠️ Comandos de Gerenciamento

Após a instalação, você pode usar:

```bash
# Ver status do sistema
erp-manage status

# Ver logs
erp-manage logs

# Reiniciar sistema
erp-manage restart

# Fazer backup
erp-manage backup

# Verificar saúde
erp-manage health

# Limpar logs
erp-manage clean
```

## 🔄 Deploy Automático

Após configurar os secrets no GitHub, faça push para o branch principal:

```bash
# No seu computador de desenvolvimento
git add .
git commit -m "Atualização"
git push origin main
```

O GitHub Actions irá automaticamente:
1. Conectar ao servidor
2. Fazer pull das mudanças
3. Atualizar dependências
4. Reiniciar o serviço

## 🚨 Troubleshooting

### Serviço não inicia

```bash
# Verificar logs
journalctl -u erp-system -n 50

# Verificar permissões
chown -R erp:erp /opt/erp-system

# Verificar configuração
systemctl status erp-system
```

### Nginx não funciona

```bash
# Testar configuração
nginx -t

# Verificar status
systemctl status nginx

# Verificar portas
netstat -tlnp | grep :80
```

### Banco de dados corrompido

```bash
# Restaurar backup
erp-manage restore /opt/backups/erp/ultimo_backup.db
```

## 📊 Monitoramento

### Logs em Tempo Real

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

## ✅ Checklist de Instalação

- [ ] Servidor Ubuntu configurado
- [ ] Script de instalação executado
- [ ] Serviço ERP funcionando
- [ ] Nginx funcionando
- [ ] Firewall configurado
- [ ] SSH key gerada
- [ ] GitHub secrets configurados
- [ ] Primeiro deploy testado
- [ ] SSL configurado (opcional)
- [ ] Backup funcionando

**🎉 Sistema pronto para produção!**
