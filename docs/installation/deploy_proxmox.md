# 🖥️ Deploy via Interface Proxmox

Este guia explica como fazer o deploy do Sistema ERP usando apenas a interface web do Proxmox.

## 📋 Pré-requisitos

- Acesso à interface web do Proxmox
- VM Ubuntu já criada e funcionando
- Acesso à VM via console web ou VNC

## 🚀 Passo a Passo

### **1. Preparar o Projeto**

No seu computador local:

```bash
# 1. Compactar o projeto
tar -czf erp-system.tar.gz .

# 2. O arquivo erp-system.tar.gz será enviado para o servidor
```

### **2. Acessar a VM Ubuntu**

1. **Acesse a interface do Proxmox**
2. **Vá para sua VM Ubuntu**
3. **Clique em "Console"** (ou use VNC)
4. **Faça login** com suas credenciais

### **3. Upload do Projeto**

**Opção A: Via Interface Web (Recomendado)**

1. **No Proxmox:**
   - Vá para a VM Ubuntu
   - Clique em "Hardware" → "CD/DVD Drive"
   - Selecione "Upload" e escolha o arquivo `erp-system.tar.gz`

2. **Na VM Ubuntu:**
   ```bash
   # Montar o CD virtual
   sudo mount /dev/sr0 /mnt
   
   # Copiar arquivo
   sudo cp /mnt/erp-system.tar.gz /tmp/
   
   # Desmontar
   sudo umount /mnt
   ```

**Opção B: Via Web Server Temporário**

1. **No seu computador local:**
   ```bash
   # Iniciar servidor web temporário
   python -m http.server 8000
   ```

2. **Na VM Ubuntu:**
   ```bash
   # Baixar via wget
   wget http://IP_DO_SEU_COMPUTADOR:8000/erp-system.tar.gz
   ```

### **4. Instalar Dependências**

Na VM Ubuntu:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget

# Verificar Python
python3 --version
```

### **5. Extrair e Configurar Projeto**

```bash
# Ir para diretório temporário
cd /tmp

# Extrair projeto
tar -xzf erp-system.tar.gz
cd erp-system

# Verificar arquivos
ls -la
```

### **6. Executar Deploy Manual**

Como não temos SSH, vamos executar os comandos manualmente:

```bash
# 1. Criar usuário para aplicação
sudo useradd -r -s /bin/bash -d /opt/erp-system erp

# 2. Criar diretório da aplicação
sudo mkdir -p /opt/erp-system
sudo chown erp:erp /opt/erp-system

# 3. Copiar código
sudo cp -r /tmp/erp-system/* /opt/erp-system/
sudo chown -R erp:erp /opt/erp-system

# 4. Criar ambiente virtual
sudo -u erp python3 -m venv /opt/erp-system/venv

# 5. Instalar dependências Python
sudo -u erp /opt/erp-system/venv/bin/pip install --upgrade pip
sudo -u erp /opt/erp-system/venv/bin/pip install -r /opt/erp-system/requirements.txt

# 6. Criar diretórios necessários
sudo -u erp mkdir -p /opt/erp-system/instance
sudo -u erp mkdir -p /opt/erp-system/uploads
sudo -u erp mkdir -p /opt/erp-system/logs
sudo -u erp mkdir -p /opt/erp-system/backups
```

### **7. Configurar Variáveis de Ambiente**

```bash
# Criar arquivo .env
sudo -u erp tee /opt/erp-system/.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:////opt/erp-system/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
EOF
```

### **8. Configurar Supervisor**

```bash
# Criar configuração do Supervisor
sudo tee /etc/supervisor/conf.d/erp-system.conf > /dev/null <<EOF
[program:erp-system]
command=/opt/erp-system/venv/bin/gunicorn --workers 3 --bind unix:/opt/erp-system/erp-system.sock --access-logfile /opt/erp-system/logs/access.log --error-logfile /opt/erp-system/logs/error.log wsgi:app
directory=/opt/erp-system
user=erp
autostart=true
autorestart=true
stderr_logfile=/opt/erp-system/logs/supervisor_err.log
stdout_logfile=/opt/erp-system/logs/supervisor_out.log
EOF
```

### **9. Configurar Nginx**

```bash
# Criar configuração do Nginx
sudo tee /etc/nginx/sites-available/erp-system > /dev/null <<EOF
server {
    listen 80;
    server_name _;

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
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/erp-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### **10. Inicializar Banco de Dados**

```bash
# Ir para diretório da aplicação
cd /opt/erp-system

# Executar script de inicialização
sudo -u erp /opt/erp-system/venv/bin/python init_db.py
```

### **11. Iniciar Serviços**

```bash
# Reiniciar Supervisor
sudo systemctl restart supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar aplicação
sudo supervisorctl start erp-system

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo supervisorctl status erp-system
sudo systemctl status nginx
```

### **12. Verificar Funcionamento**

```bash
# Verificar se está rodando
curl http://localhost

# Ver logs
tail -f /opt/erp-system/logs/error.log
```

## 🔧 Script de Gerenciamento Manual

Criar script para facilitar gerenciamento:

```bash
# Criar script de gerenciamento
sudo tee /usr/local/bin/erp-manage > /dev/null <<'EOF'
#!/bin/bash

APP_DIR="/opt/erp-system"
SERVICE_NAME="erp-system"

case "$1" in
    start)
        sudo supervisorctl start $SERVICE_NAME
        sudo systemctl start nginx
        echo "Sistema iniciado!"
        ;;
    stop)
        sudo supervisorctl stop $SERVICE_NAME
        sudo systemctl stop nginx
        echo "Sistema parado!"
        ;;
    restart)
        sudo supervisorctl restart $SERVICE_NAME
        sudo systemctl reload nginx
        echo "Sistema reiniciado!"
        ;;
    status)
        echo "=== Supervisor ==="
        sudo supervisorctl status $SERVICE_NAME
        echo "=== Nginx ==="
        sudo systemctl status nginx --no-pager -l
        ;;
    logs)
        echo "=== Logs de Erro ==="
        tail -20 $APP_DIR/logs/error.log
        echo "=== Logs de Acesso ==="
        tail -20 $APP_DIR/logs/access.log
        ;;
    backup)
        BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).db"
        sudo -u erp cp $APP_DIR/instance/erp.db $APP_DIR/backups/$BACKUP_FILE
        echo "Backup criado: $BACKUP_FILE"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|backup}"
        exit 1
        ;;
esac
EOF

# Tornar executável
sudo chmod +x /usr/local/bin/erp-manage
```

## 🌐 Acesso ao Sistema

Após o deploy, o sistema estará disponível em:

- **Local:** `http://IP_DA_VM`
- **Rede:** `http://IP_DA_VM` (se configurado)

## 🔒 Configuração de Rede

### **1. Verificar IP da VM**

```bash
# Ver IP da VM
ip addr show

# Ou
hostname -I
```

### **2. Configurar Firewall (Opcional)**

```bash
# Instalar UFW
sudo apt install ufw

# Permitir SSH e HTTP
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 📊 Monitoramento

### **Comandos Úteis**

```bash
# Ver status
erp-manage status

# Ver logs
erp-manage logs

# Fazer backup
erp-manage backup

# Reiniciar
erp-manage restart
```

### **Verificar Recursos**

```bash
# Uso de CPU e memória
htop

# Espaço em disco
df -h

# Processos
ps aux | grep gunicorn
ps aux | grep nginx
```

## 🆘 Troubleshooting

### **Problemas Comuns**

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

## 📝 Notas Importantes

- ✅ Sempre faça backup antes de atualizações
- ✅ Monitore logs regularmente
- ✅ Mantenha o sistema atualizado
- ✅ Use o script `erp-manage` para gerenciamento
- ✅ Teste em ambiente de desenvolvimento antes de produção

