from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.schedule import Event, Appointment
from app.models.crm import Customer
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
@login_required
def index():
    # Eventos de hoje
    today = datetime.now().date()
    today_events = Event.query.filter(
        func.date(Event.start_date) == today,
        Event.user_id == current_user.id
    ).all()
    
    # Agendamentos de hoje
    today_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status == 'scheduled'
    ).all()
    
    # Próximos eventos
    upcoming_events = Event.query.filter(
        Event.start_date >= datetime.now(),
        Event.user_id == current_user.id
    ).order_by(Event.start_date).limit(5).all()
    
    # Próximos agendamentos
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now(),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date).limit(5).all()
    
    return render_template('schedule/index.html',
                         today_events=today_events,
                         today_appointments=today_appointments,
                         upcoming_events=upcoming_events,
                         upcoming_appointments=upcoming_appointments)

@schedule_bp.route('/calendar')
@login_required
def calendar():
    return render_template('schedule/calendar.html')

@schedule_bp.route('/events')
@login_required
def events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter_by(user_id=current_user.id).order_by(
        Event.start_date.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template('schedule/events.html', events=events)

@schedule_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M'),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M'),
            location=request.form.get('location'),
            event_type=request.form.get('event_type'),
            priority=request.form.get('priority', 'normal'),
            is_all_day=request.form.get('is_all_day') == 'on',
            reminder_minutes=int(request.form.get('reminder_minutes', 15)),
            user_id=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('schedule.events'))
    
    return render_template('schedule/new_event.html')

@schedule_bp.route('/events/<int:id>')
@login_required
def event_detail(id):
    event = Event.query.get_or_404(id)
    return render_template('schedule/event_detail.html', event=event)

@schedule_bp.route('/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
        event.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%dT%H:%M')
        event.location = request.form.get('location')
        event.event_type = request.form.get('event_type')
        event.priority = request.form.get('priority')
        event.is_all_day = request.form.get('is_all_day') == 'on'
        event.reminder_minutes = int(request.form.get('reminder_minutes', 15))
        event.status = request.form.get('status')
        
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('schedule.event_detail', id=event.id))
    
    return render_template('schedule/edit_event.html', event=event)

@schedule_bp.route('/appointments')
@login_required
def appointments():
    page = request.args.get('page', 1, type=int)
    
    # Filtros
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Query base
    query = Appointment.query
    
    # Aplicar filtros
    if search:
        query = query.join(Customer).filter(Customer.name.ilike(f'%{search}%'))
    if status:
        query = query.filter(Appointment.status == status)
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    
    # Paginação
    appointments_pagination = query.order_by(
        Appointment.appointment_date.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('schedule/appointments.html', 
                         appointments=appointments_pagination.items,
                         pagination=appointments_pagination)

@schedule_bp.route('/appointments/new', methods=['GET', 'POST'])
@login_required
def new_appointment():
    if request.method == 'POST':
        try:
            # Validar campos obrigatórios
            customer_id = request.form.get('customer_id')
            title = request.form.get('title', '').strip()
            appointment_date = request.form.get('appointment_date')
            duration_minutes = request.form.get('duration_minutes', 60)
            
            if not customer_id:
                flash('Selecione um cliente!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            if not title:
                flash('O título é obrigatório!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            if not appointment_date:
                flash('A data e hora do agendamento são obrigatórias!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            # Validar se o cliente existe
            customer = Customer.query.get(customer_id)
            if not customer:
                flash('Cliente não encontrado!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            # Validar duração
            try:
                duration_minutes = int(duration_minutes)
                if duration_minutes <= 0:
                    flash('A duração deve ser maior que zero!', 'error')
                    customers = Customer.query.all()
                    return render_template('schedule/new_appointment.html', customers=customers)
            except ValueError:
                flash('Duração inválida!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            # Validar data
            try:
                appointment_datetime = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
                if appointment_datetime < datetime.now():
                    flash('A data do agendamento não pode ser no passado!', 'error')
                    customers = Customer.query.all()
                    return render_template('schedule/new_appointment.html', customers=customers)
            except ValueError:
                flash('Data e hora inválidas!', 'error')
                customers = Customer.query.all()
                return render_template('schedule/new_appointment.html', customers=customers)
            
            appointment = Appointment(
                customer_id=customer_id,
                user_id=current_user.id,
                title=title,
                description=request.form.get('description'),
                appointment_date=appointment_datetime,
                duration_minutes=duration_minutes,
                appointment_type=request.form.get('appointment_type'),
                location=request.form.get('location'),
                notes=request.form.get('notes'),
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('schedule.appointments'))
            
        except ValueError as e:
            flash('Erro: Verifique se os valores estão corretos.', 'error')
            db.session.rollback()
        except Exception as e:
            flash(f'Erro ao criar agendamento: {str(e)}', 'error')
            db.session.rollback()
            print(f"Erro detalhado no agendamento: {e}")
    
    # Buscar todos os clientes, independente do status
    customers = Customer.query.all()
    return render_template('schedule/new_appointment.html', customers=customers)

@schedule_bp.route('/appointments/<int:id>')
@login_required
def appointment_detail(id):
    appointment = Appointment.query.get_or_404(id)
    return render_template('schedule/appointment_detail.html', appointment=appointment)

@schedule_bp.route('/appointments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    if request.method == 'POST':
        appointment.customer_id = request.form.get('customer_id')
        appointment.title = request.form.get('title')
        appointment.description = request.form.get('description')
        appointment.appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%dT%H:%M')
        appointment.duration_minutes = int(request.form.get('duration_minutes', 60))
        appointment.appointment_type = request.form.get('appointment_type')
        appointment.location = request.form.get('location')
        appointment.notes = request.form.get('notes')
        appointment.status = request.form.get('status')
        
        db.session.commit()
        flash('Agendamento atualizado com sucesso!', 'success')
        return redirect(url_for('schedule.appointment_detail', id=appointment.id))
    
    customers = Customer.query.all()
    return render_template('schedule/edit_appointment.html', 
                         appointment=appointment, customers=customers)

@schedule_bp.route('/api/events')
@login_required
def api_events():
    start = request.args.get('start')
    end = request.args.get('end')
    
    events = Event.query.filter(
        Event.user_id == current_user.id,
        Event.start_date >= start,
        Event.end_date <= end
    ).all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'allDay': event.is_all_day,
            'url': url_for('schedule.event_detail', id=event.id)
        })
    
    return jsonify(events_data)

@schedule_bp.route('/api/appointments')
@login_required
def api_appointments():
    start = request.args.get('start')
    end = request.args.get('end')
    
    appointments = Appointment.query.filter(
        Appointment.appointment_date >= start,
        Appointment.appointment_date <= end
    ).all()
    
    appointments_data = []
    for appointment in appointments:
        end_time = appointment.appointment_date + timedelta(minutes=appointment.duration_minutes)
        appointments_data.append({
            'id': appointment.id,
            'title': f"{appointment.title} - {appointment.customer.name}",
            'start': appointment.appointment_date.isoformat(),
            'end': end_time.isoformat(),
            'url': url_for('schedule.appointment_detail', id=appointment.id)
        })
    
    return jsonify(appointments_data)

