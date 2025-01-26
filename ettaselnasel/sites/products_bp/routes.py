from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app
from sites.products_bp.forms import NewProductForm, EditProductForm, CategoryForm
from sites import db
from sites.models import Product, Category, User
from flask_login import current_user, login_required
from sites.helpers import save_picture, delete_picture, index_product, delete_product_index
from whoosh.qparser import MultifieldParser

products_bp = Blueprint('products', __name__) 

@products_bp.route('/products/', methods=['GET'])
def products():
    discount_products = Product.query.filter_by(is_discount=True).order_by(Product.date_posted.desc()).all()
    products = Product.query.order_by(Product.date_posted.desc()).all()
    
    return render_template('products.html', title="المنتجات", products=products, discount_products=discount_products)


@products_bp.route('/product/<int:category_id>/<int:product_id>/')
def product_detail(category_id, product_id):
    product = Product.query.filter_by(id=product_id, category=category_id).first()
    productId = product.id if product else None
    product = Product.query.get_or_404(productId)
    seller = product.author
    category = Category.query.get(product.category)
    return render_template('product_detail.html', title=product.title, product=product, seller=seller, category=category)


@products_bp.route('/product/create/', methods=['GET', 'POST'])
@login_required
def create_product():
    product_form = NewProductForm()
    category_form = CategoryForm()
    form_name = request.form.get("form_name")
    
    if request.method == 'POST':
        if form_name == 'category_form' and category_form.validate_on_submit():
            if category_form.icon.data:
                icon_file = save_picture(category_form.icon.data, path='static/category_icons', output_size=(500, 500))
            else:
                icon_file = 'default_product.jpg'
            category = Category(
                category=category_form.category.data,
                icon=icon_file,
            )
            db.session.add(category)
            db.session.commit()
            flash('تم انشاء التصنيف بنجاح!', 'success')
            return redirect(url_for('products.create_product'))
        
        elif form_name == 'product_form' and product_form.validate_on_submit():
            if product_form.icon.data:
                icon_file = save_picture(product_form.icon.data, path='static/product_icons', output_size=(500, 500))
            else:
                icon_file = 'default_product.jpg'

            # نأخذ السعر النهائي المحسوب من JavaScript
            is_discount = product_form.is_discount.data
            discount = product_form.discount.data
            if not is_discount:
                final_price = product_form.price.data
                discount = 0
            else:
                final_price = request.form.get('final_price')
                if discount == 0:
                    is_discount = False
                else:
                    is_discount = product_form.is_discount.data
                    discount = product_form.discount.data
            product = Product(
                title=product_form.title.data,
                content=product_form.content.data,
                icon=icon_file,
                slug=product_form.slug.data,
                price=product_form.price.data,
                quantity=product_form.quantity.data,
                author=current_user,
                cat=product_form.category.data,
                is_discount=is_discount,
                discount=discount,
                final_price = final_price
            )
            db.session.add(product)
            db.session.commit()
            
            index_product(product)
            
            flash('تم انشاء المنتج بنجاح!', 'success')
            return redirect(url_for('users.dashboard'))

        elif form_name not in ['category_form', 'product_form']:
            flash('يرجى ملء أحد النماذج', 'danger')
            
        else:
            flash('يرجى التأكد من ان جميع الحقول سليمة', 'danger')
    elif request.method == 'GET':
        product_form.discount.data = 0

    return render_template(
        'create_product.html', 
        title='انشاء منتج', 
        product_form=product_form, 
        category_form=category_form, 
        active_tab='create_product',
    )


@products_bp.route('/product/<int:category_id>/<int:product_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_product(category_id, product_id):
    product = Product.query.filter_by(id=product_id, category=category_id).first()
    productId = product.id if product else None
    product = Product.query.get_or_404(productId)
    if product.author != current_user:
        abort(403)
    form = EditProductForm()
    delete_product_index(product)
    
    if form.validate_on_submit():
        product.cat = form.category.data
        product.title = form.title.data
        product.slug = form.slug.data
        product.content = form.content.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        
        is_discount = form.is_discount.data
        discount = form.discount.data
        if not is_discount:
            final_price = form.price.data
            discount = 0
        else:
            final_price = request.form.get('final_price')
            if discount == 0:
                is_discount = False
            else:
                is_discount = form.is_discount.data
                discount = form.discount.data
                
        product.is_discount=is_discount,
        product.discount=discount,
        product.final_price = final_price
        
        if form.icon.data:
            if product.icon != 'default_product.jpg':
                delete_picture(product.icon, "static/product_icons")
            new_picture = save_picture(form.icon.data, "static/product_icons")
            product.icon = new_picture
            
        
        
        db.session.commit()
        
        index_product(product)  # تحديث الفهرسة بعد التعديل
        flash("تم تحديث منتجك بنجاح", "success")
        return redirect(url_for("users.dashboard"))
    
    elif request.method == 'GET':
        form.title.data = product.title
        form.slug.data = product.slug
        form.content.data = product.content
        form.category.data = product.cat
        form.price.data = product.price
        form.quantity.data = product.quantity
        form.is_discount.data = product.is_discount
        form.discount.data = product.discount
        form.final_price.data = product.final_price

    return render_template('edit_product.html', title=' تعديل المنتج : ' + product.title, form=form, product_id=product_id, category_id=category_id)
 

@products_bp.route('/product/<int:category_id>/<int:product_id>/delete/', methods=['GET', 'POST'])
def delete_product(category_id, product_id):
    product = Product.query.filter_by(id=product_id, category=category_id).first()
    productId = product.id if product else None
    product = Product.query.get_or_404(productId)
    if product.author != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    
    delete_product_index(product)
    
    flash("تم حذف منتجك بنجاح", "success")
    return redirect(url_for("users.dashboard"))

@products_bp.route('/search', methods=['GET'])
def search_view():
    query_str = request.args.get('query', '')
    selected_category = request.args.get('category', 'all')  # الحصول على التصنيف المختار، الافتراضي هو 'all'
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    categories = Category.query.all()  # جلب جميع التصنيفات من قاعدة البيانات

    # البحث في المنتجات بناءً على الاستعلام
    if query_str:
        try:
            ix = current_app.config['WHOOSH_INDEX']
            
            with ix.searcher() as searcher:
                parser = MultifieldParser(["title", "slug", "content"], ix.schema)
                query = parser.parse(query_str)
                results = searcher.search(query)

                # تحويل النتائج إلى قائمة من المنتجات
                product_ids = [int(result['path']) for result in results]
                products = Product.query.filter(Product.id.in_(product_ids)).all()

                # تصفية النتائج بناءً على التصنيف
                if selected_category and selected_category != 'all':
                    products = [product for product in products if product.cat.id == int(selected_category)]

                # تصفية النتائج بناءً على السعر
                if min_price is not None:
                    products = [product for product in products if product.final_price >= min_price]
                if max_price is not None:
                    products = [product for product in products if product.final_price <= max_price]

                # تمرير المتغيرات إلى القالب
                return render_template('search_results.html', products=products, query=query_str, categories=categories, selected_category=selected_category, min_price=min_price, max_price=max_price)
        except Exception as e:
            # التعامل مع الأخطاء
            print(f"Error during search: {e}")
            return render_template('search_results.html', products=[], query=query_str, categories=categories, selected_category=selected_category, min_price=min_price, max_price=max_price, error="حدث خطأ أثناء البحث. يرجى المحاولة مرة أخرى.")

    # إذا لم يكن هناك استعلام، نعرض الصفحة بدون أي تصنيف محدد
    return render_template('search_results.html', products=[], query='', categories=categories, selected_category='all', min_price=min_price, max_price=max_price)





