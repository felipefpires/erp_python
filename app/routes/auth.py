from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"DEBUG: Usuário já autenticado: {current_user.username}")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"DEBUG: Tentativa de login - Usuário: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"DEBUG: Usuário encontrado: {user.username}, Ativo: {user.is_active}")
            if user.check_password(password):
                print(f"DEBUG: Senha correta, fazendo login...")
                login_user(user, remember=True)
                user.last_login = db.func.now()
                db.session.commit()
                
                print(f"DEBUG: Login realizado com sucesso para {user.username}")
                next_page = request.args.get('next')
                redirect_url = next_page or url_for('main.dashboard')
                print(f"DEBUG: Redirecionando para: {redirect_url}")
                return redirect(redirect_url)
            else:
                print(f"DEBUG: Senha incorreta para usuário {username}")
                flash('Usuário ou senha inválidos', 'error')
        else:
            print(f"DEBUG: Usuário não encontrado: {username}")
            flash('Usuário ou senha inválidos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return render_template('auth/register.html')
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuário criado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


