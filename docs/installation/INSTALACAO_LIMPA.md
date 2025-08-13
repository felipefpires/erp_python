# 🧹 Instalação Limpa - Sistema ERP

Este guia explica como fazer uma **instalação limpa** do Sistema ERP, removendo completamente qualquer instalação anterior.

## ⚠️ ATENÇÃO

**Este processo irá REMOVER completamente o sistema atual e todos os dados!**

## 🚀 Instalação Limpa Automatizada

### **1. Baixar e Executar Script de Instalação Limpa**

```bash
# Conectar ao servidor
ssh usuario@seu-servidor.com

# Baixar script de instalação limpa
cd /tmp
wget https://raw.githubusercontent.com/felipefpires/erp_python/erp_python/scripts/deploy/clean-install.sh
chmod +x clean-install.sh

# Executar instalação limpa
./clean-install.sh https://github.com/felipefpires/erp_python.git
```

### **2. O que o Script Faz**

✅ **Faz backup automático do sistema atual**
✅ **Remove completamente o sistema anterior**
✅ **Remove Nginx e Supervisor antigos**
✅ **Remove usuário e diretórios**
✅ **Atualiza o sistema operacional**
✅ **Instala dependências limpas**
✅ **Baixa código atualizado do GitHub**
✅ **Configura tudo do zero**
✅ **Testa a aplicação**

## 🔧 Instalação Manual Limpa

Se preferir fazer manualmente:

### **1. Fazer Backup**

```bash
# Backup do sistema atual
sudo tar -czf /tmp/erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /opt/erp-system instance/ uploads/ .env
```

### **2. Remover Sistema Atual**

```bash
# Parar serviços
sudo systemctl stop nginx
sudo supervisorctl stop erp-system

# Remover configurações
sudo rm -f /etc/nginx/sites-enabled/*
sudo rm -f /etc/nginx/sites-available/erp-system
sudo rm -f /etc/supervisor/conf.d/erp-system.conf

# Remover diretórios
sudo rm -rf /opt/erp-system

# Remover usuário
sudo userdel -r erp

# Remover script de gerenciamento
sudo rm -f /usr/local/bin/erp-manage
```

### **3. Remover Nginx e Supervisor**

```bash
# Remover completamente
sudo apt remove --purge nginx nginx-common nginx-full supervisor -y
sudo apt autoremove -y
```

### **4. Instalar Dependências Limpas**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget net-tools
```

### **5. Baixar e Instalar Código**

```bash
# Baixar código
cd /tmp
git clone https://github.com/felipefpires/erp_python.git erp-system-temp

# Executar deploy
cd erp-system-temp
chmod +x scripts/deploy/deploy.sh
./scripts/deploy/deploy.sh https://github.com/felipefpires/erp_python.git
```

## 🔄 Restaurar Backup (Opcional)

Se você fez backup e quer restaurar os dados:

```bash
# Restaurar backup
sudo tar -xzf /tmp/erp_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/erp-system/

# Configurar permissões
sudo chown -R erp:erp /opt/erp-system/

# Reiniciar serviços
erp-manage restart
```

## ✅ Verificar Instalação

```bash
# Verificar status
erp-manage status

# Verificar saúde
erp-manage health

# Testar aplicação
curl http://localhost/health

# Ver logs
erp-manage logs
```

## 🎯 Resultado Esperado

Após a instalação limpa:

- ✅ **Sistema funcionando em http://IP_DO_SERVIDOR**
- ✅ **Nginx configurado corretamente**
- ✅ **Supervisor gerenciando a aplicação**
- ✅ **Script de gerenciamento disponível**
- ✅ **Backup automático configurado**

## 🆘 Troubleshooting

### **Se a instalação falhar:**

```bash
# Verificar logs
erp-manage logs

# Verificar status
erp-manage status

# Verificar configuração do Nginx
sudo nginx -t

# Reiniciar tudo
erp-manage restart
```

### **Se Nginx não carregar:**

```bash
# Verificar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

## 📝 Notas Importantes

- ✅ **Sempre faça backup antes da instalação limpa**
- ✅ **O script faz backup automático**
- ✅ **Instalação limpa resolve problemas de configuração**
- ✅ **Sistema fica 100% funcional após instalação**

---

**🎉 Sistema ERP instalado do zero e pronto para uso!**
