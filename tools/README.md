# 🛠️ Ferramentas - Manutenção e Backup

Esta pasta contém ferramentas para manutenção, backup e verificação do Sistema ERP.

## 📂 Estrutura

### **💾 backup/**
Ferramentas para backup e restauração do sistema.

- `erp-system.tar.gz` - Backup compactado do sistema
- Scripts de backup automático
- Ferramentas de restauração

### **🔧 maintenance/**
Ferramentas de manutenção e verificação do sistema.

- `check_*.py` - Scripts de verificação
- `remove_email_index.py` - Remoção de índices de email
- Ferramentas de diagnóstico

## 🚀 Como Usar

### **Backup do Sistema**
```bash
# Fazer backup manual
cd tools/backup
tar -czf erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/erp-system/

# Restaurar backup
tar -xzf erp_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

### **Manutenção do Sistema**
```bash
# Verificar índices do banco
python tools/maintenance/check_indexes.py

# Verificar usuário admin
python tools/maintenance/check_admin_user.py

# Remover índice de email
python tools/maintenance/remove_email_index.py
```

## 🔧 Ferramentas Disponíveis

### **Verificação de Banco de Dados**
- `check_indexes.py` - Verifica e corrige índices do banco
- `check_admin_user.py` - Verifica usuário administrador

### **Limpeza de Dados**
- `remove_email_index.py` - Remove índices duplicados de email

### **Backup e Restauração**
- Scripts de backup automático
- Ferramentas de compactação
- Utilitários de restauração

## 📝 Procedimentos de Manutenção

### **Manutenção Preventiva**
1. Execute verificações regulares
2. Faça backup antes de mudanças
3. Monitore logs do sistema
4. Verifique integridade do banco

### **Manutenção Corretiva**
1. Identifique o problema
2. Use ferramentas específicas
3. Faça backup antes de correções
4. Teste após correções

## 🔒 Segurança

### **Backup Seguro**
- Mantenha backups em local seguro
- Use criptografia quando necessário
- Teste restaurações regularmente
- Mantenha múltiplas cópias

### **Manutenção Segura**
- Sempre faça backup antes de manutenção
- Use ferramentas em ambiente de teste
- Documente todas as alterações
- Mantenha logs de manutenção

## 📊 Monitoramento

### **Verificações Regulares**
- Integridade do banco de dados
- Performance do sistema
- Espaço em disco
- Logs de erro

### **Alertas**
- Configurar alertas automáticos
- Monitorar recursos do sistema
- Verificar backups
- Acompanhar logs

## 🔗 Links Úteis

- [📖 README Principal](../README.md)
- [🔧 Scripts](../scripts/README.md)
- [📚 Documentação](../docs/README.md)
- [📁 Aplicação](../app/)

## 📞 Suporte

Para problemas de manutenção:
1. Consulte a documentação em `../docs/troubleshooting/`
2. Use as ferramentas de diagnóstico
3. Verifique logs do sistema
4. Entre em contato com a equipe técnica
