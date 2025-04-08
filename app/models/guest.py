from app.extensions import db
from datetime import datetime, timedelta
import pickle
import numpy as np
from enum import Enum
import base64  # Add this import for image encoding

class GuestStatus(Enum):
    PENDING = 'PENDING'
    ALLOWED = 'ALLOWED'

class GuestInvitation(db.Model):
    __tablename__ = 'guest_invitation'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(GuestStatus), default=GuestStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }

class Guest(db.Model):
    __tablename__ = 'guest'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.LargeBinary, nullable=False)
    face_image = db.Column(db.LargeBinary, nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('residents.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    resident = db.relationship('Resident', backref=db.backref('guests', lazy=True))
    invitations = db.relationship('GuestInvitation', backref='guest', lazy=True, cascade='all, delete-orphan')
    history = db.relationship('GuestHistory', backref='guest', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        current_invitation = self.get_current_invitation()
        return {
            'id': self.id,
            'name': self.name,
            'face_image': base64.b64encode(self.face_image).decode('utf-8') if self.face_image else None,
            'created_at': self.created_at.isoformat(),
            'resident': self.resident.to_dict() if self.resident else None,
            'current_invitation': current_invitation.to_dict() if current_invitation else None,
            'all_invitations': [inv.to_dict() for inv in self.invitations],
            'history': [h.to_dict() for h in self.history]
        }

    @staticmethod
    def add_guest(name, embedding, face_image, resident_id, invitation_end_date=None):
        """
        Add a new guest with face embedding and image
        """
        try:
            # Check for existing face matches
            existing_guests = Guest.query.all()
            
            for guest in existing_guests:
                stored_embedding = pickle.loads(guest.embedding)
                distance = np.linalg.norm(embedding - stored_embedding)
                
                if distance < 0.8:  # Threshold for face matching
                    # Create new invitation for existing guest if needed
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

            # Create new guest with face image
            new_guest = Guest(
                name=name,
                embedding=pickle.dumps(embedding),
                face_image=face_image,
                resident_id=resident_id
            )
            db.session.add(new_guest)
            db.session.flush()

            # Create invitation if end date provided
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
                'message': 'New guest registered successfully',
                'guest': new_guest
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error adding guest: {str(e)}")

    def get_current_invitation(self):
        """Get the current valid invitation if any"""
        now = datetime.now()
        return GuestInvitation.query.filter(
            GuestInvitation.guest_id == self.id,
            GuestInvitation.start_date <= now,
            GuestInvitation.end_date >= now
        ).order_by(GuestInvitation.created_at.desc()).first()

    def update_invitation_status(self, invitation_id, new_status):
        """Update invitation status and create history entry"""
        invitation = GuestInvitation.query.get(invitation_id)
        if not invitation or invitation.guest_id != self.id:
            return False, "Invalid invitation"
        
        if invitation.status == new_status:
            return False, f"Invitation already {new_status.value}"
            
        invitation.status = new_status
        if new_status == GuestStatus.ALLOWED:
            history = GuestHistory(guest_id=self.id, invitation_id=invitation.id)
            db.session.add(history)
        db.session.commit()
        return True, "Status updated successfully"

class GuestHistory(db.Model):
    __tablename__ = 'guest_history'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', ondelete='CASCADE'), nullable=False)
    invitation_id = db.Column(db.Integer, db.ForeignKey('guest_invitation.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'guest_id': self.guest_id,
            'invitation_id': self.invitation_id,
            'timestamp': self.timestamp.isoformat()
        }