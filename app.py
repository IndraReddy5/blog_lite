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
        if data:
            if data.validate_password(password):
                login_user(data, remember=True)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error=1)
        else:
            return "user doesn't exist"


@app.route('/create_account', methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/dashboard')
        return render_template("create_account.html")
    else:
        file_uploaded = request.files['profile_image']
        username = request.form['username']
        form_data = {'username': request.form['username'],
                     'first_name': request.form['first_name'],
                     'last_name': request.form['last_name'],
                     'email': request.form['email'],
                     'password': request.form['password'],
                     'profile_image': file_uploaded.filename}
        if req.post(url=request.url_root+'api/User_profile', json=form_data).status_code == 200:
            if file_uploaded.filename:
                file_uploaded.save(os.path.join(
                    'static/profile_images/', username+"_"+file_uploaded.filename))
            return redirect('/')
        else:
            return "user exists"


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user.username, profile_image_path=current_user.profile_image)


@app.route('/<string:username>/create_post', methods=["GET", "POST"])
@login_required
def create_post(username):
    if request.method == "GET":
        return render_template("create_post.html", user=current_user.username, profile_image_path=current_user.profile_image)
    else:
        title = request.form['title']
        post_description = request.form['post_description']
        post_image = request.files['post_image']
        form_data = {"author_name": username,
                     "title": title,
                     "description": post_description,
                     "post_image": post_image.filename}
        if req.post(url=request.url_root+'/api/Posts', json=form_data).status_code == 200:
            if post_image.filename:
                post_image.save(os.path.join(
                    'static/post_images/', username+"_"+title+"_"+post_image.filename))
            return redirect(url_for('dashboard'))
        else:
            return "post already exists"

@app.route('/profile/<string:username>/posts', methods=['GET'])
@app.route('/profile/<string:username>', methods=['GET'])
@login_required
def load_profile(username):
    return_object = req.get(url=request.url_root+f'/api/User_profile/{username}').json()
    return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, load_variable="posts")


@app.route('/blog/<int:p_id>')
@login_required
def blog_post():
    return render_template('blog_post.html')


@app.route('/profile/<string:username>/followers', methods=['GET'])
@login_required
def followers(username):
    return_object = req.get(url=request.url_root+f'/api/User_profile/{username}').json()
    followers = req.get(url=request.url_root+f'/api/Follow/{username}').json()
    return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, load_variable="followers", followers=followers)


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
