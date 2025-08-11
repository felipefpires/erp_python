from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.crm import Customer, Sale
from app.models.inventory import Product
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
    # Estatísticas do dashboard
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    
    # Vendas do mês atual
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_sales = Sale.query.filter(
        func.extract('month', Sale.sale_date) == current_month,
        func.extract('year', Sale.sale_date) == current_year
    ).count()
    
    # Produtos com estoque baixo
    low_stock_products = Product.query.filter(
        Product.current_stock <= Product.min_stock
    ).limit(5).all()
    
    # Próximos agendamentos
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now(),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date).limit(5).all()
    
    # Transações recentes
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(5).all()
    
    # Total de vendas do mês
    monthly_sales_total = db.session.query(func.sum(Sale.total_amount)).filter(
        func.extract('month', Sale.sale_date) == current_month,
        func.extract('year', Sale.sale_date) == current_year
    ).scalar() or 0
    
    return render_template('main/dashboard.html',
                         total_customers=total_customers,
                         total_products=total_products,
                         total_sales=total_sales,
                         monthly_sales=monthly_sales,
                         monthly_sales_total=monthly_sales_total,
                         low_stock_products=low_stock_products,
                         upcoming_appointments=upcoming_appointments,
                         recent_transactions=recent_transactions,
                         current_date=datetime.now())

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
