""" To avoid relative imports, create a new file exts.py and import sqlalchemy class there and 
    create a db instance. Do not specify the db variable so that it becomes a global variable
    so that it can be accessed from other parts in the code.
"""

from exts import db
import datetime

class users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(10), unique = True, nullable = False)
    f_name= db.Column(db.String(30))
    l_name = db.Column(db.String(30))
    county = db.Column(db.String(25))
    town = db.Column(db.String(25))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.phone_number}>'

    #Convenience Methods

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    #Class Methods

    @classmethod
    def get_by_phone_number(cls, phone_number):
        return cls.query.filter_by(phone_number=phone_number).first()
    


class paymentplans(db.Model):
    __tablename__ = 'paymentplans'
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    installment_amount = db.Column(db.Integer, nullable=False)
    number_of_installments = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_flexible = db.Column(db.Boolean, default=False)  # Indicates if it's a flexible plan

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

class flexibleplans(db.Model):
    __tablename__ = 'flexibleplans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    agreed_installment_amount = db.Column(db.Integer, nullable=False)
    number_of_installments = db.Column(db.Integer, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)  # User-defined duration
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    user = db.relationship('users', back_populates='flexibleplans')


class payments(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('paymentplans.id'), nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.DateTime)
    payment_status = db.Column(db.String(50), default="pending")


    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()


class installmentschedules(db.Model):
    __tablename__ = 'installmentschedules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('paymentplans.id'), nullable=False)
    installment_due_date = db.Column(db.Date, nullable=False)
    installment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="unpaid")


    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

class complaints(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="open")
    submission_date = db.Column(db.DateTime, default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

class transactionhistory(db.Model):
    __tablename__ = 'transactionhistory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.now())
    transaction_type = db.Column(db.String(50), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

# class Agent(db.Model):
#     __tablename__ = 'agents'
#     id = db.Column(db.Integer, primary_key=True)
#     agent_name = db.Column(db.String(100), nullable=False)
#     location = db.Column(db.String(100), nullable=False)
#     contact_info = db.Column(db.String(100), nullable=False)
