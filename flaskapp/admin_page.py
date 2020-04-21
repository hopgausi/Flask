from flaskapp import admin, db
from flask_admin.contrib.sqla import ModelView
from flaskapp.models import User


admin.add_view(ModelView(User, db.session))
