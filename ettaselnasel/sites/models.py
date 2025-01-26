from sites import db, login_manager
from sqlalchemy.orm import validates
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email_or_phone = db.Column(db.String(125), unique=True, nullable=False)  # أصبح اختياريًا
    password = db.Column(db.String(30), nullable=False)
    image_file = db.Column(db.String(60), nullable=False, default="default_user.jpg")
    product = db.relationship('Product', backref='author', lazy=True)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    user_type = db.Column(db.String(10), nullable=False, default='customer')
    
    # New fields for sellers
    store_name = db.Column(db.String(100))
    store_location = db.Column(db.String(200))
    store_phone_number = db.Column(db.String(20))  # رقم هاتف المتجر
    product_description = db.Column(db.Text)

    @validates('email_or_phone')
    def validate_email_or_phone(self, key, email_or_phone):
        if email_or_phone and len(email_or_phone) < 3:
            raise ValueError("البريد الإلكتروني غير صحيح")
        return email_or_phone
    
    def get_pw_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_pw_reset_token(token, age=600):
        s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
        try:
            user_id = s.loads(token, max_age=age)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def get_confirm_email_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], salt='email_or_phone-confirm')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_confirm_email_token(token, max_age=3600):
        s = Serializer(current_app.config['SECRET_KEY'], salt='email_or_phone-confirm')
        try:
            user_id = s.loads(token, max_age=max_age)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_confirm_phone_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], salt='email_or_phone-confirm')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_confirm_phone_token(token, max_age=3600):
        s = Serializer(current_app.config['SECRET_KEY'], salt='email_or_phone-confirm')
        try:
            user_id = s.loads(token, max_age=max_age)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.username}')"

    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=False, default="default_product.jpg")
    slug = db.Column(db.String(32), nullable=False)
    price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    is_discount = db.Column(db.Boolean, nullable=False, default=False)
    discount = db.Column(db.Integer, default=10)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_posted}')"
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(70), nullable=False)
    icon = db.Column(db.String(100), nullable=False, default="default_product.jpg")
    product = db.relationship('Product', backref='cat', lazy=True)
