from flask import render_template, url_for, flash, redirect, request, Blueprint, Response, current_app
from flask_mail import Message
from sites.main_bp.forms import ContactForm
from sites import mail
from sites.models import Product
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    ten_days_ago = (datetime.now()).strftime('%Y-%m-%d')
    
    # قائمة المسارات المستثناة مثل صفحات الادمن
    excluded_pages = ['/admin', '/admin/user/', '/admin/product/', '/admin/category/']  # أضف هنا المسارات التي لا تريد إضافتها

    # جلب جميع المسارات من url_map
    for rule in current_app.url_map.iter_rules():
        # فقط اجلب المسارات الثابتة (بدون معاملات ديناميكية مثل <id>)
        if "GET" in rule.methods and not rule.arguments:
            url = f"https://ettaselnasel.pythonanywhere.com{rule.rule}"
            
            # استثناء المسارات المحددة
            if rule.rule not in excluded_pages:
                pages.append({
                    'loc': url,
                    'lastmod': ten_days_ago
                })
    
    # إنشاء خريطة الموقع بتنسيق XML
    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = Response(sitemap_xml, mimetype='application/xml')
    return response


@main_bp.route('/')
@main_bp.route('/home/', methods=['GET'])
def home():
    discount_products = Product.query.filter_by(is_discount=True).order_by(Product.date_posted.desc()).paginate(
        page=1, per_page=6
    )
    products = Product.query.order_by(Product.date_posted.desc()).paginate(
        page=1, per_page=6
    )
    return render_template('home.html', title="الرئيسية", products=products, discount_products=discount_products)

@main_bp.route('/about/', methods=['GET'])
def about():
    return render_template('about.html', title="عنا")

@main_bp.route('/contact/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # بيانات النموذج
        name = form.name.data
        email_or_phone = form.email_or_phone.data
        subject = form.subject.data
        message_body = form.message.data
        
        msg = Message(' رسالة جديدة من ' + name + ' بعنوان' + subject,
                      sender=email_or_phone,
                      recipients=['info.ettaselnasel@gmail.com'])
        # استبدل بعنوان بريدك الإلكتروني
        msg.body=f"""الاسم: {name}\nالبريد الإلكتروني: {email_or_phone}\n\nالرسالة:\n{message_body}"""

        try:
            mail.send(msg)
            flash(' تم إرسال رسالتك بنجاح! وسيتم الرد عليك في اسرع وقت ممكن تفقد الايميل الخاص بك', 'success')
        except Exception as e:
            flash(f'حدث خطأ أثناء إرسال رسالتك: {str(e)}', 'danger')

        return redirect(url_for('main.contact'))

    return render_template('contact.html', title='اتصل بنا', form=form)
