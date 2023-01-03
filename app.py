from flask import request, redirect, url_for
from flask import render_template

from application.models import User
from create_app import create_app, login_manager, db

from flask_login import login_required, login_user, logout_user, current_user
import requests as req
import os

app = create_app()
app.app_context().push()
db.create_all()

# login manager handler routes start

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

# login manager handler routes End

# App login and Sign routes Start

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
                return render_template('login.html')
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

# App login and Sign routes End

# App Dashboard route start

@app.route('/dashboard',methods=["GET"])
@login_required
def dashboard():
    feed = req.get(url=request.url_root+f'api/Feed/{current_user.username}').json()
    return render_template('dashboard.html', user=current_user.username, profile_image_path=current_user.profile_image, feed = feed)

# App Dashboard route End

# App route for Search query and results Start

@app.route('/search', methods=["GET"])
@login_required
def search():
    q = request.args.get('search', type=str)
    q_results = req.get(url=request.url_root+f'api/Search/{q}')
    if q_results.status_code == 200:
        q_results = q_results.json()
    else:
        q_results = ""
    return render_template('search.html',user=current_user.username, profile_image_path = current_user.profile_image, q_results = q_results)
# App route for Search query and results End


# App routes for User Profile Actions (posts, followers, following) Start

@app.route('/profile/<string:username>/posts', methods=['GET'])
@app.route('/profile/<string:username>', methods=['GET'])
@login_required
def load_profile(username):
    return_object = req.get(url=request.url_root+f'/api/User_profile/{username}').json()
    user_posts = req.get(url=request.url_root+f'/api/Posts/{username}').json()
    lu_followers = req.get(url=request.url_root+f'/api/Follow/{current_user.username}').json()
    return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, load_variable="posts", lu_followers=lu_followers, user_posts=user_posts)

@app.route('/profile/<string:username>/followers', methods=['GET'])
@login_required
def followers(username):
    return_object = req.get(url=request.url_root+f'/api/User_profile/{username}').json()
    followers = req.get(url=request.url_root+f'/api/Follow/{username}').json().get('followers')
    lu_followers = req.get(url=request.url_root+f'/api/Follow/{current_user.username}').json()
    return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, load_variable="followers", lu_followers=lu_followers, followers=followers)

@app.route('/profile/<string:username>/followed', methods=['GET'])
@login_required
def followed(username):
    return_object = req.get(url=request.url_root+f'/api/User_profile/{username}').json()
    followed = req.get(url=request.url_root+f'/api/Follow/{username}').json().get("following")
    lu_followers = req.get(url=request.url_root+f'/api/Follow/{current_user.username}').json()
    return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, load_variable="followed", lu_followers=lu_followers,followers=followed)

@app.route('/delete/<string:username>')
@login_required
def delete_account(username):
    if current_user.username == username:
        if req.delete(url=request.url_root+f'/api/User_profile/{username}').status_code == 200:
            logout_user()
            return redirect('/')

# App routes for User Profile Actions End

# App routes for users posts Start

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

@app.route('/blog/<int:p_id>')
@login_required
def blog_post():
    return render_template('blog_post.html')

# App routes for users posts End

# App routes for follow & unfollow action Start

@app.route('/profile/<string:username>/followers/follow/<string:fr_name>/<string:fd_name>', methods=['GET'])
def follow_action(username,fr_name,fd_name):
    if req.post(url=request.url_root+f'/api/Follow/{fr_name}/{fd_name}').status_code==200:
        return redirect(request.referrer)
    else:
        return "some error"

@app.route('/profile/<string:username>/followers/unfollow/<string:fr_name>/<string:fd_name>', methods=['GET'])
def unfollow_action(username,fr_name,fd_name):
    if req.delete(url=request.url_root+f'/api/Follow/{fr_name}/{fd_name}').status_code==200:
        return redirect(request.referrer)
    else:
        return "some error"

# App routes for follow & unfollow action End

# App route for logout of current_user Start

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# App route for logout of current_user End

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
