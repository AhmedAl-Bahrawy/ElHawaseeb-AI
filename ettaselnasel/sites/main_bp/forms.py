from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email
from tokenize import String


class ContactForm(FlaskForm):
    name = StringField('الاسم الكامل', validators=[DataRequired()])
    email_or_phone = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    subject = StringField('الموضوع', validators=[DataRequired()])
    message = TextAreaField('الرسالة', validators=[DataRequired()] )
    submit = SubmitField('إرسال')