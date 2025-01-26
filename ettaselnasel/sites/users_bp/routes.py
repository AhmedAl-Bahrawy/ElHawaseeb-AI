from flask import render_template, url_for, flash, redirect, request, Blueprint
from sites.users_bp.forms import SignupForm, LoginForm, UpdateProfileForm, UpdatePasswordForm, RequestResetForm, ResetPasswordForm, SellerSetupForm
from sites import db
from sites.models import User, Product
from flask_login import login_user, current_user, logout_user, login_required
from sites.helpers import save_picture, delete_picture, send_email, send_sms

users_bp = Blueprint('users', __name__) 


@users_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = SignupForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        user = User(
            fullname=form.fullname.data,
            username=form.username.data,
            email_or_phone=form.email_or_phone.data,  # استقبال رقم الهاتف أو البريد
            password=form.password.data
        )
        
        # إضافة المستخدم لقاعدة البيانات
        db.session.add(user)
        db.session.commit()

        # إرسال البريد الإلكتروني أو رسالة SMS بناءً على المدخل
        if '@' in user.email_or_phone:  # إذا كان بريد إلكتروني
            send_email(user, condition="confirm_email")
        else:
            pass# إذا كان رقم هاتف
            #send_sms(user, condition="confirm_phone")
        
        flash("تم إنشاء الحساب بنجاح. يرجى التحقق من بريدك الإلكتروني أو رقم هاتفك لتأكيد الحساب.", 'success')
        logout_user()  # تسجيل خروج المستخدم بعد التسجيل
        return redirect(url_for('users.activation_info'))
    
    return render_template('signup.html', title="إنشاء حساب", form=form)

@users_bp.route('/activation-info', methods=['GET'])
def activation_info():
    return render_template('activation_info.html', title="تأكيد البريد الإلكتروني")

# تأكيد البريد الإلكتروني
@users_bp.route('/confirm-email/<token>')
def confirm_email(token):
    user = User.verify_confirm_email_token(token)
    if user is None:
        flash('رابط التفعيل غير صالح أو منتهي الصلاحية.', 'danger')
        return redirect(url_for('users.signup'))
    
    if user.is_confirmed:
        flash('بريدك الإلكتروني قد تم تأكيده مسبقًا.', 'info')
    else:
        user.is_confirmed = True
        db.session.commit()
        login_user(user, remember=True)
        flash('تم تأكيد بريدك الإلكتروني بنجاح! اختر دورك الآن.', 'success')
        return redirect(url_for('users.choose_role'))

# تأكيد رقم الهاتف
@users_bp.route('/confirm-phone/<token>')
def confirm_phone(token):
    user = User.verify_confirm_phone_token(token)
    if user is None:
        flash('رابط التفعيل غير صالح أو منتهي الصلاحية.', 'danger')
        return redirect(url_for('users.signup'))
    
    if user.is_confirmed:
        flash('رقم هاتفك قد تم تأكيده مسبقًا.', 'info')
    else:
        user.is_confirmed = True
        db.session.commit()
        flash('تم تأكيد رقم هاتفك بنجاح!', 'success')
    
    return redirect(url_for('main.home'))

@users_bp.route('/resend-confirmation', methods=['GET'])
def resend_confirmation():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    if not current_user.is_confirmed:
        if '@' in current_user.email_or_phone:
            send_email(current_user, condition="confirm_email")
        else :
            pass
            #send_sms(current_user, condition="confirm_phone")
        flash('تمت إعادة إرسال رسالة تأكيد البريد الإلكتروني أو رسالة تفعيل رقم الهاتف بنجاح.', 'info')
    else:
        flash('حسابك مفعل بالفعل.', 'info')
    
    return redirect(url_for('users.activation_info'))

@users_bp.route('/setup-seller', methods=['GET', 'POST'])
def setup_seller():
    if not current_user.is_authenticated or not current_user.is_confirmed:
        return redirect(url_for('users.login'))

    form = SellerSetupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.store_name = form.store_name.data
            current_user.store_location = form.store_location.data
            current_user.store_phone_number = form.phone_number.data
            current_user.product_description = form.product_description.data
            current_user.user_type = 'seller'
            db.session.commit()
            flash('تم تحديث معلومات متجرك بنجاح!', 'success')
            return redirect(url_for('main.home'))

    return render_template('setup_seller.html', title="إعداد التاجر", form=form)

@users_bp.route('/choose-role', methods=['GET', 'POST'])
def choose_role():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'customer':
            return redirect(url_for('main.home'))
        elif role == 'seller':
            return redirect(url_for('users.setup_seller'))
        else:
            flash('يرجى اختيار دور صحيح.', 'danger')

    return render_template('choose_role.html', title="اختر دورك")

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email_or_phone=form.email_or_phone.data).first()
            if user and form.password.data == user.password:  # تحقق من كلمة المرور (يفضل استخدام hash للتحقق)
                if user.is_confirmed:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash("لقد تم تسجيل دخولك بنجاح", 'success')
                    return redirect(next_page) if next_page else redirect(url_for('main.home'))
                else:
                    flash('هذا البريد الإلكتروني غير مفعل. يرجى تأكيد بريدك الإلكتروني أو رقم هاتفك.', 'warning')
                    return redirect(url_for('users.login'))
            else:
                flash('توجد مشكلة في إدخال البيانات، يرجى المحاولة مرة أخرى.', 'danger')
    return render_template('login.html', title="تسجيل الدخول", form=form)

@users_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    products = Product.query.filter_by(author=current_user).all()
    return render_template('dashboard.html', title="لوحة التحكم", active_tab='dashboard', products=products)


@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    password_form = UpdatePasswordForm()

    if form.validate_on_submit():
        if form.image.data:
            if current_user.image_file != 'default_user.jpg':
                delete_picture(current_user.image_file, "static/profile_pics")
            picture_file = save_picture(form.image.data, path='static/profile_pics', output_size=(200, 200))
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email_or_phone = form.email_or_phone.data
        db.session.commit()
        flash('تم تحديث ملفك الشخصي بنجاح!', 'success')
        return redirect(url_for('users.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email_or_phone.data = current_user.email_or_phone
    else:
        flash('توجد مشكلة في إدخال البيانات، يرجى المحاولة مرة أخرى.', 'danger')
        form.username.data = current_user.username
        form.email_or_phone.data = current_user.email_or_phone

    if password_form.validate_on_submit():
        if current_user.password == password_form.current_password.data:
            current_user.password = password_form.new_password.data
            db.session.commit()
            flash('تم تغيير كلمة المرور بنجاح!', 'success')
            return redirect(url_for('users.profile'))
        else:
            flash('كلمة المرور الحالية غير صحيحة', 'danger')

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='الملف الشخصي',
                           image_file=image_file, form=form, password_form=password_form, active_tab='profile')
    
@users_bp.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_or_phone=form.email_or_phone.data).first()
        if user:
            send_email(user=user, condition="reset_email")
        flash(
            "إذا كان هذا الحساب موجودًا، فسوف تتلقى بريدًا إلكترونيًا يحتوي على التعليمات",
            "info",
        )
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="اعادة ضبط كلمة المرور", form=form)


@users_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_pw_reset_token(token)
    if not user:
        flash("The token is invalid or expired", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.commit()
        flash(f"تم تحديث كلمة المرور الخاصة بك. يمكنك الآن تسجيل الدخول", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_password.html", title="اعادة ضبط كلمة المرور", form=form)