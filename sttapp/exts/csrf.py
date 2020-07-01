from flask_wtf.csrf import CSRFProtect


def init_csrf(app):
    
    csrf = CSRFProtect(app)
    return csrf
