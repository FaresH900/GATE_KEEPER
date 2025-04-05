from app import create_app
from app.models.user import User
from app.extensions import db

def create_test_users():
    app = create_app()
    with app.app_context():
        # Create admin user
        admin = User.query.filter_by(email='hossam@admin.com').first()
        if not admin:
            admin = User(
                email='hossam@admin.com',
                name='Admin User',
                role='ADMIN'
            )
            admin.set_password('password123')
            db.session.add(admin)
            
        # Create test resident
        resident = User.query.filter_by(email='hossam@resident.com').first()
        if not resident:
            resident = User(
                email='hossam@resident.com',
                name='Resident User',
                role='RESIDENT'
            )
            resident.set_password('password123')
            db.session.add(resident)
        
        db.session.commit()
        print("Test users created successfully")

if __name__ == "__main__":
    create_test_users()