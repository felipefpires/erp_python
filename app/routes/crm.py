from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.crm import Customer, Sale, SaleItem
from app.models.inventory import Product
from app import db
from datetime import datetime
from sqlalchemy import func

crm_bp = Blueprint('crm', __name__, url_prefix='/crm')

@crm_bp.route('/')
@login_required
def index():
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('crm/index.html', customers=customers)

@crm_bp.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('crm/customers.html', customers=customers)

@crm_bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            instagram=request.form.get('instagram'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            company=request.form.get('company'),
            cpf_cnpj=request.form.get('cpf_cnpj'),
            status=request.form.get('status', 'active')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash('Cliente criado com sucesso!', 'success')
        return redirect(url_for('crm.customers'))
    
    # Criar um objeto form com todos os campos necessários
    class Form:
        def __init__(self):
            self.name = type('Field', (), {'data': None, 'errors': []})()
            self.email = type('Field', (), {'data': None, 'errors': []})()
            self.phone = type('Field', (), {'data': None, 'errors': []})()
            self.instagram = type('Field', (), {'data': None, 'errors': []})()
            self.status = type('Field', (), {'data': 'active', 'errors': []})()
            self.company = type('Field', (), {'data': None, 'errors': []})()
            self.position = type('Field', (), {'data': None, 'errors': []})()
            self.cnpj = type('Field', (), {'data': None, 'errors': []})()
            self.cpf = type('Field', (), {'data': None, 'errors': []})()
            self.cep = type('Field', (), {'data': None, 'errors': []})()
            self.city = type('Field', (), {'data': None, 'errors': []})()
            self.state = type('Field', (), {'data': None, 'errors': []})()
            self.address = type('Field', (), {'data': None, 'errors': []})()
            self.source = type('Field', (), {'data': None, 'errors': []})()
            self.notes = type('Field', (), {'data': None, 'errors': []})()
    
    form = Form()
    return render_template('crm/new_customer.html', form=form)

@crm_bp.route('/customers/<int:id>')
@login_required
def customer_detail(id):
    customer = Customer.query.get_or_404(id)
    sales = Sale.query.filter_by(customer_id=id).order_by(Sale.sale_date.desc()).all()
    return render_template('crm/customer_detail.html', customer=customer, sales=sales)

@crm_bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.instagram = request.form.get('instagram')
        customer.address = request.form.get('address')
        customer.city = request.form.get('city')
        customer.state = request.form.get('state')
        customer.zip_code = request.form.get('zip_code')
        customer.company = request.form.get('company')
        customer.cpf_cnpj = request.form.get('cpf_cnpj')
        customer.status = request.form.get('status')
        
        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('crm.customer_detail', id=customer.id))
    
    return render_template('crm/edit_customer.html', customer=customer)

@crm_bp.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    sales_pagination = Sale.query.order_by(Sale.sale_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('crm/sales.html', sales=sales_pagination.items, pagination=sales_pagination)

@crm_bp.route('/sales/new', methods=['GET', 'POST'])
@login_required
def new_sale():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        total_amount = float(request.form.get('total_amount', 0))
        discount = float(request.form.get('discount', 0))
        tax = float(request.form.get('tax', 0))
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes')
        
        sale = Sale(
            customer_id=customer_id,
            user_id=current_user.id,
            total_amount=total_amount,
            discount=discount,
            tax=tax,
            payment_method=payment_method,
            notes=notes,
            status='completed'
        )
        
        db.session.add(sale)
        db.session.commit()
        
        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('crm.sales'))
    
    customers = Customer.query.filter_by(status='active').all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('crm/new_sale.html', 
                         customers=customers, 
                         products=products,
                         today=datetime.now().strftime('%Y-%m-%d'))

@crm_bp.route('/sales/<int:id>')
@login_required
def sale_detail(id):
    sale = Sale.query.get_or_404(id)
    return render_template('crm/sale_detail.html', sale=sale)

@crm_bp.route('/customers/<int:id>/delete', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    try:
        # Verificar se o cliente tem vendas associadas
        if customer.sales:
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir um cliente que possui vendas registradas.'
            }), 400
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente excluído com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir cliente: {str(e)}'
        }), 500

@crm_bp.route('/sales/<int:id>/delete', methods=['DELETE'])
@login_required
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    
    try:
        db.session.delete(sale)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Venda excluída com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir venda: {str(e)}'
        }), 500

@crm_bp.route('/reports')
@login_required
def reports():
    # Relatório de vendas por período
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        sales_report = Sale.query.filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()
    else:
        sales_report = []
    
    # Top clientes
    top_customers = db.session.query(
        Customer.name,
        func.count(Sale.id).label('total_sales'),
        func.sum(Sale.total_amount).label('total_amount')
    ).join(Sale).group_by(Customer.id).order_by(
        func.sum(Sale.total_amount).desc()
    ).limit(10).all()
    
    # Estatísticas resumidas
    total_sales = Sale.query.count()
    total_revenue = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    active_customers = Customer.query.filter_by(status='active').count()
    average_ticket = total_revenue / total_sales if total_sales > 0 else 0
    
    summary = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'active_customers': active_customers,
        'average_ticket': average_ticket
    }
    
    return render_template('crm/reports.html', 
                         sales_report=sales_report,
                         top_customers=top_customers,
                         summary=summary)

# API Endpoints
@crm_bp.route('/api/customers', methods=['GET'])
def api_get_customers():
    customers = Customer.query.all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'instagram': c.instagram,
            'address': c.address,
            'city': c.city,
            'state': c.state,
            'zip_code': c.zip_code,
            'company': c.company,
            'cpf_cnpj': c.cpf_cnpj,
            'status': c.status,
            'created_at': c.created_at.isoformat(),
            'updated_at': c.updated_at.isoformat()
        } for c in customers
    ])

@crm_bp.route('/api/customers/<int:id>', methods=['GET'])
def api_get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'instagram': customer.instagram,
        'address': customer.address,
        'city': customer.city,
        'state': customer.state,
        'zip_code': customer.zip_code,
        'company': customer.company,
        'cpf_cnpj': customer.cpf_cnpj,
        'status': customer.status,
        'created_at': customer.created_at.isoformat(),
        'updated_at': customer.updated_at.isoformat()
    })

@crm_bp.route('/api/customers', methods=['POST'])
def api_create_customer():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400

    customer = Customer(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        instagram=data.get('instagram'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        zip_code=data.get('zip_code'),
        company=data.get('company'),
        cpf_cnpj=data.get('cpf_cnpj'),
        status=data.get('status', 'active')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'message': 'Customer created successfully',
        'customer': {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'status': customer.status
        }
    }), 201
