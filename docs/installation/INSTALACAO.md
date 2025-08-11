# Guia de Instalação - Sistema ERP

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

### 1. Clone ou baixe o projeto
```bash
# Se estiver usando git
git clone <url-do-repositorio>
cd erp-project

# Ou simplesmente extraia o arquivo ZIP
```

### 2. Crie um ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
# Copie o arquivo de configuração
cp config.env .env

# Edite o arquivo .env com suas configurações
# SECRET_KEY=sua-chave-secreta-aqui
# DATABASE_URL=sqlite:///erp.db
```

### 5. Inicialize o banco de dados
```bash
python init_db.py
```

### 6. Execute o sistema
```bash
python app.py
```

## Acesso ao Sistema

Após executar o sistema, acesse:
- **URL**: http://localhost:5000
- **Usuário**: admin
- **Senha**: admin123

## Estrutura do Projeto

```
erp-project/
├── app/
│   ├── __init__.py          # Configuração da aplicação
│   ├── models/              # Modelos de dados
│   │   ├── user.py          # Usuários
│   │   ├── crm.py           # CRM (Clientes, Vendas)
│   │   ├── inventory.py     # Estoque
│   │   ├── finance.py       # Finanças
│   │   └── schedule.py      # Agendamentos
│   ├── routes/              # Rotas da aplicação
│   │   ├── auth.py          # Autenticação
│   │   ├── main.py          # Dashboard
│   │   ├── crm.py           # CRM
│   │   ├── inventory.py     # Estoque
│   │   ├── finance.py       # Finanças
│   │   └── schedule.py      # Agendamentos
│   └── templates/           # Templates HTML
├── app.py                   # Arquivo principal
├── init_db.py              # Inicialização do banco
├── requirements.txt         # Dependências
└── README.md               # Documentação
```

## Módulos Disponíveis

### 1. CRM (Customer Relationship Management)
- Gestão de clientes
- Registro de vendas
- Histórico de vendas
- Relatórios de clientes

### 2. Gestão de Estoque
- Cadastro de produtos
- Controle de estoque
- Movimentações de entrada/saída
- Alertas de estoque baixo
- Categorias de produtos

### 3. Finanças
- Controle de receitas e despesas
- Gestão de contas bancárias
- Faturas
- Relatórios financeiros
- Fluxo de caixa

### 4. Agendamentos
- Calendário de eventos
- Agendamentos com clientes
- Lembretes
- Gestão de compromissos

## Funcionalidades Principais

- ✅ Sistema de autenticação
- ✅ Dashboard com estatísticas
- ✅ Gestão completa de clientes
- ✅ Controle de estoque
- ✅ Sistema financeiro
- ✅ Agendamentos e calendário
- ✅ Interface responsiva
- ✅ Relatórios básicos

## Próximos Passos

Para expandir o sistema, considere:

1. **Relatórios Avançados**: Gráficos e dashboards mais detalhados
2. **Integração com APIs**: Pagamentos, correios, etc.
3. **Sistema de Notificações**: Email, SMS
4. **Backup Automático**: Do banco de dados
5. **Múltiplos Usuários**: Com diferentes níveis de acesso
6. **API REST**: Para integração com outros sistemas

## Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências foram instaladas
2. Confirme se o banco de dados foi inicializado
3. Verifique os logs de erro no terminal
4. Certifique-se de que a porta 5000 está disponível

## Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, Font Awesome
- **Banco de Dados**: SQLite (desenvolvimento)
- **Autenticação**: Flask-Login
- **Formulários**: HTML Forms


