class Config:
    
    SECRET_KEY = "62913a7dac3933f87a84626fcdeaaf9e2653f0a000843efd9bf2b31ba4767402"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    #SQLALCHEMY_DATABASE_URI = 'mysql://ettaselnasel:B?Gf6-W2+y9d@ettaselnasel.mysql.pythonanywhere-services.com/ettaselnasel$site'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'info.ettaselnasel@gmail.com'
    MAIL_PASSWORD = 'uigi hfxv oazh cxap'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
