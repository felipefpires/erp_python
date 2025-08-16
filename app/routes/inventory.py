from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.inventory import Product, Category, StockMovement
from app import db
from datetime import datetime
from sqlalchemy import func, or_
from urllib.parse import urlencode

def create_pagination_urls(base_url, current_args, page):
    """Cria URLs de paginação preservando todos os filtros"""
    args = current_args.copy()
    args['page'] = page
    return f"{base_url}?{urlencode(args)}"

def create_pagination(query, page, per_page):
    """Função utilitária para criar paginação compatível com Flask-SQLAlchemy 3.0.5"""
    # Contar total de registros
    total = query.count()
    
    # Calcular offset
    offset = (page - 1) * per_page
    
    # Buscar itens paginados
    items = query.offset(offset).limit(per_page).all()
    
    # Criar objeto de paginação
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page if total > 0 else 0
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
            """Método para iterar sobre as páginas da paginação"""
            if self.pages == 0:
                return
                
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or 
                    (num > self.page - left_current - 1 and 
                     num < self.page + right_current) or 
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    return Pagination(items, page, per_page, total)

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    products = Product.query.filter_by(is_active=True).all()
    low_stock_products = Product.query.filter(
        Product.current_stock <= Product.min_stock
    ).all()
    
    return render_template('inventory/index.html', 
                         products=products,
                         low_stock_products=low_stock_products)

@inventory_bp.route('/products')
@login_required
def products():
    try:
        # Obter parâmetros de filtro
        search = request.args.get('search', '').strip()
        category_id = request.args.get('category', type=int)
        status = request.args.get('status', '')
        stock_status = request.args.get('stock_status', '')
        sort = request.args.get('sort', 'name')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Debug: imprimir parâmetros recebidos
        print(f"DEBUG - Filtros recebidos: search='{search}', category_id={category_id}, status='{status}', stock_status='{stock_status}', sort='{sort}', page={page}")
        
        # Query base
        query = Product.query
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%'),
                    Product.barcode.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if status == 'active':
            query = query.filter(Product.is_active == True)
        elif status == 'inactive':
            query = query.filter(Product.is_active == False)
        
        # Filtros de estoque corrigidos
        if stock_status == 'in_stock':
            # Produtos com estoque acima do mínimo
            query = query.filter(
                Product.current_stock > func.coalesce(Product.min_stock, 0)
            )
        elif stock_status == 'low_stock':
            # Produtos com estoque baixo (acima de 0 mas abaixo ou igual ao mínimo)
            query = query.filter(
                Product.current_stock > 0,
                Product.current_stock <= func.coalesce(Product.min_stock, 0)
            )
        elif stock_status == 'out_of_stock':
            # Produtos sem estoque
            query = query.filter(
                or_(
                    Product.current_stock == 0,
                    Product.current_stock.is_(None)
                )
            )
        
        # Ordenação
        if sort == 'name':
            query = query.order_by(Product.name.asc())
        elif sort == 'price':
            query = query.order_by(Product.sale_price.asc())
        elif sort == 'stock':
            query = query.order_by(Product.current_stock.asc())
        elif sort == 'created_at':
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.name.asc())
        
        # Usar função utilitária para paginação
        pagination = create_pagination(query, page, per_page)
        
        # Buscar categorias para o filtro
        categories = Category.query.all()
        
        # Criar URLs de paginação preservando filtros
        base_url = url_for('inventory.products')
        current_args = dict(request.args)
        if 'page' in current_args:
            del current_args['page']
        
        # Debug: imprimir resultados
        print(f"DEBUG - Total de produtos encontrados: {pagination.total}")
        print(f"DEBUG - Produtos na página atual: {len(pagination.items)}")
        
        return render_template('inventory/products.html',
                              products=pagination.items,
                              pagination=pagination,
                              categories=categories,
                              base_url=base_url,
                              current_args=current_args)
    
    except Exception as e:
        print(f"Erro na listagem de produtos: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Erro ao carregar produtos: {str(e)}', 'error')
        return render_template('inventory/products.html',
                              products=[],
                              pagination=None,
                              categories=[])

@inventory_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if request.method == 'POST':
        try:
            # Tratar valores vazios
            cost_price = request.form.get('cost_price')
            cost_price = float(cost_price) if cost_price else 0.0
            
            sale_price = request.form.get('sale_price')
            sale_price = float(sale_price) if sale_price else 0.0
            
            current_stock = request.form.get('current_stock')
            current_stock = int(current_stock) if current_stock else 0
            
            min_stock = request.form.get('min_stock')
            min_stock = int(min_stock) if min_stock else 0
            
            max_stock = request.form.get('max_stock')
            max_stock = int(max_stock) if max_stock else 0
            
            category_id = request.form.get('category_id')
            if category_id and category_id.strip():
                try:
                    category_id = int(category_id)
                    # Verificar se a categoria existe
                    category = Category.query.get(category_id)
                    if not category:
                        category_id = None
                except ValueError:
                    category_id = None
            else:
                category_id = None
            
            # Validar nome obrigatório
            name = request.form.get('name', '').strip()
            if not name:
                flash('O nome do produto é obrigatório.', 'error')
                categories = Category.query.all()
                return render_template('inventory/new_product.html', categories=categories)
            
            product = Product(
                name=name,
                description=request.form.get('description'),
                sku=request.form.get('sku'),
                barcode=request.form.get('barcode'),
                category_id=category_id,
                cost_price=cost_price,
                sale_price=sale_price,
                current_stock=current_stock,
                min_stock=min_stock,
                max_stock=max_stock,
                unit=request.form.get('unit', 'un')
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('inventory.products'))
            
        except ValueError as e:
            flash('Erro: Verifique se os valores numéricos estão corretos.', 'error')
            db.session.rollback()
        except Exception as e:
            flash(f'Erro ao criar produto: {str(e)}', 'error')
            db.session.rollback()
            print(f"Erro detalhado: {e}")  # Para debug
    
    categories = Category.query.all()
    return render_template('inventory/new_product.html', categories=categories)

@inventory_bp.route('/products/<int:id>')
@login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    movements = StockMovement.query.filter_by(product_id=id).order_by(
        StockMovement.movement_date.desc()
    ).all()
    return render_template('inventory/product_detail.html', 
                         product=product, movements=movements)

@inventory_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.sku = request.form.get('sku')
        product.barcode = request.form.get('barcode')
        product.category_id = request.form.get('category_id')
        product.cost_price = float(request.form.get('cost_price', 0))
        product.sale_price = float(request.form.get('sale_price', 0))
        product.min_stock = int(request.form.get('min_stock', 0))
        product.max_stock = int(request.form.get('max_stock', 0))
        product.unit = request.form.get('unit', 'un')
        product.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('inventory.product_detail', id=product.id))
    
    categories = Category.query.all()
    return render_template('inventory/edit_product.html', 
                         product=product, categories=categories)

@inventory_bp.route('/products/<int:id>/delete', methods=['DELETE', 'POST'])
@login_required
def delete_product(id):
    print(f"Tentando excluir produto ID: {id}")
    product = Product.query.get_or_404(id)
    print(f"Produto encontrado: {product.name}")
    
    try:
        # Verificar se o produto tem movimentações
        if product.stock_movements:
            print(f"Produto tem {len(product.stock_movements)} movimentações")
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir um produto que possui movimentações registradas.'
            }), 400
        
        # Verificar se o produto tem itens de venda
        if product.sale_items:
            print(f"Produto tem {len(product.sale_items)} itens de venda")
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir um produto que possui vendas registradas.'
            }), 400
        
        print("Excluindo produto...")
        db.session.delete(product)
        db.session.commit()
        print("Produto excluído com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Produto excluído com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir produto: {str(e)}'
        }), 500

@inventory_bp.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('inventory/categories.html', categories=categories)

@inventory_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            slug=request.form.get('slug', '').lower().replace(' ', '-'),
            description=request.form.get('description'),
            is_active=request.form.get('is_active') == 'on'
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('inventory.categories'))
    
    return render_template('inventory/new_category.html')

@inventory_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug', '').lower().replace(' ', '-')
        category.description = request.form.get('description')
        category.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('inventory.categories'))
    
    return render_template('inventory/edit_category.html', category=category)

@inventory_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.products:
        flash('Não é possível excluir uma categoria que possui produtos!', 'error')
        return redirect(url_for('inventory.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Categoria excluída com sucesso!', 'success')
    return redirect(url_for('inventory.categories'))

@inventory_bp.route('/movements')
@login_required
def movements():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Query base
    query = StockMovement.query.order_by(StockMovement.movement_date.desc())
    
    # Usar função utilitária para paginação
    pagination = create_pagination(query, page, per_page)
    
    return render_template('inventory/movements.html', 
                         movements=pagination.items,
                         pagination=pagination)

@inventory_bp.route('/movements/new', methods=['GET', 'POST'])
@login_required
def new_movement():
    if request.method == 'POST':
        try:
            product_id = request.form.get('product_id')
            movement_type = request.form.get('movement_type')
            quantity = int(request.form.get('quantity', 0))
            unit_cost = float(request.form.get('unit_cost', 0))
            reference = request.form.get('reference')
            notes = request.form.get('notes')
            
            if not product_id:
                flash('Selecione um produto!', 'error')
                products = Product.query.filter_by(is_active=True).all()
                return render_template('inventory/new_movement.html', 
                                     products=products,
                                     now=datetime.now())
            
            product = Product.query.get(product_id)
            if not product:
                flash('Produto não encontrado!', 'error')
                products = Product.query.filter_by(is_active=True).all()
                return render_template('inventory/new_movement.html', 
                                     products=products,
                                     now=datetime.now())
            
            if quantity <= 0:
                flash('A quantidade deve ser maior que zero!', 'error')
                products = Product.query.filter_by(is_active=True).all()
                return render_template('inventory/new_movement.html', 
                                     products=products,
                                     now=datetime.now())
            
            previous_stock = product.current_stock
            
            if movement_type == 'entrada':
                product.current_stock += quantity
            elif movement_type == 'saida':
                if product.current_stock < quantity:
                    flash('Estoque insuficiente!', 'error')
                    products = Product.query.filter_by(is_active=True).all()
                    return render_template('inventory/new_movement.html', 
                                         products=products,
                                         now=datetime.now())
                product.current_stock -= quantity
            elif movement_type == 'ajuste':
                product.current_stock = quantity
            else:
                flash('Tipo de movimentação inválido!', 'error')
                products = Product.query.filter_by(is_active=True).all()
                return render_template('inventory/new_movement.html', 
                                     products=products,
                                     now=datetime.now())
            
            new_stock = product.current_stock
            total_cost = quantity * unit_cost
            
            movement = StockMovement(
                product_id=product_id,
                movement_type=movement_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                unit_cost=unit_cost,
                total_cost=total_cost,
                reference=reference,
                notes=notes,
                user_id=current_user.id
            )
            
            db.session.add(movement)
            db.session.commit()
            
            flash(f'Movimento de estoque registrado com sucesso! Estoque atual: {new_stock}', 'success')
            return redirect(url_for('inventory.movements'))
            
        except ValueError as e:
            flash('Erro: Verifique se os valores numéricos estão corretos.', 'error')
            db.session.rollback()
        except Exception as e:
            flash(f'Erro ao registrar movimento: {str(e)}', 'error')
            db.session.rollback()
            print(f"Erro detalhado no movimento: {e}")
    
    products = Product.query.filter_by(is_active=True).all()
    return render_template('inventory/new_movement.html', 
                         products=products,
                         now=datetime.now())

@inventory_bp.route('/reports')
@login_required
def reports():
    # Estatísticas gerais
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    low_stock_products_count = Product.query.filter(
        Product.current_stock <= Product.min_stock
    ).count()
    
    # Valor total do estoque
    total_stock_value = db.session.query(
        func.sum(Product.current_stock * Product.cost_price)
    ).scalar() or 0
    
    # Produtos com estoque baixo
    low_stock_products = Product.query.filter(
        Product.current_stock <= Product.min_stock
    ).all()
    
    # Categorias para filtro
    categories = Category.query.all()
    
    # Movimentos por período
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        movements_report = StockMovement.query.filter(
            StockMovement.movement_date >= start_date,
            StockMovement.movement_date <= end_date
        ).all()
    else:
        movements_report = []
    
    # Dados para gráficos
    products_by_category = db.session.query(
        Category.name,
        func.count(Product.id)
    ).join(Product).group_by(Category.name).all()
    
    stock_status_data = {
        'normal': Product.query.filter(
            Product.current_stock > Product.min_stock,
            Product.current_stock < Product.max_stock
        ).count(),
        'low': low_stock_products_count,
        'high': Product.query.filter(
            Product.current_stock >= Product.max_stock
        ).count()
    }
    
    summary = {
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products_count,
        'total_value': float(total_stock_value)
    }
    
    return render_template('inventory/reports.html',
                         summary=summary,
                         low_stock_products=low_stock_products,
                         total_stock_value=total_stock_value,
                         movements_report=movements_report,
                         categories=categories,
                         products_by_category=products_by_category,
                         stock_status_data=stock_status_data)

@inventory_bp.route('/stock-summary')
@login_required
def stock_summary():
    # Calculate stock summary metrics
    total_quantity = db.session.query(func.sum(Product.current_stock)).scalar() or 0
    total_value = db.session.query(func.sum(Product.current_stock * Product.cost_price)).scalar() or 0

    # Return data as JSON
    return jsonify({
        'total_quantity': int(total_quantity),
        'total_value': float(total_value)
    })

