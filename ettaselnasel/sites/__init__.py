from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_mail import Mail
from flask_admin import Admin
from sites.config import Config
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
import os

db = SQLAlchemy()
login_manager = LoginManager()
ckeditor = CKEditor()
migrate = Migrate()
mail = Mail()
admin = Admin()

def init_whoosh(app):
    schema = Schema(title=TEXT(stored=True), slug=TEXT(stored=True), content=TEXT(stored=True), path=ID(stored=True))
    
    # مسار الفهرس
    index_dir = os.path.join(app.instance_path, 'index')
    
    # إنشاء الفهرس إذا لم يكن موجودًا
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        ix = create_in(index_dir, schema)
    else:
        ix = open_dir(index_dir)
    
    app.config['WHOOSH_INDEX'] = ix


def create_app(class_config=Config):
    
    app = Flask(__name__)
    app.config.from_object(class_config)
    
    from sites.adminbp.routes import MyAdminIndexView

    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())
    init_whoosh(app)
    
    # تسجيل Blueprints
    from sites.main_bp.routes import main_bp
    from sites.users_bp.routes import users_bp
    from sites.products_bp.routes import products_bp
    from sites.errors_bp.handlers import errors_bp
    from sites.adminbp.routes import adminbp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(adminbp)
    
    return app
