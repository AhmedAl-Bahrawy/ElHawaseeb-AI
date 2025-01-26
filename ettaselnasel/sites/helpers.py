import os
import secrets
from PIL import Image
from flask import render_template, url_for, current_app, flash
from flask_mail import Message
from sites import mail
from sites.models import User

def save_picture(form_image, path, output_size=None):
    if output_size==None:
        output_size=(400, 400)
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, path, picture_fn)
    
    image = Image.open(form_image)
    width, height = image.size

    if width > height:
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    elif height > width:
        top = (height - width) // 2
        left = 0
        right = width
        bottom = top + width
    else:
        left = top = right = bottom = None

    if left is not None and top is not None:
        image = image.crop((left, top, right, bottom))
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn

def delete_picture(picture_name, path):
    picture_path = os.path.join(current_app.root_path, path, picture_name)
    try:
        os.remove(picture_path)
    except:
        pass
    
def send_email(user:User, condition):
    defualt_sender = "info.ettaselnasel@gmail.com"
    if condition == "reset_email":
        token = user.get_pw_reset_token()
        url=url_for('users.reset_password', token=token, _external=True)
        msg = Message(
        "Etasel Nasel App Password Reset Request",
        sender=defualt_sender,
        recipients=[user.email_or_phone],
        )
        msg.html = render_template('reset_password_message.html', reset_url=url)
    elif condition == "confirm_email":
        token = user.get_confirm_email_token()
        url=url_for('users.confirm_email', token=token, _external=True)
        msg = Message(
        "Etasel Nasel App Email Confirmation",
        sender=defualt_sender,
        recipients=[user.email_or_phone],
        )
        msg.html = render_template('confirm_email_message.html', confirm_url=url)
    
    mail.send(msg)
    
def send_sms(user : User, condition):
    carrier_gateways = {
        'att': 'txt.att.net',
        'tmobile': 'tmomail.net',
        'verizon': 'vtext.com'
    }
    
    if condition == "confirm_phone":
        token = user.get_confirm_phone_token()
        confirm_url = url_for('users.confirm_phone', token=token, _external=True)
        message_body = f"Hello {user.fullname}, confirm your phone number by clicking here: {confirm_url}"

        # احصل على بوابة مشغل الهاتف بناءً على شركة الاتصال للمستخدم
        carrier = 'verizon'  # مثل 'att' أو 'tmobile'
        email_to_sms = f"{user.email_or_phone}@{carrier_gateways[carrier]}"
        
        msg = Message(
            "Phone Confirmation",
            sender="info.ettaselnasel@gmail.com",
            recipients=[email_to_sms]
        )
        msg.body = message_body
        
        try:
            mail.send(msg)
            return flash(f"تم إرسال الرسالة بنجاح عبر SMS Gateway.")
        except Exception as e:
            return flash(f"حدث خطأ أثناء إرسال الرسالة: {str(e)}")
        
def index_product(product):
    # الوصول إلى فهرس Whoosh من config
    ix = current_app.config['WHOOSH_INDEX']
    
    writer = ix.writer()
    writer.add_document(
        title=product.title,
        slug=product.slug,
        content=product.content,
        path=str(product.id)
    )
    writer.commit()
    
def delete_product_index(product):
    ix = current_app.config['WHOOSH_INDEX']
    
    # فتح الفهرس والبدء بحذف المنتج
    writer = ix.writer()
    writer.delete_by_term('path', str(product.id))  # حذف المنتج حسب مسار الفهرس (رقم الـ ID الخاص بالمنتج)
    writer.commit()
        

