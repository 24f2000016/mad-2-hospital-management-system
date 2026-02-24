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
    full_name = db.Column(db.String(), nullable=False)
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
    appointment_date = db.Column(db.DateTime(), nullable=False)
    appointment_time_slot = db.Column(db.String(), nullable=False)
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
    
    return jsonify({"patients": patients_data}), 200





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
            full_name=data.get('doctor_full_name', ''),
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
                'full_name': doctor.full_name,
                'department': doctor.department.name if doctor.department else None,
                'experience': doctor.experience,
                'email': doctor.user.email if doctor.user else None
            })
        return jsonify({"doctors": doctors_data}), 200






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