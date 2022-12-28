from flask import request, redirect, url_for
from flask import render_template
from flask import Flask

from application.models import User
from create_app import create_app,  login_manager, basedir, db

from flask_login import login_required, login_user, logout_user, current_user
import requests as req
import os


app = create_app()
app.app_context().push()
db.create_all()


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/dashboard')
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        # check if username and password matches
        data = User.query.filter_by(username=username).first()
        if data.validate_password(password):
            login_user(data, remember=True)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=1)


@app.route('/create_account', methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/dashboard')
        return render_template("create_account.html")
    else:
        file_uploaded = request.files['profile_image']
        username = request.form['username']
        if file_uploaded.filename:
            file_path = 'static\\profile_images\\' + \
                f'{username}_'+f'{file_uploaded.filename}'
        else:
            file_path = ""
        form_data = {'username': request.form['username'],
                     'first_name': request.form['first_name'],
                     'last_name': request.form['last_name'],
                     'email': request.form['email'],
                     'password': request.form['password'],
                     'profile_image': file_uploaded.filename}
        if req.post(url=request.url_root+'api/User_profile', json=form_data).status_code == 200:
            if file_path:
                file_uploaded.save(os.path.join(basedir, file_path))
            return redirect('/')
        else:
            return "user exists"


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user.username)


@app.route('/<string:username>/create_post')
@login_required
def create_post(username):
    return render_template("create_post.html")


@app.route('/profile/<string:username>')
@login_required
def load_profile(username):
    return render_template("profile.html")


@app.route('/blog/<int:p_id>')
@login_required
def blog_post():
    return render_template('blog_post.html')


@app.route('/<string:username>/followers')
@login_required
def followers():
    return render_template('followers_page.html')


@app.route('/<string:username>/followers')
@login_required
def followed():
    return render_template('followed_page.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
