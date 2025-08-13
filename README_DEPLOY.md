# 🚀 Sistema ERP - Deploy Automático

Este projeto inclui um sistema completo de deploy automático para o Sistema ERP, permitindo atualizações automáticas via GitHub Actions.

## 📋 Visão Geral

O sistema está configurado para:
- ✅ **Deploy automático** via GitHub Actions
- ✅ **Servidor dedicado** Ubuntu/Debian
- ✅ **Banco de dados protegido** em produção
- ✅ **Backup automático** diário
- ✅ **SSL/HTTPS** opcional
- ✅ **Monitoramento** completo

## 🖥️ Instalação no Servidor

### Passo 1: Conectar ao Servidor

```bash
ssh root@SEU_SERVIDOR_IP
```

### Passo 2: Executar Instalador

```bash
# Baixar o instalador
wget https://raw.githubusercontent.com/felipefpires/erp_python/main/scripts/deploy/install_server.sh

# Tornar executável
chmod +x install_server.sh

# Executar instalação
./install_server.sh
```

O script irá solicitar:
- URL do seu repositório GitHub
- Branch principal (main/master)

### Passo 3: Configurar SSH para GitHub Actions

```bash
# Gerar chave SSH
ssh-keygen -t rsa -b 4096 -C "erp@seudominio.com"

# Mostrar chave pública
cat ~/.ssh/id_rsa.pub

# Mostrar chave privada (para GitHub Secrets)
cat ~/.ssh/id_rsa
```

### Passo 4: Configurar GitHub Secrets

No seu repositório GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

- `SERVER_HOST`: IP do seu servidor
- `SERVER_USER`: erp
- `SERVER_SSH_KEY`: Conteúdo da chave privada SSH (todo o arquivo id_rsa)
- `SERVER_PORT`: 22

## 🔒 Proteger Banco de Dados

Após a instalação inicial, execute:

```bash
# Proteger banco de dados contra modificações
sudo /opt/erp-system/scripts/deploy/protect_database.sh
```

Isso irá:
- ✅ Tornar o banco de dados somente leitura
- ✅ Desabilitar `init_db.py` no deploy automático
- ✅ Criar script de manutenção (`erp-db-maintenance`)

## 🔄 Deploy Automático

Após configurar tudo, faça push para o branch principal:

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

## 🛠️ Comandos de Gerenciamento

### Comandos Principais

```bash
# Ver status do sistema
erp-manage status

# Ver logs
erp-manage logs

# Reiniciar sistema
erp-manage restart

# Fazer backup manual
erp-manage backup

# Verificar saúde
erp-manage health

# Limpar logs e cache
erp-manage clean
```

### Comandos de Banco de Dados

```bash
# Habilitar escrita no banco (para manutenção)
erp-db-maintenance enable

# Desabilitar escrita no banco (após manutenção)
erp-db-maintenance disable

# Restaurar backup
erp-manage restore /opt/backups/erp/arquivo_backup.db
```

## 🔒 Configurar SSL (Opcional)

Para configurar HTTPS:

```bash
# Executar script SSL
sudo /opt/erp-system/scripts/deploy/ssl_setup.sh
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
- **Formato**: `erp_YYYYMMDD_HHMMSS.db`

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

## 📁 Estrutura de Arquivos

```
/opt/erp-system/          # Aplicação principal
├── app/                  # Código da aplicação
├── instance/             # Banco de dados SQLite (protegido)
├── venv/                 # Ambiente virtual Python
├── scripts/deploy/       # Scripts de deploy
└── .env                  # Configurações

/opt/backups/erp/         # Backups automáticos
/etc/systemd/system/      # Serviço systemd
/etc/nginx/sites-available/ # Configuração Nginx
```

## 🔧 Configuração Avançada

### Modificar Configurações

```bash
# Editar configurações da aplicação
nano /opt/erp-system/.env

# Editar configuração do Nginx
nano /etc/nginx/sites-available/erp-system

# Editar serviço systemd
nano /etc/systemd/system/erp-system.service
```

### Atualizar Dependências

```bash
# Atualizar manualmente
cd /opt/erp-system
source venv/bin/activate
pip install -r requirements.txt
systemctl restart erp-system
```

## 📞 Suporte

### Informações do Sistema

```bash
# Versão do sistema
cat /opt/erp-system/version.txt

# Status completo
erp-manage health

# Informações do servidor
uname -a
df -h
free -h
```

### Arquivos Importantes

- **Documentação**: `/opt/erp-system/docs/`
- **Logs**: `/var/log/`
- **Backups**: `/opt/backups/erp/`
- **Configurações**: `/opt/erp-system/.env`

## ✅ Checklist de Deploy

- [ ] Servidor Ubuntu configurado
- [ ] Script de instalação executado
- [ ] SSH key gerada
- [ ] GitHub secrets configurados
- [ ] Primeiro deploy testado
- [ ] Banco de dados protegido
- [ ] SSL configurado (opcional)
- [ ] Backup funcionando
- [ ] Monitoramento ativo

## 🎯 Fluxo de Trabalho

1. **Desenvolvimento**: Faça alterações no código
2. **Commit**: Faça commit das mudanças
3. **Push**: Push para o branch principal
4. **Deploy Automático**: GitHub Actions atualiza o servidor
5. **Verificação**: Teste as mudanças em produção

## 🔐 Segurança

- ✅ Firewall configurado (SSH, HTTP, HTTPS)
- ✅ Usuário dedicado sem privilégios root
- ✅ Banco de dados protegido contra modificações
- ✅ Backup automático
- ✅ Logs de auditoria

---

**🎉 Sistema pronto para produção com deploy automático!**

Para suporte adicional, consulte a documentação em `/opt/erp-system/docs/`.
