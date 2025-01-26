from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from sites import admin, db
from sites.models import User, Product, Category

adminbp = Blueprint('adminbp', __name__)


class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        else:
            return False


class MyAdminIndexView(AdminIndexView):
     def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        else:
            return False

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Product, db.session))
admin.add_view(MyModelView(Category, db.session))



