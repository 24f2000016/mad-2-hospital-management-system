from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, auth_required, current_user
from flask_security.utils import hash_password
from flask_cors import CORS
from datetime import datetime, date

app = Flask(__name__)

app.config['SECRET_KEY'] = 'iit-madras'
app.config['SECURITY_PASSWORD_SALT'] = 'app-dev-II'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_FLASH_MESSAGES'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_INCLUDE_AUTH_TOKEN_IN_API'] = True



db = SQLAlchemy(app)
CORS(app)



# Database Models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    users = db.relationship('User', secondary=roles_users, back_populates='roles')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    doctor = db.relationship('Doctor', back_populates='user', uselist=False)
    patient = db.relationship('Patient', back_populates='user', uselist=False)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String(), nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, back_populates='users')

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    experience = db.Column(db.String(), nullable=False)
    user = db.relationship('User', back_populates='doctor')
    department = db.relationship('Department', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    dob = db.Column(db.Date())
    sex = db.Column(db.String())
    contact_number = db.Column(db.String())
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_start_timestamp = db.Column(db.DateTime(), nullable=False)
    appointment_end_timestamp = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.String(), default='booked', nullable=False)  # 'booked', 'completed', 'canceled'
    patient = db.relationship('Patient', back_populates='appointments', cascade='all, delete-orphan', single_parent=True)
    doctor = db.relationship('Doctor', back_populates='appointments', cascade='all, delete-orphan', single_parent=True)
    patient_history = db.relationship('PatientHistory', back_populates='appointment', uselist=False)
    
class PatientHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    visit_type = db.Column(db.String()) # 'consultation', 'follow-up', 'emergency'
    test_done = db.Column(db.String())
    diagnosis = db.Column(db.String())
    prescription = db.Column(db.String())
    medicines = db.Column(db.String())
    symptoms = db.Column(db.String())
    follow_up_date = db.Column(db.Date())
    additional_notes = db.Column(db.String())
    appointment = db.relationship('Appointment', back_populates='patient_history', cascade='all, delete-orphan', single_parent=True)

class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    available_date = db.Column(db.Date(), nullable=False)
    morning_slot = db.Column(db.Boolean(), default=False, nullable=False)
    evening_slot = db.Column(db.Boolean(), default=False, nullable=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=True)
    doctors = db.relationship('Doctor', back_populates='department')


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if user_datastore.find_user(email=data['email']):
        return jsonify({"message": "User already exists"}), 400
    
    if user_datastore.find_user(username=data['username']):
        return jsonify({"message": "Username already taken"}), 400

    user = user_datastore.create_user(
        email=data['email'],
        username=data['username'],
        password=hash_password(data['password'])
    )
    patient_role = user_datastore.find_role('patient')
    user_datastore.add_role_to_user(user, patient_role)
    patient = Patient(user_id=user.id)  # Create associated Patient record
    db.session.add(patient)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/current-user-details', methods=['GET'])
@auth_required('token')
def current_user_details():
    return jsonify({
        "current_user_email": current_user.email, 
        "current_user_username": current_user.username,
        "current_user_roles": [role.name for role in current_user.roles]
    })

@app.route('/api/admin-dashboard', methods=['GET'])
@auth_required('token')
def admin_dashboard():
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    if admin_role not in current_user.roles:
        return jsonify({"message": "Unauthorized access"}), 403
    
    # Get patients data
    patients = Patient.query.all()
    patients_data = []
    
    for patient in patients:
        # Calculate age from date of birth
        age = None
        if patient.dob:
            today = date.today()
            age = today.year - patient.dob.year - ((today.month, today.day) < (patient.dob.month, patient.dob.day))
        
        # Count appointments
        appointment_count = len(patient.appointments) if patient.appointments else 0
        
        patients_data.append({
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'full_name': f"{patient.first_name or ''} {patient.last_name or ''}".strip(),
            'age': age,
            'sex': patient.sex,
            'contact_number': patient.contact_number,
            'dob': str(patient.dob) if patient.dob else None,
            'appointment_count': appointment_count,
            'user_email': patient.user.email if patient.user else None
        })
    
    # Get doctors data
    doctors = Doctor.query.all()
    doctors_data = []
    
    for doctor in doctors:
        doctors_data.append({
            'id': doctor.id,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'full_name': f"{doctor.first_name or ''} {doctor.last_name or ''}".strip(),
            'department_id': doctor.department_id,
            'department_name': doctor.department.name if doctor.department else None,
            'experience': doctor.experience,
            'user_email': doctor.user.email if doctor.user else None
        })
    
    # Get departments data
    departments = Department.query.all()
    departments_data = []
    
    for dept in departments:
        departments_data.append({
            'id': dept.id,
            'name': dept.name,
            'description': dept.description
        })
    
    # Get appointments data
    appointments = Appointment.query.all()
    appointments_data = []
    
    for appt in appointments:
        patient_name = f"{appt.patient.first_name or ''} {appt.patient.last_name or ''}".strip() if appt.patient else None
        doctor_name = f"{appt.doctor.first_name or ''} {appt.doctor.last_name or ''}".strip() if appt.doctor else None
        department_name = appt.doctor.department.name if appt.doctor and appt.doctor.department else None
        
        appointments_data.append({
            'id': appt.id,
            'patient_id': appt.patient_id,
            'doctor_id': appt.doctor_id,
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'department_name': department_name,
            'appointment_start_timestamp': appt.appointment_start_timestamp.isoformat() if appt.appointment_start_timestamp else None,
            'appointment_end_timestamp': appt.appointment_end_timestamp.isoformat() if appt.appointment_end_timestamp else None,
            'status': appt.status
        })
    
    return jsonify({
        "patients": patients_data,
        "doctors": doctors_data,
        "departments": departments_data,
        "appointments": appointments_data
    }), 200





@app.route('/api/doctor', methods=['POST', 'GET'])
@auth_required('token')
def manage_doctors():
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    

    if request.method == 'POST':
        if admin_role not in current_user.roles:
            return jsonify({"message": "Unauthorized access"}), 403
        data = request.get_json()

        user = user_datastore.create_user(
            email=data.get('doctor_email'),
            username=data.get('doctor_username'),
            password=hash_password(data.get('doctor_password'))
        )
        user_datastore.add_role_to_user(user, user_datastore.find_role('doctor'))

        doctor = Doctor(
            user_id=user.id,
            first_name=data.get('doctor_first_name', ''),
            last_name=data.get('doctor_last_name', ''),
            department_id=data.get('doctor_department_id'),
            experience=data.get('doctor_experience', '')
        )

        db.session.add(doctor)
        db.session.commit()
        return jsonify({"message": "Doctor added successfully"}), 201
    
    elif request.method == 'GET':
        doctors = Doctor.query.all()
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'first_name': doctor.first_name,
                'last_name': doctor.last_name,
                'full_name': f"{doctor.first_name or ''} {doctor.last_name or ''}".strip(),
                'department': doctor.department.name if doctor.department else None,
                'experience': doctor.experience,
                'email': doctor.user.email if doctor.user else None
            })
        return jsonify({"doctors": doctors_data}), 200

@app.route('/api/doctor/<int:doctor_id>', methods=['PUT'])
@auth_required('token')
def update_doctor(doctor_id):
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    if admin_role not in current_user.roles:
        return jsonify({"message": "Unauthorized access"}), 403
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404
    
    data = request.get_json()
    
    # Update doctor's personal info
    if data.get('first_name'):
        doctor.first_name = data.get('first_name')
    if data.get('last_name'):
        doctor.last_name = data.get('last_name')
    if data.get('experience'):
        doctor.experience = data.get('experience')
    if data.get('department_id'):
        doctor.department_id = data.get('department_id')
    
    # Update user's email and username if provided
    if data.get('email'):
        doctor.user.email = data.get('email')
    if data.get('username'):
        doctor.user.username = data.get('username')
    
    db.session.commit()
    return jsonify({"message": "Doctor updated successfully"}), 200



@app.route('/api/patient', methods=['POST', 'GET'])
@auth_required('token')
def manage_patients():
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    
    if request.method == 'POST':
        if admin_role not in current_user.roles:
            return jsonify({"message": "Unauthorized access"}), 403
        data = request.get_json()

        # Check if user already exists
        if user_datastore.find_user(email=data.get('patient_email')):
            return jsonify({"message": "Email already exists"}), 400
        
        if user_datastore.find_user(username=data.get('patient_username')):
            return jsonify({"message": "Username already taken"}), 400

        # Create user for patient
        user = user_datastore.create_user(
            email=data.get('patient_email'),
            username=data.get('patient_username'),
            password=hash_password(data.get('patient_password'))
        )
        user_datastore.add_role_to_user(user, user_datastore.find_role('patient'))

        # Parse date of birth
        dob = None
        if data.get('patient_dob'):
            try:
                dob = datetime.strptime(data.get('patient_dob'), '%Y-%m-%d').date()
            except:
                return jsonify({"message": "Invalid date format for DOB"}), 400

        # Create patient record
        patient = Patient(
            user_id=user.id,
            first_name=data.get('patient_first_name', ''),
            last_name=data.get('patient_last_name', ''),
            dob=dob,
            sex=data.get('patient_sex', ''),
            contact_number=data.get('patient_contact_number', '')
        )

        db.session.add(patient)
        db.session.commit()
        return jsonify({"message": "Patient added successfully"}), 201
    
    elif request.method == 'GET':
        patients = Patient.query.all()
        patients_data = []
        for patient in patients:
            # Calculate age from date of birth
            age = None
            if patient.dob:
                today = date.today()
                age = today.year - patient.dob.year - ((today.month, today.day) < (patient.dob.month, patient.dob.day))
            
            patients_data.append({
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'age': age,
                'sex': patient.sex,
                'contact_number': patient.contact_number,
                'dob': str(patient.dob) if patient.dob else None,
                'email': patient.user.email if patient.user else None
            })
        return jsonify({"patients": patients_data}), 200



@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
@auth_required('token')
def update_patient(patient_id):
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    if admin_role not in current_user.roles:
        return jsonify({"message": "Unauthorized access"}), 403
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404
    
    data = request.get_json()
    
    # Update patient's personal info
    if data.get('full_name'):
        full_name = data.get('full_name').strip().split(' ', 1)
        patient.first_name = full_name[0] if full_name else ''
        patient.last_name = full_name[1] if len(full_name) > 1 else ''
    if data.get('sex'):
        patient.sex = data.get('sex')
    if data.get('dob'):
        try:
            patient.dob = datetime.strptime(data.get('dob'), '%Y-%m-%d').date()
        except:
            return jsonify({"message": "Invalid date format"}), 400
    if data.get('contact_number'):
        patient.contact_number = data.get('contact_number')
    
    # Update user's email if provided
    if data.get('user_email'):
        patient.user.email = data.get('user_email')
    
    db.session.commit()
    return jsonify({"message": "Patient updated successfully"}), 200



@app.route('/api/departments', methods=['GET', 'POST'])
@auth_required('token')
def manage_departments():
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    if admin_role not in current_user.roles:
        return jsonify({"message": "Unauthorized access"}), 403

    if request.method == 'GET':
        departments = Department.query.all()
        departments_data = [{
            'id': dept.id, 
            'name': dept.name, 
            'description': dept.description} for dept in departments]
        return jsonify({"departments": departments_data}), 200

    elif request.method == 'POST':
        data = request.get_json()
        if not data.get('name'):
            return jsonify({"message": "Department name is required"}), 400
        
        if Department.query.filter_by(name=data['name']).first():
            return jsonify({"message": "Department already exists"}), 400

        new_department = Department(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(new_department)
        db.session.commit()
        return jsonify({"message": "Department added successfully"}), 201




@app.route('/api/profile', methods=['PUT'])
@auth_required('token')
def profile():
    data = request.get_json()

    # Update user details
    if data.get('username'):
        current_user.username = data.get('username', current_user.username)
    patient_role = user_datastore.find_role('patient')
    user_datastore.add_role_to_user(current_user, patient_role)
    if data.get('email'):
        current_user.email = data.get('email', current_user.email)
    if data.get('password'):
        current_user.password = hash_password(data.get('password'))

    patient = current_user.patient or Patient(user_id=current_user.id)
    
    if data.get('first_name'):
        patient.first_name = data.get('first_name', patient.first_name)
    if data.get('last_name'):
        patient.last_name = data.get('last_name', patient.last_name)
    if data.get('sex'):
        patient.sex = data.get('sex', patient.sex)
    if data.get('dob'):
        patient.dob = datetime.strptime(data.get('dob', patient.dob), '%Y-%m-%d').date()
    if data.get('contact_number'):
        patient.contact_number = data.get('contact_number', patient.contact_number)
    db.session.add(patient)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})




@app.route('/api/appointment', methods=['POST', 'GET'])
@auth_required('token')
def manage_appointments():
    if request.method == 'POST':
        data = request.get_json()
        patient = current_user.patient
        if not patient:
            return jsonify({"message": "Current user is not a patient"}), 400
        
        doctor = Doctor.query.get(data.get('doctor_id'))
        if not doctor:
            return jsonify({"message": "Doctor not found"}), 404

        try:
            start_timestamp = datetime.fromisoformat(data.get('appointment_start_timestamp'))
            end_timestamp = datetime.fromisoformat(data.get('appointment_end_timestamp'))
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid timestamp format"}), 400

        new_appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_start_timestamp=start_timestamp,
            appointment_end_timestamp=end_timestamp,
            status='booked'
        )
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({"message": "Appointment scheduled successfully", "appointment_id": new_appointment.id}), 201
    
    elif request.method == 'GET':
        
        all_appointments = Appointment.query.all()
        appointments_data = []
        for appt in all_appointments:
            appointments_data.append({
                'id': appt.id,
                'doctor_id': appt.doctor_id,
                'patient_id': appt.patient_id,
                'patient_name': f"{appt.patient.first_name or ''} {appt.patient.last_name or ''}".strip() if appt.patient else None,
                'doctor_name': f"{appt.doctor.first_name or ''} {appt.doctor.last_name or ''}".strip() if appt.doctor else None,
                'doctor_email': appt.doctor.user.email if appt.doctor and appt.doctor.user else None,
                'department': appt.doctor.department.name if appt.doctor and appt.doctor.department else None,
                'appointment_start_timestamp': appt.appointment_start_timestamp.isoformat() if appt.appointment_start_timestamp else None,
                'appointment_end_timestamp': appt.appointment_end_timestamp.isoformat() if appt.appointment_end_timestamp else None,
                'status': appt.status
            })
        return jsonify({"appointments": appointments_data}), 200

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
@auth_required('token')
def update_appointment(appointment_id):
    # Check if current user is admin
    admin_role = user_datastore.find_role('admin')
    if admin_role not in current_user.roles:
        return jsonify({"message": "Unauthorized access"}), 403
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    data = request.get_json()
    
    # Update appointment timestamps if provided
    if data.get('appointment_start_timestamp'):
        try:
            appointment.appointment_start_timestamp = datetime.fromisoformat(data.get('appointment_start_timestamp'))
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid start timestamp format"}), 400
    
    if data.get('appointment_end_timestamp'):
        try:
            appointment.appointment_end_timestamp = datetime.fromisoformat(data.get('appointment_end_timestamp'))
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid end timestamp format"}), 400
    
    # Update status if provided
    if data.get('status'):
        valid_statuses = ['booked', 'completed', 'canceled']
        if data.get('status') not in valid_statuses:
            return jsonify({"message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        appointment.status = data.get('status')
    
    db.session.commit()
    return jsonify({"message": "Appointment updated successfully"}), 200

@app.route('/api/appointment/available-slots/<int:doctor_id>/<date_str>', methods=['GET'])
@auth_required('token')
def get_available_slots(doctor_id, date_str):
    """Get available appointment slots for a doctor on a specific date (10-minute intervals)"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404
    
    # Get all booked appointments for this doctor on this date
    booked_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_start_timestamp >= datetime.combine(target_date, datetime.min.time()),
        Appointment.appointment_start_timestamp < datetime.combine(target_date + __import__('datetime').timedelta(days=1), datetime.min.time())
    ).all()
    
    available_slots = []
    
    # Generate 10-minute slots from 09:00 to 19:00, excluding lunch 14:30-15:00
    current_time = datetime.combine(target_date, __import__('datetime').time(9, 0))
    end_time = datetime.combine(target_date, __import__('datetime').time(19, 0))
    lunch_start = datetime.combine(target_date, __import__('datetime').time(14, 30))
    lunch_end = datetime.combine(target_date, __import__('datetime').time(15, 0))
    
    while current_time < end_time:
        # Skip lunch break
        if lunch_start <= current_time < lunch_end:
            current_time += __import__('datetime').timedelta(minutes=10)
            continue
        
        slot_end = current_time + __import__('datetime').timedelta(minutes=10)
        
        # Skip if slot end goes into lunch break
        if current_time < lunch_start and slot_end > lunch_start:
            current_time += __import__('datetime').timedelta(minutes=10)
            continue
        
        # Check if this slot is already booked (max 1 patient per slot)
        slot_booked = any(appt.appointment_start_timestamp == current_time for appt in booked_appointments)
        
        if not slot_booked:
            start_time_str = current_time.strftime('%H:%M')
            end_time_str = slot_end.strftime('%H:%M')
            
            available_slots.append({
                'start_time': start_time_str,
                'end_time': end_time_str,
                'start_timestamp': current_time.isoformat(),
                'end_timestamp': slot_end.isoformat(),
                'available': True
            })
        
        current_time += __import__('datetime').timedelta(minutes=10)
    
    return jsonify({"available_slots": available_slots}), 200



# Setup Database and Create admin User
with app.app_context():
    db.create_all()
    
    # Create roles if they don't exist
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin', description='Administrator')
    if not user_datastore.find_role('patient'):
        user_datastore.create_role(name='patient', description='Patient')
    if not user_datastore.find_role('doctor'):
        user_datastore.create_role(name='doctor', description='Doctor')
    
    db.session.commit()
    
    # Create test admin user if it doesn't exist
    if not user_datastore.find_user(email="admin@ndch.org"):
        user_datastore.create_user(
            email="admin@ndch.org",
            username="admin",
            password=hash_password("admin1234")
        )
        db.session.commit()

        user = user_datastore.find_user(email="admin@ndch.org")
        admin_role = user_datastore.find_role('admin')
        user_datastore.add_role_to_user(user, admin_role)

        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)