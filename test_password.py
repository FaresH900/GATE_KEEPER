from app import create_app
from app.extensions import bcrypt
from app.models.user import User
from app.extensions import db

app = create_app()

with app.app_context():
    # Create test user
    test_password = "password123"
    hashed = bcrypt.generate_password_hash(test_password).decode('utf-8')
    print(f"Test password: {test_password}")
    print(f"Generated hash: {hashed}")
    
    # Verify existing user
    user = User.query.filter_by(email='hossam@admin.com').first()
    if user:
        print(f"\nExisting user: {user.email}")
        print(f"Stored hash: {user.password_hash}")
        print(f"Password check result: {user.check_password('password123')}")