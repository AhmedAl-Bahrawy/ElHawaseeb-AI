from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed , FileField
from wtforms import StringField, PasswordField, SubmitField ,EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from tokenize import String
from flask_login import current_user
from sites.models import User


class SignupForm(FlaskForm):
    fullname = StringField("الاسم الكامل", validators=[DataRequired(), Length(min=3, max=30)], render_kw={"placeholder": "أدخل اسمك الكامل"})
    username = StringField("اسم المستخدم", validators=[DataRequired(), Length(min=3, max=30)], render_kw={"placeholder": "أدخل اسم المستخدم"})
    email_or_phone = StringField("رقم الهاتف او البريد الالكتروني", validators=[Length(min=3, max=100)], render_kw={"placeholder": "أدخل بريدك الإلكتروني او رقم الهاتف"})
    password = PasswordField("كلمة المرور", validators=[DataRequired(), Length(min=3, max=30)], render_kw={"placeholder": "أدخل كلمة المرور"})
    confirmpassword = PasswordField("تأكيد كلمة المرور", validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "أكد كلمة المرور"})
    submit = SubmitField("إنشاء حساب")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("اسم المستخدم هذا مسجل بالفعل من فضلك اختر اسم مستخدم اخر")

    def validate_email_or_phone(self, email_or_phone):
        if email_or_phone.data:
            user = User.query.filter_by(email_or_phone=email_or_phone.data).first()
            if user:
                raise ValidationError(" هذا الايميل او رقم الهاتف موجود بالفعل من فضلك ادخل ايميل اخر")


        
class SellerSetupForm(FlaskForm):
    store_name = StringField('اسم المتجر', validators=[DataRequired()])
    store_location = StringField('موقع المتجر', validators=[DataRequired()])
    phone_number = StringField('رقم الهاتف', validators=[DataRequired()])
    product_description = TextAreaField('وصف المنتجات')
    submit = SubmitField('حفظ المعلومات')

    
class LoginForm(FlaskForm):
    email_or_phone = EmailField("رقم الهاتف او البريد الالكتروني", validators=[DataRequired(), Length(min=3, max=100)], render_kw={"placeholder": "أدخل بريدك الإلكتروني"})
    password = PasswordField("كلمة المرور", validators=[DataRequired(), Length(min=3, max=30)], render_kw={"placeholder": "أدخل كلمة المرور"})
    remember = BooleanField('تذكرني')
    submit = SubmitField("تسجيل الدخول")
    
    def validate_email(self, email_or_phone):
        if email_or_phone.data:
            user = User.query.filter_by(email_or_phone=email_or_phone.data).first()
            if user:
                raise ValidationError(" هذا الايميل او رقم الهاتف موجود بالفعل من فضلك ادخل ايميل اخر")
        
class UpdateProfileForm(FlaskForm):
    username = StringField('اسم المستخدم',
                           validators=[DataRequired(), Length(min=2, max=30)])
    email_or_phone = StringField('البريد الإلكتروني',
                        validators=[DataRequired(), Email()])
    image = FileField('تحديث صورة الملف الشخصي', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'svg', 'tiff', 'ico'])])
    submit = SubmitField('تحديث المعلومات')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('اسم المستخدم هذا مأخوذ بالفعل. الرجاء اختيار اسم آخر.')

    def validate_email(self, email_or_phone):
        if email_or_phone.data != current_user.email_or_phone:
            user = User.query.filter_by(email_or_phone=email_or_phone.data).first()
            if user:
                raise ValidationError('البريد الإلكتروني هذا مأخوذ بالفعل. الرجاء اختيار بريد إلكتروني آخر.')

class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField("كلمة المرور الحالية", validators=[DataRequired()])
    new_password = PasswordField("كلمة المرور الجديدة", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("تأكيد كلمة المرور الجديدة", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("تغيير كلمة المرور")
    
class RequestResetForm(FlaskForm):
    email_or_phone = StringField('البريد الالكتروني', validators=[DataRequired(), Email()])
    submit = SubmitField('ارسال')
    
    def validate_email(self, email_or_phone):
        user = User.query.filter_by(email_or_phone=email_or_phone.data).first()
        if not user:
            raise ValidationError("هذا االايميل غير موجود لدينا من فضلك استخدم ايميل اخر")

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("كلمة المرور الجديدة", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("تأكيد كلمة المرور الجديدة", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("تغيير كلمة المرور")