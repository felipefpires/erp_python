#!/bin/bash

# 🚀 Helper Script para Instalação do Sistema ERP no Proxmox
# Este script automatiza todo o processo de instalação

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="erp-system"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="erp-system"
USER_NAME="erp"
BACKUP_DIR="$APP_DIR/backups"
LOG_DIR="$APP_DIR/logs"

# Funções de log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] ❌ $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[AVISO] ⚠️ $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] ℹ️ $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCESSO] 🎉 $1${NC}"
}

# Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 SISTEMA ERP                            ║"
    echo "║              Helper Script para Proxmox                     ║"
    echo "║                                                              ║"
    echo "║  Este script irá instalar automaticamente o Sistema ERP     ║"
    echo "║  em sua VM Ubuntu no Proxmox                                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar sistema
check_system() {
    log "Verificando sistema..."
    
    # Verificar se é Ubuntu
    if ! grep -q "Ubuntu" /etc/os-release; then
        error "Este script é destinado para Ubuntu. Sistema detectado: $(cat /etc/os-release | grep PRETTY_NAME)"
    fi
    
    # Verificar se está rodando como root
    if [[ $EUID -eq 0 ]]; then
        error "Este script não deve ser executado como root. Use um usuário normal com sudo."
    fi
    
    # Verificar se tem sudo
    if ! sudo -n true 2>/dev/null; then
        error "Este usuário não tem privilégios sudo ou não está configurado para NOPASSWD"
    fi
    
    success "Sistema verificado com sucesso!"
}

# Atualizar sistema
update_system() {
    log "Atualizando sistema..."
    sudo apt update
    sudo apt upgrade -y
    success "Sistema atualizado!"
}

# Instalar dependências
install_dependencies() {
    log "Instalando dependências do sistema..."
    
    # Lista de pacotes necessários
    PACKAGES=(
        "python3"
        "python3-pip"
        "python3-venv"
        "nginx"
        "supervisor"
        "git"
        "curl"
        "wget"
        "ufw"
        "htop"
        "tree"
    )
    
    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            info "Instalando $package..."
            sudo apt install -y "$package"
        else
            info "$package já está instalado"
        fi
    done
    
    success "Dependências instaladas!"
}

# Criar usuário e diretórios
setup_user_and_dirs() {
    log "Configurando usuário e diretórios..."
    
    # Criar usuário se não existir
    if ! id "$USER_NAME" &>/dev/null; then
        sudo useradd -r -s /bin/bash -d $APP_DIR $USER_NAME
        info "Usuário $USER_NAME criado"
    else
        info "Usuário $USER_NAME já existe"
    fi
    
    # Criar diretórios
    sudo mkdir -p $APP_DIR
    sudo mkdir -p $BACKUP_DIR
    sudo mkdir -p $LOG_DIR
    
    # Definir permissões
    sudo chown $USER_NAME:$USER_NAME $APP_DIR
    sudo chown $USER_NAME:$USER_NAME $BACKUP_DIR
    sudo chown $USER_NAME:$USER_NAME $LOG_DIR
    
    success "Usuário e diretórios configurados!"
}

# Copiar código da aplicação
copy_application() {
    log "Copiando código da aplicação..."
    
    # Verificar se estamos no diretório correto
    if [ ! -f "requirements.txt" ]; then
        error "Execute este script no diretório do projeto (onde está requirements.txt)"
    fi
    
    # Fazer backup se já existir instalação
    if [ -d "$APP_DIR/app" ]; then
        warning "Instalação anterior detectada. Fazendo backup..."
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        sudo cp -r $APP_DIR $BACKUP_DIR/$BACKUP_NAME
        info "Backup criado: $BACKUP_DIR/$BACKUP_NAME"
    fi
    
    # Copiar código
    sudo cp -r . $APP_DIR/
    sudo chown -R $USER_NAME:$USER_NAME $APP_DIR
    
    success "Código copiado com sucesso!"
}

# Configurar ambiente Python
setup_python_env() {
    log "Configurando ambiente Python..."
    
    # Criar ambiente virtual
    sudo -u $USER_NAME python3 -m venv $VENV_DIR
    
    # Ativar e instalar dependências
    sudo -u $USER_NAME $VENV_DIR/bin/pip install --upgrade pip
    sudo -u $USER_NAME $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt
    
    success "Ambiente Python configurado!"
}

# Configurar variáveis de ambiente
setup_environment() {
    log "Configurando variáveis de ambiente..."
    
    # Gerar chave secreta
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Criar arquivo .env
    sudo -u $USER_NAME tee $APP_DIR/.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=sqlite:///$APP_DIR/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
HOST=0.0.0.0
PORT=5000
EOF
    
    success "Variáveis de ambiente configuradas!"
}

# Configurar Supervisor
setup_supervisor() {
    log "Configurando Supervisor..."
    
    sudo tee /etc/supervisor/conf.d/$SERVICE_NAME.conf > /dev/null <<EOF
[program:$SERVICE_NAME]
command=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$SERVICE_NAME.sock --access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log --log-level info wsgi:app
directory=$APP_DIR
user=$USER_NAME
autostart=true
autorestart=true
stderr_logfile=$LOG_DIR/supervisor_err.log
stdout_logfile=$LOG_DIR/supervisor_out.log
environment=HOME="$APP_DIR",USER="$USER_NAME"
EOF
    
    success "Supervisor configurado!"
}

# Configurar Nginx
setup_nginx() {
    log "Configurando Nginx..."
    
    # Backup configuração original
    if [ -f /etc/nginx/sites-enabled/default ]; then
        sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
    fi
    
    # Criar configuração
    sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Logs
    access_log /var/log/nginx/erp_access.log;
    error_log /var/log/nginx/erp_error.log;

    # Proxy para aplicação
    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$SERVICE_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Arquivos estáticos
    location /static {
        alias $APP_DIR/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads {
        alias $APP_DIR/uploads;
        expires 30d;
    }

    # Segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF
    
    # Ativar site
    sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    success "Nginx configurado!"
}

# Configurar firewall
setup_firewall() {
    log "Configurando firewall..."
    
    # Permitir SSH
    sudo ufw allow ssh
    
    # Permitir HTTP e HTTPS
    sudo ufw allow 'Nginx Full'
    
    # Ativar firewall
    echo "y" | sudo ufw enable
    
    success "Firewall configurado!"
}

# Inicializar banco de dados
init_database() {
    log "Inicializando banco de dados..."
    
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py
    
    success "Banco de dados inicializado!"
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    # Reiniciar Supervisor
    sudo systemctl restart supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start $SERVICE_NAME
    
    # Reiniciar Nginx
    sudo systemctl restart nginx
    
    # Aguardar um pouco
    sleep 3
    
    success "Serviços iniciados!"
}

# Criar script de gerenciamento
create_management_script() {
    log "Criando script de gerenciamento..."
    
    sudo tee /usr/local/bin/erp-manage > /dev/null <<'EOF'
#!/bin/bash

APP_DIR="/opt/erp-system"
SERVICE_NAME="erp-system"
LOG_DIR="$APP_DIR/logs"
BACKUP_DIR="$APP_DIR/backups"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

case "$1" in
    start)
        log "Iniciando sistema..."
        sudo supervisorctl start $SERVICE_NAME
        sudo systemctl start nginx
        log "Sistema iniciado!"
        ;;
    stop)
        log "Parando sistema..."
        sudo supervisorctl stop $SERVICE_NAME
        sudo systemctl stop nginx
        log "Sistema parado!"
        ;;
    restart)
        log "Reiniciando sistema..."
        sudo supervisorctl restart $SERVICE_NAME
        sudo systemctl reload nginx
        log "Sistema reiniciado!"
        ;;
    status)
        echo -e "${BLUE}=== Status do Sistema ===${NC}"
        echo -e "${GREEN}Supervisor:${NC}"
        sudo supervisorctl status $SERVICE_NAME
        echo -e "${GREEN}Nginx:${NC}"
        sudo systemctl status nginx --no-pager -l
        echo -e "${GREEN}Portas:${NC}"
        sudo netstat -tlnp | grep -E ':(80|443|5000)'
        ;;
    logs)
        echo -e "${BLUE}=== Logs do Sistema ===${NC}"
        echo -e "${GREEN}Logs de Erro:${NC}"
        tail -20 $LOG_DIR/error.log
        echo -e "${GREEN}Logs de Acesso:${NC}"
        tail -20 $LOG_DIR/access.log
        ;;
    logs-follow)
        echo -e "${BLUE}=== Acompanhando Logs ===${NC}"
        tail -f $LOG_DIR/error.log $LOG_DIR/access.log
        ;;
    backup)
        BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).db"
        log "Criando backup: $BACKUP_FILE"
        sudo -u erp cp $APP_DIR/instance/erp.db $BACKUP_DIR/$BACKUP_FILE
        log "Backup criado: $BACKUP_FILE"
        ;;
    backup-list)
        echo -e "${BLUE}=== Backups Disponíveis ===${NC}"
        ls -la $BACKUP_DIR/*.db 2>/dev/null || echo "Nenhum backup encontrado"
        ;;
    update)
        log "Atualizando sistema..."
        cd $APP_DIR
        sudo -u erp git pull origin main 2>/dev/null || info "Git não configurado ou não há atualizações"
        sudo -u erp $APP_DIR/venv/bin/pip install -r requirements.txt
        sudo supervisorctl restart $SERVICE_NAME
        log "Sistema atualizado!"
        ;;
    info)
        echo -e "${BLUE}=== Informações do Sistema ===${NC}"
        echo -e "${GREEN}Diretório:${NC} $APP_DIR"
        echo -e "${GREEN}Usuário:${NC} $USER"
        echo -e "${GREEN}IP:${NC} $(hostname -I | awk '{print $1}')"
        echo -e "${GREEN}Versão Python:${NC} $(python3 --version)"
        echo -e "${GREEN}Uso de Disco:${NC}"
        df -h $APP_DIR
        echo -e "${GREEN}Uso de Memória:${NC}"
        free -h
        ;;
    *)
        echo -e "${BLUE}=== Sistema ERP - Comandos Disponíveis ===${NC}"
        echo "  start        - Iniciar sistema"
        echo "  stop         - Parar sistema"
        echo "  restart      - Reiniciar sistema"
        echo "  status       - Ver status"
        echo "  logs         - Ver logs recentes"
        echo "  logs-follow  - Acompanhar logs em tempo real"
        echo "  backup       - Criar backup do banco"
        echo "  backup-list  - Listar backups"
        echo "  update       - Atualizar sistema"
        echo "  info         - Informações do sistema"
        exit 1
        ;;
esac
EOF
    
    sudo chmod +x /usr/local/bin/erp-manage
    success "Script de gerenciamento criado!"
}

# Verificar instalação
verify_installation() {
    log "Verificando instalação..."
    
    # Verificar se os serviços estão rodando
    if sudo supervisorctl status $SERVICE_NAME | grep -q "RUNNING"; then
        success "Supervisor: OK"
    else
        error "Supervisor não está rodando"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        success "Nginx: OK"
    else
        error "Nginx não está rodando"
    fi
    
    # Verificar se o socket existe
    if [ -S "$APP_DIR/$SERVICE_NAME.sock" ]; then
        success "Socket: OK"
    else
        error "Socket não encontrado"
    fi
    
    # Testar acesso local
    if curl -s http://localhost > /dev/null; then
        success "Acesso local: OK"
    else
        warning "Acesso local falhou - verifique os logs"
    fi
    
    success "Verificação concluída!"
}

# Mostrar informações finais
show_final_info() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 INSTALAÇÃO CONCLUÍDA!                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}✅ Sistema ERP instalado com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Acesso:${NC}"
    echo "   Local: http://$(hostname -I | awk '{print $1}')"
    echo "   Rede: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo -e "${BLUE}📁 Diretórios:${NC}"
    echo "   Aplicação: $APP_DIR"
    echo "   Logs: $LOG_DIR"
    echo "   Backups: $BACKUP_DIR"
    echo ""
    echo -e "${BLUE}🔧 Comandos de Gerenciamento:${NC}"
    echo "   erp-manage status    # Ver status"
    echo "   erp-manage logs      # Ver logs"
    echo "   erp-manage restart   # Reiniciar"
    echo "   erp-manage backup    # Fazer backup"
    echo "   erp-manage info      # Informações do sistema"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
    echo "   - Faça backup regularmente"
    echo "   - Monitore os logs"
    echo "   - Mantenha o sistema atualizado"
    echo ""
    echo -e "${GREEN}🚀 Para começar:${NC}"
    echo "   Acesse http://$(hostname -I | awk '{print $1}') no seu navegador"
    echo ""
}

# Função principal
main() {
    show_banner
    
    echo -e "${YELLOW}Este script irá instalar o Sistema ERP no Proxmox.${NC}"
    echo -e "${YELLOW}Certifique-se de que:${NC}"
    echo "  ✅ Você está em uma VM Ubuntu"
    echo "  ✅ Tem acesso sudo"
    echo "  ✅ Está no diretório do projeto"
    echo ""
    
    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Instalação cancelada."
        exit 0
    fi
    
    # Executar etapas
    check_system
    update_system
    install_dependencies
    setup_user_and_dirs
    copy_application
    setup_python_env
    setup_environment
    setup_supervisor
    setup_nginx
    setup_firewall
    init_database
    start_services
    create_management_script
    verify_installation
    show_final_info
}

# Executar função principal
main "$@"

