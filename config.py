class Config(object):
    SECRET_KEY = 'Clave nueva'
    SESSION_COOKIE_SECURE = FalseDEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/loginflask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
