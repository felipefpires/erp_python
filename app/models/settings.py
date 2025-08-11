from app import db
from datetime import datetime

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200))
    company_email = db.Column(db.String(200))
    company_phone = db.Column(db.String(50))
    company_address = db.Column(db.Text)
    currency = db.Column(db.String(10), default='BRL')
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')
    low_stock_threshold = db.Column(db.Integer, default=10)
    invoice_due_days = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.company_name}>'

class EmailSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(200))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(200))
    smtp_password = db.Column(db.String(200))
    smtp_use_tls = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailSettings {self.smtp_server}>'

class BackupSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    retention_days = db.Column(db.Integer, default=30)
    last_backup = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BackupSettings {self.frequency}>'

