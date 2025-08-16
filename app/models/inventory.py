from app import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=False)
    barcode = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    sale_price = db.Column(db.Numeric(10, 2), default=0)
    current_stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='un')  # un, kg, l, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    stock_movements = db.relationship('StockMovement', backref='product', lazy=True)
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'current_stock': self.current_stock,
            'cost_price': float(self.cost_price),
            'sale_price': float(self.sale_price),
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'unit': self.unit,
            'is_active': self.is_active,
            'stock_status': self.stock_status
        }
    
    @property
    def stock_status(self):
        # Sem estoque
        if self.current_stock is None or self.current_stock <= 0:
            return 'out_of_stock'
        # Abaixo ou igual ao mínimo
        if self.current_stock <= (self.min_stock or 0):
            return 'low_stock'
        # Acima ou igual ao máximo (quando configurado)
        if self.max_stock and self.current_stock >= self.max_stock:
            return 'high_stock'
        return 'in_stock'

class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # entrada, saida, ajuste
    quantity = db.Column(db.Integer, nullable=False)
    previous_stock = db.Column(db.Integer, nullable=False)
    new_stock = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    reference = db.Column(db.String(100))  # número da nota fiscal, etc.
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockMovement {self.id}>'

