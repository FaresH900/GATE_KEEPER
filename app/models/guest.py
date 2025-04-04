from app.extensions import db
from datetime import datetime, timedelta
import pickle
import numpy as np
from enum import Enum

# Define GuestStatus first
class GuestStatus(Enum):
    PENDING = 'pending'
    ALLOWED = 'allowed'

# Then use it in the models
class GuestInvitation(db.Model):
    __tablename__ = 'guest_invitation'
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(GuestStatus), default=GuestStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Guest(db.Model):
    __tablename__ = 'guest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Add relationships
    invitations = db.relationship('GuestInvitation', backref='guest', lazy=True)
    history = db.relationship('GuestHistory', backref='guest', lazy=True)

    @staticmethod
    def add_guest(name, embedding, invitation_end_date=None):
        # Check for existing face matches
        existing_guests = Guest.query.all()
        
        for guest in existing_guests:
            stored_embedding = pickle.loads(guest.embedding)
            distance = np.linalg.norm(embedding - stored_embedding)
            
            if distance < 0.8:  # Your threshold
                # Create new invitation for existing guest
                if invitation_end_date:
                    new_invitation = GuestInvitation(
                        guest_id=guest.id,
                        end_date=invitation_end_date,
                        status=GuestStatus.PENDING
                    )
                    db.session.add(new_invitation)
                    db.session.commit()
                    return {
                        'status': 'exists',
                        'message': 'New invitation created for existing guest',
                        'guest': guest,
                        'invitation': new_invitation
                    }
                return {
                    'status': 'exists',
                    'message': 'Person already registered',
                    'guest': guest
                }

        # If no match found, create new guest and invitation
        new_guest = Guest(name=name, embedding=pickle.dumps(embedding))
        db.session.add(new_guest)
        db.session.flush()  # Get the new guest ID

        if invitation_end_date:
            new_invitation = GuestInvitation(
                guest_id=new_guest.id,
                end_date=invitation_end_date,
                status=GuestStatus.PENDING
            )
            db.session.add(new_invitation)
        
        db.session.commit()
        return {
            'status': 'new',
            'message': 'New guest registered with invitation',
            'guest': new_guest
        }

    def get_current_invitation(self):
        """Get the current valid invitation if any"""
        now = datetime.now()
        return GuestInvitation.query.filter(
            GuestInvitation.guest_id == self.id,
            GuestInvitation.start_date <= now,
            GuestInvitation.end_date >= now
        ).first()

    def update_invitation_status(self, invitation_id, new_status):
        invitation = GuestInvitation.query.get(invitation_id)
        if not invitation:
            return False, "Invitation not found"
        
        if invitation.status == GuestStatus.ALLOWED and new_status == GuestStatus.ALLOWED:
            return False, "Already allowed for this invitation"
            
        invitation.status = new_status
        if new_status == GuestStatus.ALLOWED:
            history = GuestHistory(guest_id=self.id, invitation_id=invitation.id)
            db.session.add(history)
        db.session.commit()
        return True, "Status updated successfully"

class GuestHistory(db.Model):
    __tablename__ = 'guest_history'
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    invitation_id = db.Column(db.Integer, db.ForeignKey('guest_invitation.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())