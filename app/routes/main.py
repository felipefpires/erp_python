from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.crm import Customer, Sale
from app.models.inventory import Product, Category
from app.models.finance import Transaction, Account
from app.models.schedule import Appointment, Event
from app.models.settings import SystemSettings, EmailSettings, BackupSettings
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    product_search = request.args.get('product_search', '').strip()
    product_category_id = request.args.get('product_category', type=int)
    product_stock_status = request.args.get('product_stock_status', '')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de data inicial inválido. Use YYYY-MM-DD.', 'error')
            start_date = None
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de data final inválido. Use YYYY-MM-DD.', 'error')
            end_date = None

    # Default to current month if no date range is provided
    if not start_date and not end_date:
        current_month = datetime.now().month
        current_year = datetime.now().year
        start_date = datetime(current_year, current_month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif start_date and not end_date:
        # If only start_date is provided, set end_date to end of that month
        end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif not start_date and end_date:
        # If only end_date is provided, set start_date to beginning of that month
        start_date = end_date.replace(day=1)

    # Ensure end_date is always at the end of the day
    if end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59)

    # Estatísticas do dashboard
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    
    # Vendas no período
    sales_query = Sale.query
    if start_date:
        sales_query = sales_query.filter(Sale.sale_date >= start_date)
    if end_date:
        sales_query = sales_query.filter(Sale.sale_date <= end_date)
    
    filtered_sales_count = sales_query.count()
    filtered_sales_total = db.session.query(func.sum(Sale.total_amount)).filter(
        sales_query.subquery().c.id == Sale.id
    ).scalar() or 0
    
    # Produtos com estoque baixo (não filtrado por data, é um estado atual)
    # Query base para produtos
    products_query = Product.query

    # Aplicar filtros de produto
    if product_search:
        products_query = products_query.filter(
            or_(
                Product.name.ilike(f'%{product_search}%'),
                Product.sku.ilike(f'%{product_search}%'),
                Product.barcode.ilike(f'%{product_search}%')
            )
        )
    
    if product_category_id:
        products_query = products_query.filter(Product.category_id == product_category_id)
    
    if product_stock_status == 'in_stock':
        products_query = products_query.filter(
            Product.current_stock > func.coalesce(Product.min_stock, 0)
        )
    elif product_stock_status == 'low_stock':
        products_query = products_query.filter(
            Product.current_stock > 0,
            Product.current_stock <= func.coalesce(Product.min_stock, 0)
        )
    elif product_stock_status == 'out_of_stock':
        products_query = products_query.filter(
            or_(
                Product.current_stock == 0,
                Product.current_stock.is_(None)
            )
        )

    # Produtos com estoque baixo (agora filtrados também pelos parâmetros gerais de produto)
    low_stock_products = products_query.filter(
        Product.current_stock <= Product.min_stock
    ).limit(5).all()

    # Todos os produtos (com filtros aplicados)
    all_filtered_products = products_query.order_by(Product.name.asc()).all()
    
    # Próximos agendamentos (filtrado por data)
    appointments_query = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now(),
        Appointment.status == 'scheduled'
    )
    if start_date:
        appointments_query = appointments_query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        appointments_query = appointments_query.filter(Appointment.appointment_date <= end_date)
    
    upcoming_appointments = appointments_query.order_by(Appointment.appointment_date).limit(5).all()
    
    # Transações recentes (filtrado por data)
    transactions_query = Transaction.query
    if start_date:
        transactions_query = transactions_query.filter(Transaction.created_at >= start_date)
    if end_date:
        transactions_query = transactions_query.filter(Transaction.created_at <= end_date)
    
    recent_transactions = transactions_query.order_by(
        Transaction.created_at.desc()
    ).limit(5).all()

    # Resumo do estoque (agora baseado nos produtos filtrados)
    filtered_products_subquery = products_query.subquery()
    total_stock_quantity = db.session.query(func.sum(filtered_products_subquery.c.current_stock)).scalar() or 0
    total_stock_value = db.session.query(func.sum(filtered_products_subquery.c.current_stock * filtered_products_subquery.c.cost_price)).scalar() or 0
    total_potential_sales_value = db.session.query(func.sum(filtered_products_subquery.c.current_stock * filtered_products_subquery.c.sale_price)).scalar() or 0
    
    # Buscar categorias para o filtro de produtos
    categories = Category.query.all()

    return render_template('main/dashboard.html',
                         total_customers=total_customers,
                         total_products=total_products,
                         total_sales=total_sales,
                         filtered_sales_count=filtered_sales_count,
                         filtered_sales_total=filtered_sales_total,
                         low_stock_products=low_stock_products,
                         all_filtered_products=all_filtered_products, # Novo: todos os produtos filtrados
                         upcoming_appointments=upcoming_appointments,
                         recent_transactions=recent_transactions,
                         total_stock_quantity=int(total_stock_quantity),
                         total_stock_value=float(total_stock_value),
                         total_potential_sales_value=float(total_potential_sales_value),
                         current_date=datetime.now(),
                         start_date=start_date.strftime('%Y-%m-%d') if start_date else '',
                         end_date=end_date.strftime('%Y-%m-%d') if end_date else '',
                         categories=categories, # Novo: categorias para filtro
                         product_search=product_search,
                         product_category_id=product_category_id,
                         product_stock_status=product_stock_status)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Atualizar informações do perfil
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.role = request.form.get('role')
        current_user.is_active = bool(request.form.get('is_active'))
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/profile.html')

@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Senha atual incorreta!', 'error')
        return redirect(url_for('main.profile'))
    
    if new_password != confirm_password:
        flash('As senhas não coincidem!', 'error')
        return redirect(url_for('main.profile'))
    
    if len(new_password) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres!', 'error')
        return redirect(url_for('main.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('main.profile'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Buscar configurações existentes ou criar padrão
    system_settings = SystemSettings.query.first()
    if not system_settings:
        system_settings = SystemSettings()
        db.session.add(system_settings)
        db.session.commit()
    
    if request.method == 'POST':
        # Atualizar configurações do sistema
        system_settings.company_name = request.form.get('company_name')
        system_settings.company_email = request.form.get('company_email')
        system_settings.company_phone = request.form.get('company_phone')
        system_settings.company_address = request.form.get('company_address')
        system_settings.currency = request.form.get('currency')
        system_settings.timezone = request.form.get('timezone')
        system_settings.low_stock_threshold = int(request.form.get('low_stock_threshold', 10))
        system_settings.invoice_due_days = int(request.form.get('invoice_due_days', 30))
        
        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('main.settings'))
    
    # Buscar configurações de email e backup
    email_settings = EmailSettings.query.first()
    backup_settings = BackupSettings.query.first()
    
    return render_template('main/settings.html', 
                         settings=system_settings,
                         email_settings=email_settings,
                         backup_settings=backup_settings)

@main_bp.route('/email_settings', methods=['POST'])
@login_required
def email_settings():
    email_settings = EmailSettings.query.first()
    if not email_settings:
        email_settings = EmailSettings()
        db.session.add(email_settings)
    
    email_settings.smtp_server = request.form.get('smtp_server')
    email_settings.smtp_port = int(request.form.get('smtp_port', 587))
    email_settings.smtp_username = request.form.get('smtp_username')
    email_settings.smtp_password = request.form.get('smtp_password')
    email_settings.smtp_use_tls = bool(request.form.get('smtp_use_tls'))
    
    db.session.commit()
    flash('Configurações de e-mail salvas com sucesso!', 'success')
    return redirect(url_for('main.settings'))

@main_bp.route('/backup_settings', methods=['POST'])
@login_required
def backup_settings():
    backup_settings = BackupSettings.query.first()
    if not backup_settings:
        backup_settings = BackupSettings()
        db.session.add(backup_settings)
    
    backup_settings.frequency = request.form.get('backup_frequency')
    backup_settings.retention_days = int(request.form.get('backup_retention', 30))
    
    db.session.commit()
    flash('Configurações de backup salvas com sucesso!', 'success')
    return redirect(url_for('main.settings'))

@main_bp.route('/create_backup')
@login_required
def create_backup():
    # Implementar lógica de backup aqui
    backup_settings = BackupSettings.query.first()
    if backup_settings:
        backup_settings.last_backup = datetime.utcnow()
        db.session.commit()
    
    flash('Backup criado com sucesso!', 'success')
    return redirect(url_for('main.settings'))
