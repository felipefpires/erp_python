# 🚀 Execução Rápida - Sistema ERP

## ⚡ Passos para Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados
```bash
python init_db.py
```

### 3. Executar o Sistema
```bash
python app.py
```

### 4. Acessar o Sistema
- **URL**: http://localhost:5000
- **Usuário**: admin
- **Senha**: admin123

## 🧪 Testar o Sistema
```bash
python test_system.py
```

## 📁 Estrutura do Projeto
```
erp-project/
├── app/                    # Aplicação principal
│   ├── models/            # Modelos de dados
│   ├── routes/            # Rotas da aplicação
│   └── templates/         # Templates HTML
├── app.py                 # Arquivo principal
├── init_db.py            # Inicialização do banco
├── test_system.py        # Teste do sistema
├── requirements.txt      # Dependências
└── README.md            # Documentação completa
```

## 🔧 Módulos Disponíveis

### 📊 Dashboard
- Visão geral do sistema
- Estatísticas principais
- Alertas e notificações

### 👥 CRM
- Gestão de clientes
- Histórico de vendas
- Relatórios de clientes

### 📦 Estoque
- Controle de produtos
- Movimentações de estoque
- Alertas de estoque baixo

### 💰 Finanças
- Controle de receitas/despesas
- Gestão de contas
- Relatórios financeiros

### 📅 Agendamentos
- Calendário de eventos
- Agendamentos com clientes
- Gestão de compromissos

## 🆘 Solução de Problemas

### Erro de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de Banco de Dados
```bash
rm erp.db  # Remove banco antigo
python init_db.py  # Recria o banco
```

### Erro de Porta
```bash
# Altere a porta no arquivo app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📞 Suporte
- Verifique se Python 3.8+ está instalado
- Confirme se todas as dependências foram instaladas
- Verifique os logs no terminal para erros específicos


