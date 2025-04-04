from app.extensions import db, bcrypt
from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    RESIDENT = 'resident'
    GATEKEEPER = 'gatekeeper'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum(UserRole), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship
    resident = db.relationship('Resident', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')


    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role.value,
            'name': self.name,
            'email': self.email
        }

class Resident(db.Model):
    __tablename__ = 'residents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    face_data_ref = db.Column(db.String(255))
    
    # Relationships
    homes = db.relationship('Home', backref='resident')
    cars = db.relationship('Car', backref='resident')

class Home(db.Model):
    __tablename__ = 'home'
    
    id = db.Column(db.Integer, primary_key=True)
    home_section = db.Column(db.String(20))
    home_num = db.Column(db.String(20))
    home_appart = db.Column(db.String(20))
    res_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)

class Car(db.Model):
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'))
    license_plate = db.Column(db.String(50), unique=True)