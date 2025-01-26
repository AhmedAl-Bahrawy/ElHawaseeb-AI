from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed , FileField
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from tokenize import String
from sites.models import Category

def choice_query():
    return Category.query

class NewProductForm(FlaskForm):
    category = QuerySelectField('صنف المنتج', query_factory=choice_query, get_label='category')
    title = StringField('عنوان المنتج', validators=[DataRequired(), Length(max=70)])
    content = CKEditorField('محتوى المنتج', validators=[DataRequired()], render_kw={'rows':'20'})
    icon = FileField('تحميل صورة المنتج', validators=[DataRequired() ,FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'svg', 'tiff', 'ico'])])
    slug = StringField('معلومات المنتج', validators=[DataRequired(), Length(max=100)])
    price = FloatField('سعر المنتج', validators=[DataRequired()])
    quantity = IntegerField('الكمية', validators=[DataRequired()])
    is_discount = BooleanField('هل هذا المنتج عليه تخفيض')
    discount = IntegerField('نسبة التخفيض')
    final_price = FloatField('السعر النهائي بعد الخصم', render_kw={'readonly': True})  # حقل السعر النهائي
    submit = SubmitField('إنشاء المنتج')
    
    def validate_discount(self, discount):
        if discount.data >= 100:
            raise ValidationError("اقصى رقم يمكن وضعه هنا هو ال 99")

    
class EditProductForm(NewProductForm):
    icon = FileField('تحميل صورة المنتج', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'svg', 'tiff', 'ico'])])
    submit = SubmitField('تحديث المنتج')

class CategoryForm(FlaskForm):
    category = StringField('اسم التصنيف الجديد:', validators=[DataRequired(), Length(max=70)])
    icon = FileField('أيقونة التصنيف')
    submit = SubmitField('إضافة التصنيف')