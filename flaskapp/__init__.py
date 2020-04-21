from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin


app = Flask(__name__)

app.config['SECRET_KEY'] = '1384ab74c6c624dffd691748900fc348'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myflaskApp.db'
app.config['ADMIN_CREDENTIALS'] = ('admin', 'adminm')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
admin = Admin(app)

login_manager.login_view = "login"
login_manager.login_message_category = "info"

from flaskapp import routes, admin_page
