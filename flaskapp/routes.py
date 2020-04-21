from flask import render_template, url_for, flash, redirect, request, abort
from flaskapp.Forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskapp.models import User, Post
from flaskapp import app, bcrypt, db
import secrets
import os
from flask_login import login_user, current_user, login_required, logout_user
from PIL import Image


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about_us():
    return render_template('about.html', title='About')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    signup_form = RegistrationForm()
    if signup_form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(signup_form.password.data).decode('utf - 8')
        user = User(username=signup_form.username.data, email=signup_form.email.data, password=pw_hash)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash(f'Your account has been created', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', title='Sign Up', signup_form=signup_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get('next')
            flash('Logged in successfully', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log in unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Log in', login_form=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_profile}')
    return render_template('account.html', title='My account', image_file=image_file)


def save_profile_pic(form_picture):
    random_name = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    new_pic_filename = random_name + file_ext
    path_to_save_pic = os.path.join(app.root_path, 'static/profile_pics', new_pic_filename)
    output_size = (120, 120)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(path_to_save_pic)
    return new_pic_filename


@app.route("/update_account", methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic:
            profile_picture = save_profile_pic(form.profile_pic.data)
            current_user.image_profile = profile_picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.description = form.description.data
        db.session.commit()
        flash('Account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.description.data = current_user.description
    return render_template('update_account.html', form=form, title='Update account')


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash(f'Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='Create new post', form=form)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update_post', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update_post.html', form=form, title='Update post', post=post)


@app.route('/post/<int:post_id>/delete_post', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))
