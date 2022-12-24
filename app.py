from flask import request, redirect
from flask import render_template
from flask import Flask

from application.models import User
from create_app import create_app,  login_manager, basedir, db

from flask_login import login_required, login_user, logout_user
import requests as req
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()

app = create_app()
app.app_context().push()
db.create_all()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        # check if username and password matches
        data = User.query.filter_by(username=username).first()
        if data.validate_password(password):
            login_user(User.query.filter_by(username=username).first(), remember=True)
            return redirect('/dashboard')
        else:
            return render_template('login.html', error=1)

@app.route('/create_account', methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        return render_template("create_account.html")
    else:
        file_uploaded = request.files['profile_image']
        username = request.form['username']
        if file_uploaded.filename:
            file_path = 'static\\profile_images\\'+f'{username}_'+f'{file_uploaded.filename}'
        else:
            file_path = ""
        form_data = {'username': request.form['username'],
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'password': request.form['password'],
                'profile_image': file_path}
        if req.post(url=request.url_root+'api/User_profile', json=form_data).status_code == 200:
            if file_path:
                file_uploaded.save(os.path.join(basedir,file_path))
            return redirect('/')
        else:
            return "user exists"
        

@app.route('/dashboard')
@login_required
def dashboard():
    return "user logged in"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)