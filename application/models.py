from .database import db
from flask_login import UserMixin
from passlib.hash import sha256_crypt

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String, unique=True, primary_key=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = sha256_crypt.hash(password)
        self.email = email

    def validate_password(self, password):
        return sha256_crypt.verify(password, self.password)

    def get_id(self):
           return (self.username)

class User_profile(db.Model):
    __tablename__ = 'user_profile'
    username = db.Column(db.String, db.ForeignKey('user.username'), unique=True, primary_key=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    email = db.Column(db.String, db.ForeignKey('user.email'), unique=True, nullable=False)
    profile_image = db.Column(db.String)
    posts = db.relationship("Posts", cascade="delete", foreign_keys='Posts.author_name')
    follower = db.relationship("Follow", cascade="delete", foreign_keys='Follow.follower_username')
    followed = db.relationship("Follow", cascade="delete", foreign_keys='Follow.followed_username')

class Posts(db.Model):
    __tablename__ = 'posts'
    p_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_name = db.Column(db.String, db.ForeignKey('user_profile.username'), nullable=False )
    title = db.Column(db.String)
    description = db.Column(db.String)
    post_image = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    comments = db.relationship("Comments", cascade="delete", foreign_keys='Comments.post_id')
    likes = db.relationship("Likes", cascade="delete", foreign_keys='Likes.post_id')

class Comments(db.Model):
    __tablename__ = 'comments'
    c_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.p_id'), nullable=False)
    commenter = db.Column(db.String, db.ForeignKey('user_profile.username'), nullable=False)
    comment_description = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime)

class Likes(db.Model):
    __tablename__ = 'likes'
    l_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.p_id'), nullable=False)
    engaged_user = db.Column(db.String, db.ForeignKey('user_profile.username'), nullable=False)
    likes = db.Column(db.Boolean, nullable=False)
    dislikes = db.Column(db.Boolean, nullable=False)

class Follow(db.Model):
    __tablename__ = 'follow'
    f_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    follower_username = db.Column(db.String, db.ForeignKey('user_profile.username'), nullable=False)
    followed_username = db.Column(db.String, db.ForeignKey('user_profile.username'), nullable=False)
    follow_back = db.Column(db.Boolean, nullable=False)