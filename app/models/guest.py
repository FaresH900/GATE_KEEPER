from app.extensions import db
from datetime import datetime
import pickle
import numpy as np
from enum import Enum

class GuestStatus(Enum):
    PENDING = 'pending'
    ALLOWED = 'allowed'

class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)
    status = db.Column(db.Enum(GuestStatus), default=GuestStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Add relationship to GuestHistory
    history = db.relationship('GuestHistory', backref='guest', lazy=True)

    @staticmethod
    def add_guest(name, embedding):
        # Check for existing pending guests
        existing_guests = Guest.query.all()
        
        for guest in existing_guests:
            stored_embedding = pickle.loads(guest.embedding)
            distance = np.linalg.norm(embedding - stored_embedding)
            
            if distance < 0.8:  # Your threshold
                if guest.status == GuestStatus.PENDING:
                    return {'status': 'exists', 'message': 'Person already registered and pending', 'guest': guest}
                else:
                    # Add to history and return existing guest
                    history = GuestHistory(guest_id=guest.id)
                    db.session.add(history)
                    db.session.commit()
                    return {
                        'status': 'allowed',
                        'message': 'Person already allowed',
                        'guest': guest,
                        'history': guest.history
                    }

        # If no match found, create new guest
        new_guest = Guest(name=name, embedding=pickle.dumps(embedding))
        db.session.add(new_guest)
        db.session.commit()
        return {'status': 'new', 'message': 'New guest registered', 'guest': new_guest}

    @staticmethod
    def find_match(test_embedding, threshold=0.8):
        guests = Guest.query.all()
        min_distance = float('inf')
        best_match = None

        for guest in guests:
            stored_embedding = pickle.loads(guest.embedding)
            distance = np.linalg.norm(test_embedding - stored_embedding)
            if distance < min_distance:
                min_distance = distance
                best_match = guest

        if min_distance < threshold and best_match:
            return best_match, min_distance
        return None, min_distance

    def update_status(self, new_status):
        # If already allowed and trying to set allowed again, just return False
        if self.status == GuestStatus.ALLOWED and new_status == GuestStatus.ALLOWED:
            return False

        self.status = new_status
        if new_status == GuestStatus.ALLOWED:
            # Add new history entry
            history = GuestHistory(guest_id=self.id)
            db.session.add(history)
        db.session.commit()
        return True

class GuestHistory(db.Model):
    __tablename__ = 'guest_history'
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())