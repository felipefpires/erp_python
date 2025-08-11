from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.finance import Transaction, Account, Invoice
from app.models.crm import Customer, Sale
from app import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@login_required
def index():
    # Resumo financeiro
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'receita',
        Transaction.status == 'completed'
    ).scalar() or 0
    
    total_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'despesa',
        Transaction.status == 'completed'
    ).scalar() or 0
    
    balance = total_income - total_expenses
    
    # Transações recentes
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(10).all()
    
    # Contas
    accounts = Account.query.filter_by(is_active=True).all()
    
    return render_template('finance/index.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         recent_transactions=recent_transactions,
                         accounts=accounts)

@finance_bp.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    
    # Query base
    query = Transaction.query
    
    # Aplicar filtros
    search = request.args.get('search')
    if search:
        query = query.filter(
            Transaction.description.contains(search) | 
            Transaction.reference.contains(search)
        )
    
    transaction_type = request.args.get('type')
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    account_id = request.args.get('account', type=int)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter(Transaction.status == status)
    
    date_range = request.args.get('date_range')
    if date_range:
        today = date.today()
        if date_range == 'today':
            query = query.filter(Transaction.transaction_date == today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(Transaction.transaction_date >= week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(Transaction.transaction_date >= month_ago)
        elif date_range == 'quarter':
            quarter_ago = today - timedelta(days=90)
            query = query.filter(Transaction.transaction_date >= quarter_ago)
        elif date_range == 'year':
            year_ago = today - timedelta(days=365)
            query = query.filter(Transaction.transaction_date >= year_ago)
    
    # Paginação
    transactions_pagination = query.order_by(
        Transaction.transaction_date.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    # Calcular resumo
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'receita',
        Transaction.status == 'completed'
    ).scalar() or 0
    
    total_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'despesa',
        Transaction.status == 'completed'
    ).scalar() or 0
    
    balance = total_revenue - total_expenses
    
    pending_count = db.session.query(func.count(Transaction.id)).filter(
        Transaction.status == 'pending'
    ).scalar() or 0
    
    summary = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'balance': balance,
        'pending_count': pending_count
    }
    
    # Contas para filtro
    accounts = Account.query.filter_by(is_active=True).all()
    
    return render_template('finance/transactions.html', 
                         transactions=transactions_pagination.items,
                         pagination=transactions_pagination,
                         accounts=accounts,
                         summary=summary)

@finance_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        try:
            # Validar campos obrigatórios
            account_id = request.form.get('account_id')
            transaction_type = request.form.get('transaction_type')
            description = request.form.get('description', '').strip()
            # Normalizar valor: aceitar vírgula como separador
            amount_raw = request.form.get('amount', '').replace('.', '').replace(',', '.')
            amount = amount_raw if amount_raw else None
            transaction_date = request.form.get('transaction_date')
            
            if not account_id:
                flash('Selecione uma conta!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            
            if not transaction_type:
                flash('Selecione o tipo de transação!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            
            if not description:
                flash('A descrição é obrigatória!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            
            if not amount:
                flash('O valor é obrigatório!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            if float(amount) <= 0:
                flash('O valor deve ser maior que zero!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            
            if not transaction_date:
                flash('A data da transação é obrigatória!', 'error')
                accounts = Account.query.filter_by(is_active=True).all()
                return render_template('finance/new_transaction.html', 
                                     accounts=accounts,
                                     today=datetime.now().strftime('%Y-%m-%d'))
            
            # Processar data de vencimento
            due_date = None
            if request.form.get('due_date'):
                try:
                    due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de vencimento inválida!', 'error')
                    accounts = Account.query.filter_by(is_active=True).all()
                    return render_template('finance/new_transaction.html', 
                                         accounts=accounts,
                                         today=datetime.now().strftime('%Y-%m-%d'))
            
            transaction = Transaction(
                account_id=account_id,
                transaction_type=transaction_type,
                category=request.form.get('category'),
                description=description,
                amount=float(amount),
                transaction_date=datetime.strptime(transaction_date, '%Y-%m-%d').date(),
                due_date=due_date,
                payment_method=request.form.get('payment_method'),
                reference=request.form.get('reference'),
                notes=request.form.get('notes'),
                user_id=current_user.id,
                status='completed' if request.form.get('status') == 'completed' else 'pending'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transação registrada com sucesso!', 'success')
            return redirect(url_for('finance.transactions'))
            
        except ValueError as e:
            flash('Erro: Verifique se os valores numéricos estão corretos.', 'error')
            db.session.rollback()
        except Exception as e:
            flash(f'Erro ao registrar transação: {str(e)}', 'error')
            db.session.rollback()
            print(f"Erro detalhado na transação: {e}")
    
    accounts = Account.query.filter_by(is_active=True).all()
    return render_template('finance/new_transaction.html', 
                         accounts=accounts,
                         today=datetime.now().strftime('%Y-%m-%d'))

@finance_bp.route('/transactions/<int:id>')
@login_required
def transaction_detail(id):
    transaction = Transaction.query.get_or_404(id)
    return render_template('finance/transaction_detail.html', transaction=transaction)

@finance_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if request.method == 'POST':
        transaction.account_id = request.form.get('account_id')
        transaction.transaction_type = request.form.get('transaction_type')
        transaction.category = request.form.get('category')
        transaction.description = request.form.get('description')
        transaction.amount = float(request.form.get('amount'))
        transaction.transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        transaction.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None
        transaction.payment_method = request.form.get('payment_method')
        transaction.reference = request.form.get('reference')
        transaction.notes = request.form.get('notes')
        transaction.status = request.form.get('status')
        
        db.session.commit()
        flash('Transação atualizada com sucesso!', 'success')
        return redirect(url_for('finance.transaction_detail', id=transaction.id))
    
    accounts = Account.query.filter_by(is_active=True).all()
    return render_template('finance/edit_transaction.html', 
                         transaction=transaction, accounts=accounts)

@finance_bp.route('/transactions/<int:id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        # Se for chamada via fetch, retornar JSON
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Transação excluída com sucesso!', 'success')
        return redirect(url_for('finance.transactions'))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Erro ao excluir transação: {e}', 'error')
        return redirect(url_for('finance.transactions'))

@finance_bp.route('/accounts')
@login_required
def accounts():
    accounts = Account.query.all()
    total_balance = sum(account.current_balance for account in accounts)
    return render_template('finance/accounts.html', 
                         accounts=accounts,
                         total_balance=total_balance)

@finance_bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def new_account():
    if request.method == 'POST':
        account = Account(
            name=request.form.get('name'),
            account_type=request.form.get('account_type'),
            account_number=request.form.get('account_number'),
            bank_name=request.form.get('bank_name'),
            initial_balance=float(request.form.get('initial_balance', 0)),
            current_balance=float(request.form.get('initial_balance', 0))
        )
        
        db.session.add(account)
        db.session.commit()
        
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('finance.accounts'))
    
    return render_template('finance/new_account.html')

@finance_bp.route('/accounts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(id):
    account = Account.query.get_or_404(id)
    
    if request.method == 'POST':
        account.name = request.form.get('name')
        account.account_type = request.form.get('account_type')
        account.account_number = request.form.get('account_number')
        account.bank_name = request.form.get('bank_name')
        account.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Conta atualizada com sucesso!', 'success')
        return redirect(url_for('finance.account_detail', id=account.id))
    
    return render_template('finance/edit_account.html', account=account)

@finance_bp.route('/accounts/<int:id>/delete', methods=['POST'])
@login_required
def delete_account(id):
    account = Account.query.get_or_404(id)
    
    if account.transactions:
        flash('Não é possível excluir uma conta que possui transações!', 'error')
        return redirect(url_for('finance.account_detail', id=account.id))
    
    db.session.delete(account)
    db.session.commit()
    
    flash('Conta excluída com sucesso!', 'success')
    return redirect(url_for('finance.accounts'))

@finance_bp.route('/accounts/<int:id>')
@login_required
def account_detail(id):
    account = Account.query.get_or_404(id)
    transactions = Transaction.query.filter_by(account_id=id).order_by(
        Transaction.transaction_date.desc()
    ).all()
    return render_template('finance/account_detail.html', 
                         account=account, transactions=transactions)

@finance_bp.route('/invoices')
@login_required
def invoices():
    page = request.args.get('page', 1, type=int)
    invoices_pagination = Invoice.query.order_by(Invoice.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('finance/invoices.html', 
                         invoices=invoices_pagination.items,
                         pagination=invoices_pagination,
                         today=date.today())

@finance_bp.route('/invoices/new', methods=['GET', 'POST'])
@login_required
def new_invoice():
    if request.method == 'POST':
        sale_id = request.form.get('sale_id')
        sale = Sale.query.get(sale_id)
        
        if not sale:
            flash('Venda não encontrada!', 'error')
            return redirect(url_for('finance.new_invoice'))
        
        invoice = Invoice(
            invoice_number=request.form.get('invoice_number'),
            customer_id=sale.customer_id,
            sale_id=sale_id,
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date(),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date(),
            total_amount=sale.total_amount,
            notes=request.form.get('notes')
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        flash('Fatura criada com sucesso!', 'success')
        return redirect(url_for('finance.invoices'))
    
    sales = Sale.query.filter_by(status='completed').all()
    return render_template('finance/new_invoice.html', 
                         sales=sales,
                         today=date.today())

@finance_bp.route('/reports')
@login_required
def reports():
    # Relatório de receitas e despesas por período
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    account_id = request.args.get('account_id')
    transaction_type = request.args.get('transaction_type')
    
    # Query base para transações
    query = Transaction.query
    
    # Aplicar filtros
    if start_date and end_date:
        query = query.filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    # Buscar transações
    transactions = query.all()
    
    # Separar receitas e despesas
    income_report = [t for t in transactions if t.transaction_type == 'receita']
    expense_report = [t for t in transactions if t.transaction_type == 'despesa']
    
    # Calcular totais
    total_income = sum(t.amount for t in income_report if t.status == 'completed')
    total_expenses = sum(t.amount for t in expense_report if t.status == 'completed')
    net_income = total_income - total_expenses
    total_transactions = len(transactions)
    
    # Faturas vencidas
    overdue_invoices = Invoice.query.filter(
        Invoice.status == 'pending',
        Invoice.due_date < date.today()
    ).all()
    
    # Fluxo de caixa
    cash_flow = db.session.query(
        func.date(Transaction.transaction_date).label('date'),
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.status == 'completed'
    ).group_by(
        func.date(Transaction.transaction_date)
    ).order_by(
        func.date(Transaction.transaction_date)
    ).all()
    
    # Contas para filtro
    accounts = Account.query.all()
    
    return render_template('finance/reports.html',
                         income_report=income_report,
                         expense_report=expense_report,
                         overdue_invoices=overdue_invoices,
                         cash_flow=cash_flow,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         net_income=net_income,
                         total_transactions=total_transactions,
                         accounts=accounts,
                         today=date.today())

