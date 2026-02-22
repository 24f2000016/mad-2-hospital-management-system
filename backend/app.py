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