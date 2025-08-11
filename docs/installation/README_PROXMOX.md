# 🚀 Sistema ERP - Instalação no Proxmox

Este guia explica como instalar o Sistema ERP em uma VM Ubuntu no Proxmox usando scripts automatizados.

## 📋 Pré-requisitos

- **Proxmox VE** configurado e funcionando
- **VM Ubuntu** (20.04 LTS ou superior) criada
- Acesso à interface web do Proxmox
- Acesso à VM via console web ou VNC

## 🎯 Opções de Instalação

### **Opção 1: Instalação Automática (Recomendada)**

#### **Passo 1: Preparar o Projeto**
No seu computador local:

```bash
# 1. Navegar para o diretório do projeto
cd "caminho/para/erp-project"

# 2. Executar script de upload
chmod +x proxmox_upload.sh
./proxmox_upload.sh
```

#### **Passo 2: Upload para Proxmox**
O script oferecerá 3 opções:

1. **📁 Upload via Interface Web (Recomendado)**
   - Acesse a interface web do Proxmox
   - Vá para sua VM Ubuntu
   - Clique em "Hardware" → "CD/DVD Drive"
   - Selecione "Upload" e escolha `erp-system.tar.gz`

2. **🌐 Servidor Web Temporário**
   - O script iniciará um servidor web local
   - Na VM, use `wget` para baixar o arquivo

3. **📋 Instruções Manuais**
   - Para casos especiais (SCP, USB, etc.)

#### **Passo 3: Instalar na VM**
Na VM Ubuntu:

```bash
# 1. Montar CD virtual (se usado upload via interface)
sudo mount /dev/sr0 /mnt
sudo cp /mnt/erp-system.tar.gz /tmp/
sudo umount /mnt

# 2. Extrair projeto
cd /tmp
tar -xzf erp-system.tar.gz
cd erp-system

# 3. Executar instalação automática
chmod +x install_proxmox.sh
./install_proxmox.sh
```

### **Opção 2: Instalação Manual**

Se preferir instalar manualmente, siga o guia em `deploy_proxmox.md`.

## 🔧 O que o Script Faz

O script `install_proxmox.sh` automatiza:

- ✅ **Verificação do sistema** (Ubuntu, permissões)
- ✅ **Atualização do sistema**
- ✅ **Instalação de dependências** (Python, Nginx, Supervisor, etc.)
- ✅ **Criação de usuário** dedicado (`erp`)
- ✅ **Configuração do ambiente Python** (venv, dependências)
- ✅ **Configuração do banco de dados** (SQLite)
- ✅ **Configuração do Nginx** (proxy reverso)
- ✅ **Configuração do Supervisor** (gerenciamento de processos)
- ✅ **Configuração do firewall** (UFW)
- ✅ **Criação de script de gerenciamento** (`erp-manage`)

## 🌐 Acesso ao Sistema

Após a instalação, o sistema estará disponível em:

- **Local:** `http://IP_DA_VM`
- **Rede:** `http://IP_DA_VM` (se configurado)

## 🔧 Gerenciamento do Sistema

O script cria um comando `erp-manage` para facilitar o gerenciamento:

```bash
# Ver status do sistema
erp-manage status

# Ver logs
erp-manage logs

# Acompanhar logs em tempo real
erp-manage logs-follow

# Reiniciar sistema
erp-manage restart

# Fazer backup do banco
erp-manage backup

# Listar backups
erp-manage backup-list

# Atualizar sistema
erp-manage update

# Informações do sistema
erp-manage info
```

## 📁 Estrutura de Diretórios

```
/opt/erp-system/
├── app/                    # Código da aplicação
├── venv/                   # Ambiente virtual Python
├── instance/               # Banco de dados SQLite
├── uploads/                # Arquivos enviados
├── logs/                   # Logs da aplicação
├── backups/                # Backups do banco
├── .env                    # Variáveis de ambiente
└── erp-system.sock         # Socket do Gunicorn
```

## 🔒 Segurança

O script configura automaticamente:

- ✅ **Firewall UFW** (SSH, HTTP, HTTPS)
- ✅ **Usuário dedicado** (sem privilégios root)
- ✅ **Headers de segurança** no Nginx
- ✅ **Permissões restritas** nos arquivos

## 📊 Monitoramento

### **Logs Importantes**

```bash
# Logs da aplicação
tail -f /opt/erp-system/logs/error.log
tail -f /opt/erp-system/logs/access.log

# Logs do Nginx
sudo tail -f /var/log/nginx/erp_error.log
sudo tail -f /var/log/nginx/erp_access.log

# Logs do Supervisor
sudo tail -f /opt/erp-system/logs/supervisor_err.log
```

### **Comandos de Monitoramento**

```bash
# Status dos serviços
sudo systemctl status nginx
sudo supervisorctl status erp-system

# Uso de recursos
htop
df -h
free -h

# Portas em uso
sudo netstat -tlnp | grep -E ':(80|443|5000)'
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

**4. Firewall bloqueando**
```bash
# Verificar status do firewall
sudo ufw status

# Permitir portas necessárias
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### **Logs de Debug**

```bash
# Testar aplicação diretamente
cd /opt/erp-system
sudo -u erp ./venv/bin/python app.py

# Testar Nginx
sudo nginx -t

# Testar Supervisor
sudo supervisorctl reread
sudo supervisorctl update
```

## 🔄 Atualizações

### **Atualização Automática**
```bash
# Atualizar sistema
erp-manage update
```

### **Atualização Manual**
```bash
# 1. Fazer backup
erp-manage backup

# 2. Atualizar código
cd /opt/erp-system
sudo -u erp git pull origin main

# 3. Atualizar dependências
sudo -u erp ./venv/bin/pip install -r requirements.txt

# 4. Reiniciar
erp-manage restart
```

## 📝 Notas Importantes

- ✅ **Sempre faça backup** antes de atualizações
- ✅ **Monitore logs** regularmente
- ✅ **Mantenha o sistema atualizado**
- ✅ **Use o script `erp-manage`** para gerenciamento
- ✅ **Teste em ambiente de desenvolvimento** antes de produção

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs:** `erp-manage logs`
2. **Verifique o status:** `erp-manage status`
3. **Consulte a documentação:** `README.md`
4. **Verifique o troubleshooting** acima

## 📞 Contato

Para suporte adicional, consulte a documentação principal do projeto ou entre em contato com a equipe de desenvolvimento.

