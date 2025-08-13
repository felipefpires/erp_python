# 🚀 Guia de Deploy Automatizado - Sistema ERP

Este guia explica como fazer o deploy **100% automatizado** do Sistema ERP em um servidor Ubuntu.

## 📋 Pré-requisitos

- Servidor Ubuntu 20.04+ ou similar
- Acesso SSH com privilégios sudo
- Repositório GitHub configurado
- Conectividade com internet

## 🚀 Deploy Automatizado (Recomendado)

### 1. **Instalação Inicial (Primeira Vez)**

```bash
# Conectar ao servidor
ssh usuario@seu-servidor.com

# Baixar e executar script de instalação
cd /tmp
wget https://raw.githubusercontent.com/seu-usuario/erp-project/main/scripts/deploy/install.sh
chmod +x install.sh
./install.sh https://github.com/seu-usuario/erp-project.git
```

**OU se você já tem o código no servidor:**

```bash
cd /caminho/para/erp-project
chmod +x scripts/deploy/install.sh
./scripts/deploy/install.sh https://github.com/seu-usuario/erp-project.git
```

### 2. **O que o Script Faz Automaticamente**

✅ **Instala todas as dependências do sistema**
✅ **Cria usuário `erp` para a aplicação**
✅ **Configura ambiente virtual Python**
✅ **Instala dependências Python**
✅ **Configura Nginx como proxy reverso**
✅ **Configura Supervisor para gerenciar processos**
✅ **Inicializa banco de dados**
✅ **Inicia todos os serviços**
✅ **Testa a aplicação**
✅ **Instala script de gerenciamento**

### 3. **Acesso ao Sistema**

Após a instalação, acesse:
```
http://IP_DO_SERVIDOR
```

## 🔧 Gerenciamento do Sistema

### Script de Gerenciamento

O sistema instala automaticamente o comando `erp-manage`:

```bash
# Ver status do sistema
erp-manage status

# Ver logs em tempo real
erp-manage logs

# Verificar saúde do sistema
erp-manage health

# Reiniciar o sistema
erp-manage restart

# Fazer backup
erp-manage backup

# Atualizar do GitHub
erp-manage update-git

# Limpar logs e backups antigos
erp-manage clean

# Ver ajuda completa
erp-manage help
```

## 🔄 Atualizações Automáticas

### 1. **Atualização Manual**

```bash
# Atualizar do GitHub
erp-manage update-git
```

### 2. **Atualização Automática (Cron)**

Para atualizações automáticas diárias:

```bash
# Editar crontab
crontab -e

# Adicionar linha para atualização diária às 3h da manhã
0 3 * * * /opt/erp-system/scripts/deploy/auto-update.sh https://github.com/seu-usuario/erp-project.git
```

### 3. **Atualização Semanal**

```bash
# Atualização semanal aos domingos às 2h da manhã
0 2 * * 0 /opt/erp-system/scripts/deploy/auto-update.sh https://github.com/seu-usuario/erp-project.git
```

## 📊 Monitoramento

### 1. **Verificar Status**

```bash
# Status completo
erp-manage status

# Saúde do sistema
erp-manage health

# Logs em tempo real
erp-manage logs
```

### 2. **Logs Importantes**

```bash
# Logs da aplicação
tail -f /opt/erp-system/logs/access.log
tail -f /opt/erp-system/logs/error.log

# Logs do Nginx
sudo tail -f /var/log/nginx/erp_access.log
sudo tail -f /var/log/nginx/erp_error.log

# Logs de atualização automática
tail -f /opt/erp-system/logs/auto-update.log
```

## 🔒 Segurança

### 1. **Firewall**

```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. **SSL/HTTPS (Opcional)**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovar automaticamente
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🆘 Troubleshooting

### Problemas Comuns

**1. Aplicação não responde**
```bash
# Verificar status
erp-manage status

# Verificar logs
erp-manage logs

# Reiniciar
erp-manage restart
```

**2. Erro de permissão**
```bash
# Corrigir permissões
sudo chown -R erp:erp /opt/erp-system/
sudo chmod -R 755 /opt/erp-system/
```

**3. Atualização falhou**
```bash
# Verificar logs de atualização
tail -f /opt/erp-system/logs/auto-update.log

# Restaurar backup manualmente
erp-manage backup
```

**4. Nginx não carrega**
```bash
# Verificar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## 📁 Estrutura de Diretórios

```
/opt/erp-system/
├── app/                    # Código da aplicação
├── venv/                   # Ambiente virtual Python
├── instance/               # Banco de dados
├── uploads/                # Arquivos enviados
├── logs/                   # Logs da aplicação
├── backups/                # Backups automáticos
├── .env                    # Variáveis de ambiente
└── erp-system.sock         # Socket Unix
```

## 🔄 Backup e Restauração

### Backup Automático

O sistema faz backup automático antes de cada atualização:

```bash
# Verificar backups
ls -la /opt/erp-system/backups/

# Fazer backup manual
erp-manage backup
```

### Restauração Manual

```bash
# Parar serviços
erp-manage stop

# Restaurar backup
sudo tar -xzf /opt/erp-system/backups/erp_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/erp-system/

# Reiniciar
erp-manage start
```

## 📞 Comandos Úteis

```bash
# Ver IP do servidor
hostname -I

# Ver uso de disco
df -h

# Ver uso de memória
free -h

# Ver processos
ps aux | grep erp

# Ver portas em uso
sudo netstat -tlnp
```

## 🎯 Fluxo de Trabalho Recomendado

1. **Desenvolvimento**: Faça alterações no código
2. **Teste**: Teste localmente
3. **Commit**: Faça commit e push para GitHub
4. **Deploy**: Execute `erp-manage update-git` no servidor
5. **Verificação**: Use `erp-manage health` para confirmar

## 📝 Notas Importantes

- ✅ **Sempre faça backup antes de atualizações**
- ✅ **Monitore logs regularmente**
- ✅ **Configure alertas de monitoramento**
- ✅ **Mantenha o sistema atualizado**
- ✅ **Teste em ambiente de desenvolvimento antes de produção**

## 🚀 Próximos Passos

Após o deploy:

1. **Configurar domínio** (se necessário)
2. **Configurar SSL/HTTPS** (recomendado)
3. **Configurar backup externo** (recomendado)
4. **Configurar monitoramento** (recomendado)
5. **Configurar atualizações automáticas** (recomendado)

---

**🎉 Sistema ERP pronto para uso!**
