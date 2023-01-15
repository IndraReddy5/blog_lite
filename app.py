from flask import request, redirect, url_for, flash
from flask import render_template

from application.models import User
from create_app import create_app, login_manager, db

from werkzeug.exceptions import HTTPException
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


@app.route('/login', methods=["GET", "POST"])
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
                flash('Invalid password provided')
                return render_template('login.html')
        else:
            flash('User account doesn\'t exist')
            return render_template('login.html')


@app.route('/create_account', methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/dashboard')
        return render_template("create_account.html")
    else:
        file_uploaded = request.files['profile_image']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
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
                    login_user(User.query.filter_by(username=username).first(),remember=True)
                return redirect(url_for('dashboard'))
            else:
                flash('User already exists')
                return redirect(url_for('create_account'))
        else:
            flash('Passwords didn\'t match')
            return redirect(url_for('create_account'))
# App login and Sign routes End

# App Dashboard route start


@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    feed = req.get(url=request.url_root +
                   f'api/Feed/{current_user.username}').json()
    return render_template('dashboard.html', user=current_user.username, profile_image_path=current_user.profile_image, feed=feed)

# App Dashboard route End

# App route for Search query and results Start


@app.route('/search', methods=["GET"])
@login_required
def search():
    q = request.args.get('search', type=str)
    lu_following = req.get(url=request.url_root +
                           f'api/Follow/{current_user.username}').json().get('following')
    q_results = req.get(url=request.url_root+f'api/Search/{q}')
    if q_results.status_code == 200:
        q_results = q_results.json()
    else:
        q_results = ""
    return render_template('search.html', user=current_user.username, profile_image_path=current_user.profile_image, q_results=q_results, lu_following=lu_following)
# App route for Search query and results End


# App routes for User Profile Actions (posts, followers, following) Start
@app.route('/profile/<string:username>', methods=['GET'])
@login_required
def load_profile(username):
    return_object = req.get(url=request.url_root +
                            f'api/User_profile/{username}')
    if return_object.status_code == 200:
        return_object = return_object.json()
        user_posts = req.get(url=request.url_root +
                             f'api/Posts/{username}').json()
        lu_following = req.get(url=request.url_root +
                               f'api/Follow/{current_user.username}').json().get('following')
        followers_api_object = req.get(url=request.url_root +
                                       f'api/Follow/{username}').json()
        followers = followers_api_object.get('followers')
        followers_objects = followers_api_object.get('followers_objects')
        followed = followers_api_object.get("following")
        followed_objects = followers_api_object.get('following_objects')
        return render_template("profile.html", profile=return_object, user=current_user.username, profile_image_path=current_user.profile_image, lu_following=lu_following, user_posts=user_posts, followers=followers, followers_objects=followers_objects, followed=followed, followed_objects=followed_objects)
    else:
        flash(f'{username} account doesn\'t exist', 'error')
        return redirect(url_for('dashboard'))


@app.route('/delete/<string:username>')
@login_required
def delete_account(username):
    if current_user.username == username:
        if req.delete(url=request.url_root+f'api/User_profile/{username}').status_code == 200:
            return redirect('/')
    flash('You can\'t delete other users account')
    return redirect(url_for('login'))

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
        data = req.post(url=request.url_root+'api/Posts', json=form_data)
        if data.status_code == 200:
            data = data.json()
            if post_image.filename:
                post_image.save(os.path.join(
                    'static/post_images/', username+"_"+title+"_"+post_image.filename))
            return redirect(url_for('blog_post', p_id=data['p_id']))
        else:
            flash('please give a unique title, someone made post with this title')
            return redirect(url_for('create_post', username=current_user.username))

# App routes for users posts End

# App routes for follow & unfollow action Start


@app.route('/profile/<string:username>/followers/follow/<string:fr_name>/<string:fd_name>', methods=['GET'])
@app.route('/profile/<string:username>/followers/follow/<string:fr_name>/<string:fd_name>#<string:end_id>', methods=['GET'])
def follow_action(username, fr_name, fd_name, end_id=None):
    if req.post(url=request.url_root+f'api/Follow/{fr_name}/{fd_name}').status_code == 200:
        if end_id:
            return redirect(request.referrer+"#"+end_id)
        return redirect(request.referrer)
    else:
        flash(f'Sorry, We couldn\'t make {fr_name} follow {fd_name}')
        return redirect(request.referrer)


@app.route('/profile/<string:username>/followers/unfollow/<string:fr_name>/<string:fd_name>', methods=['GET'])
@app.route('/profile/<string:username>/followers/unfollow/<string:fr_name>/<string:fd_name>#<string:end_id>', methods=['GET'])
def unfollow_action(username, fr_name, fd_name, end_id=None):
    if req.delete(url=request.url_root+f'api/Follow/{fr_name}/{fd_name}').status_code == 200:
        if end_id:
            return redirect(request.referrer+"#"+end_id)
        return redirect(request.referrer)
    else:
        flash(f'Sorry, We couldn\'t make {fr_name} unfollow {fd_name}')
        return redirect(request.referrer)

# App routes for follow & unfollow action End

# App routes for like & unlike action Start


@app.route('/like/<string:engaged_user>/<int:p_id>', methods=['GET'])
@login_required
def like_action(engaged_user, p_id):
    if current_user.username == engaged_user:
        if req.post(url=request.url_root+f'api/Likes/{engaged_user}/{p_id}').status_code == 200:
            return redirect(request.referrer)
        else:
            flash(f'Sorry, We couldn\'t make {engaged_user} like the post')
            return redirect(request.referrer)


@app.route('/unlike/<string:engaged_user>/<int:p_id>', methods=['GET'])
@login_required
def unlike_action(engaged_user, p_id):
    if current_user.username == engaged_user:
        if req.delete(url=request.url_root+f'api/Likes/{engaged_user}/{p_id}').status_code == 200:
            return redirect(request.referrer)
        else:
            flash(f'Sorry, We couldn\'t make {engaged_user} unlike the post')
            return redirect(request.referrer)

# App routes for like & unlike action End

# App routes for making Comment & Deleting Comment Start


@app.route('/comment/<string:engaged_user>/<int:p_id>', methods=['POST'])
@login_required
def make_comment(engaged_user, p_id):
    if current_user.username == engaged_user:
        data = {"post_id": p_id,
                "commenter": engaged_user,
                "comment_description": request.form['comment_description']}
        if req.post(url=request.url_root+f'api/Comments/{p_id}', json=data).status_code == 200:
            return redirect(request.referrer)
        else:
            flash(
                f'Sorry, We couldn\'t make {engaged_user} to comment on the post')
            return redirect(request.referrer)


@app.route('/delete_comment/<string:engaged_user>/<int:c_id>', methods=['GET'])
@login_required
def delete_comment(engaged_user, c_id):
    if current_user.username == engaged_user:
        if req.delete(url=request.url_root+f'api/Comments/{engaged_user}/{c_id}').status_code == 200:
            return redirect(request.referrer)
        else:
            flash(
                f'Sorry, We were not able to delete {engaged_user} comment on the post')
            return redirect(request.referrer)

# App routes for making Comment & Deleting Comment End

# App routes for editing account & editing post start


@app.route('/edit_profile/<string:username>', methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if request.method == "GET":
        if current_user.username == username:
            profile = req.get(url=request.url_root +
                              f"api/User_profile/{username}")
            if profile.status_code == 200:
                profile = profile.json()
            return render_template('edit_profile.html', user=current_user.username, profile_image_path=current_user.profile_image, profile=profile)
    else:
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            file_uploaded = request.files['profile_image']
            form_data = {'username': username,
                         'first_name': request.form['first_name'],
                         'last_name': request.form['last_name'],
                         'email': request.form['email'],
                         'password': request.form['password'],
                         'profile_image': file_uploaded.filename}
            if req.put(url=request.url_root+f'api/User_profile/{username}', json=form_data).status_code == 200:
                if file_uploaded.filename:
                    file_uploaded.save(os.path.join(
                        'static/profile_images/', username+"_"+file_uploaded.filename))
                return redirect('/')
            return redirect(url_for('dashboard'))
        else:
            flash('Passwords didn\'t match, please enter them correctly')
            return redirect(url_for('edit_profile', username=username))


@app.route('/edit_post/<string:username>/<int:p_id>', methods=["GET", "POST"])
@login_required
def edit_post(username, p_id):
    if request.method == "GET":
        blog_data = req.get(url=request.url_root+f"api/Posts/{p_id}")
        if blog_data.status_code == 200:
            blog_data = blog_data.json()
            if blog_data['author_name'] == current_user.username:
                return render_template('edit_post.html', user=current_user.username, profile_image_path=current_user.profile_image, blog_data=blog_data)
    else:
        title = request.form['title']
        post_description = request.form['post_description']
        post_image = request.files['post_image']
        form_data = {"author_name": username,
                     "title": title,
                     "description": post_description,
                     "post_image": post_image.filename}
        put_query = req.put(url=request.url_root +
                            f'api/Posts/{p_id}', json=form_data)
        if put_query.status_code == 200:
            if post_image.filename:
                post_image.save(os.path.join(
                    'static/post_images/', username+"_"+title+"_"+post_image.filename))
            return redirect(url_for('blog_post', p_id=p_id))
        if put_query.status_code == 400:
            flash("Someone already made a post with this title, please try a new one")
            return redirect(url_for('edit_post', username=username, p_id=p_id))
        else:
            flash("Error in editing post, try again")
            return redirect(url_for('edit_post', username=username, p_id=p_id))
# App routes for editing account & editing post End

# App routes for deleting blog post start


@app.route('/delete_post/<string:username>/<string:author_name>/<int:p_id>', methods=['GET'])
@login_required
def delete_post(username, author_name, p_id):
    if username == author_name:
        if req.delete(url=request.url_root+f'api/Posts/{username}/{p_id}').status_code == 200:
            return redirect(url_for('load_profile', username=username))
    flash('We were unable to delete that post')
    return redirect(request.referrer)

# App routes for deleting blog post End

# App route for blog page and comments,likes of post Start


@app.route('/blog/<int:p_id>')
@login_required
def blog_post(p_id):
    data = req.get(url=request.url_root+f'api/Posts/{p_id}')
    comments = req.get(url=request.url_root+f'api/Comments/{p_id}')
    if comments.status_code == 200:
        comments = comments.json()
    else:
        comments = []
    likes = req.get(url=request.url_root+f'api/Likes/{p_id}')
    if likes.status_code == 200:
        likes = likes.json()
    else:
        likes = []
    if data.status_code == 200:
        return render_template('blog_post.html', user=current_user.username, profile_image_path=current_user.profile_image, blog_data=data.json(), likes=likes, comments=comments)

# App route for blog page and comments,likes of post Start

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


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return flash message instead of HTML for HTTP errors."""
    flash(f'{e.code}, {e.description}')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port=8000)
