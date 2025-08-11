#!/bin/bash

# 📤 Script de Upload para Proxmox
# Este script facilita o upload do projeto para VM Ubuntu no Proxmox

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    📤 UPLOAD PARA PROXMOX                    ║"
    echo "║                                                              ║"
    echo "║  Este script facilita o upload do Sistema ERP para          ║"
    echo "║  uma VM Ubuntu no Proxmox                                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar se estamos no diretório correto
check_project() {
    if [ ! -f "requirements.txt" ]; then
        error "Execute este script no diretório do projeto (onde está requirements.txt)"
    fi
    
    if [ ! -f "install_proxmox.sh" ]; then
        error "Arquivo install_proxmox.sh não encontrado"
    fi
    
    success "Projeto verificado!"
}

# Compactar projeto
create_archive() {
    log "Criando arquivo compactado..."
    
    # Remover arquivos desnecessários
    rm -f erp-system.tar.gz
    
    # Criar arquivo compactado
    tar -czf erp-system.tar.gz \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='instance' \
        --exclude='venv' \
        --exclude='logs' \
        --exclude='backups' \
        --exclude='uploads' \
        .
    
    success "Arquivo erp-system.tar.gz criado!"
    info "Tamanho: $(du -h erp-system.tar.gz | cut -f1)"
}

# Mostrar opções de upload
show_upload_options() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    📤 OPÇÕES DE UPLOAD                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}Escolha uma opção:${NC}"
    echo "1. 📁 Upload via Interface Web do Proxmox (Recomendado)"
    echo "2. 🌐 Servidor Web Temporário"
    echo "3. 📋 Instruções Manuais"
    echo "4. ❌ Cancelar"
    echo ""
}

# Opção 1: Upload via Interface Web
upload_via_web() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    📁 UPLOAD VIA INTERFACE WEB               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}Passos:${NC}"
    echo "1. Acesse a interface web do Proxmox"
    echo "2. Vá para sua VM Ubuntu"
    echo "3. Clique em 'Hardware' → 'CD/DVD Drive'"
    echo "4. Selecione 'Upload' e escolha o arquivo 'erp-system.tar.gz'"
    echo "5. Aguarde o upload completar"
    echo ""
    
    echo -e "${YELLOW}Após o upload, execute na VM:${NC}"
    echo "sudo mount /dev/sr0 /mnt"
    echo "sudo cp /mnt/erp-system.tar.gz /tmp/"
    echo "sudo umount /mnt"
    echo "cd /tmp"
    echo "tar -xzf erp-system.tar.gz"
    echo "cd erp-system"
    echo "chmod +x install_proxmox.sh"
    echo "./install_proxmox.sh"
    echo ""
    
    read -p "Pressione Enter para continuar..."
}

# Opção 2: Servidor Web Temporário
upload_via_web_server() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🌐 SERVIDOR WEB TEMPORÁRIO                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Obter IP local
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    echo -e "${GREEN}Iniciando servidor web...${NC}"
    echo "IP local: $LOCAL_IP"
    echo "Porta: 8000"
    echo ""
    
    echo -e "${YELLOW}Na VM Ubuntu, execute:${NC}"
    echo "wget http://$LOCAL_IP:8000/erp-system.tar.gz"
    echo "tar -xzf erp-system.tar.gz"
    echo "cd erp-system"
    echo "chmod +x install_proxmox.sh"
    echo "./install_proxmox.sh"
    echo ""
    
    echo -e "${BLUE}Iniciando servidor web...${NC}"
    echo "Pressione Ctrl+C para parar o servidor"
    echo ""
    
    # Iniciar servidor web
    python3 -m http.server 8000
}

# Opção 3: Instruções Manuais
show_manual_instructions() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    📋 INSTRUÇÕES MANUAIS                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}Método 1: SCP (se tiver SSH configurado)${NC}"
    echo "scp erp-system.tar.gz usuario@IP_DA_VM:/tmp/"
    echo ""
    
    echo -e "${GREEN}Método 2: USB/CD${NC}"
    echo "1. Copie erp-system.tar.gz para um pendrive"
    echo "2. Monte o pendrive na VM"
    echo "3. Copie o arquivo para /tmp/"
    echo ""
    
    echo -e "${GREEN}Método 3: Cloud Storage${NC}"
    echo "1. Faça upload para Google Drive, Dropbox, etc."
    echo "2. Baixe na VM usando wget ou curl"
    echo ""
    
    echo -e "${YELLOW}Após transferir o arquivo:${NC}"
    echo "cd /tmp"
    echo "tar -xzf erp-system.tar.gz"
    echo "cd erp-system"
    echo "chmod +x install_proxmox.sh"
    echo "./install_proxmox.sh"
    echo ""
    
    read -p "Pressione Enter para continuar..."
}

# Função principal
main() {
    show_banner
    
    # Verificar projeto
    check_project
    
    # Criar arquivo compactado
    create_archive
    
    # Mostrar opções
    while true; do
        show_upload_options
        read -p "Escolha uma opção (1-4): " choice
        
        case $choice in
            1)
                upload_via_web
                break
                ;;
            2)
                upload_via_web_server
                break
                ;;
            3)
                show_manual_instructions
                break
                ;;
            4)
                echo "Operação cancelada."
                exit 0
                ;;
            *)
                echo "Opção inválida. Tente novamente."
                ;;
        esac
    done
}

# Executar função principal
main "$@"

