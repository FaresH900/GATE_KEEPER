from app.extensions import db, bcrypt
from enum import Enum
import base64

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    RESIDENT = 'RESIDENT'
    GATEKEEPER = 'GATEKEEPER'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum(UserRole), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Define the one-to-one relationship with Resident
    resident = db.relationship('Resident', backref=db.backref('user', uselist=False), uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role
        }

class Resident(db.Model):
    __tablename__ = 'residents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    face_data_ref = db.Column(db.LargeBinary, nullable=True)
    face_image = db.Column(db.LargeBinary, nullable=True)

    # Relationships
    homes = db.relationship('Home', backref='resident', lazy=True)
    cars = db.relationship('Car', backref='resident', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'has_face_data': self.face_data_ref is not None,
            'face_image': base64.b64encode(self.face_image).decode('utf-8') if self.face_image else None,
            'homes': [{
                'id': home.id,
                'section': home.home_section,
                'number': home.home_num,
                'apartment': home.home_appart
            } for home in self.homes],
            'cars': [{
                'id': car.id,
                'license_plate': car.license_plate
            } for car in self.cars]
        }

class Car(db.Model):
    __tablename__ = 'cars'
    
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)
    license_plate = db.Column(db.String(50), unique=True)

class Home(db.Model):
    __tablename__ = 'home'
    
    id = db.Column(db.Integer, primary_key=True)
    home_section = db.Column(db.String(20))
    home_num = db.Column(db.String(20))
    home_appart = db.Column(db.String(20))
    res_id = db.Column(db.Integer, db.ForeignKey('residents.id'), nullable=False)