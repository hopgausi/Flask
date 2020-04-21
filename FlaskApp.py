from flaskapp import app, db
from flaskapp.models import User, Post


# flask shell register the import after invoking the function
@app.shell_context_processor
def shell_processor_context():
    return {'db': db, 'User': User, 'Post': Post}


if __name__ == '__main__':
    app.run(debug=True, port=5001)