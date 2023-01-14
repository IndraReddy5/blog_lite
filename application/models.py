from .database import db
from flask_login import UserMixin
from passlib.hash import sha256_crypt


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, unique=True,
                         primary_key=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_image = db.Column(db.String)

    def __init__(self, username, password, email, profile_image):
        self.username = username
        self.password = sha256_crypt.hash(password)
        self.email = email
        self.profile_image = profile_image

    def validate_password(self, password):
        return sha256_crypt.verify(password, self.password)

    def get_id(self):
        return (self.username)


class User_profile(db.Model):
    __tablename__ = 'user_profile'
    username = db.Column(db.String, db.ForeignKey(
        'user.username'), unique=True, primary_key=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    email = db.Column(db.String, db.ForeignKey(
        'user.email'), unique=True, nullable=False)
    profile_image = db.Column(db.String)
    posts_rel = db.relationship(
        "Posts", cascade="delete", foreign_keys='Posts.author_name', backref=db.backref('author_profile'))
    comments_rel = db.relationship(
        "Comments", cascade="delete", foreign_keys='Comments.commenter', backref=db.backref('commenter_profile'))
    follower = db.relationship(
        "Follow", cascade="delete", foreign_keys='Follow.follower_username', backref=db.backref('follower_profile'))
    followed = db.relationship(
        "Follow", cascade="delete", foreign_keys='Follow.followed_username', backref=db.backref('followed_profile'))
    likes_rel = db.relationship(
        "Likes", cascade="delete", foreign_keys='Likes.engaged_user')


class Posts(db.Model):
    __tablename__ = 'posts'
    p_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_name = db.Column(db.String, db.ForeignKey(
        'user_profile.username'), nullable=False)
    title = db.Column(db.String)
    description = db.Column(db.String)
    post_image = db.Column(db.String)
    timestamp = db.Column(db.String)
    comments = db.relationship(
        "Comments", cascade="delete", foreign_keys='Comments.post_id')
    likes = db.relationship("Likes", cascade="delete",
                            foreign_keys='Likes.post_id')


class Comments(db.Model):
    __tablename__ = 'comments'
    c_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.p_id'), nullable=False)
    commenter = db.Column(db.String, db.ForeignKey(
        'user_profile.username'), nullable=False)
    comment_description = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.String)


class Likes(db.Model):
    __tablename__ = 'likes'
    l_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.p_id'), nullable=False)
    engaged_user = db.Column(db.String, db.ForeignKey(
        'user_profile.username'), nullable=False)


class Follow(db.Model):
    __tablename__ = 'follow'
    f_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    follower_username = db.Column(db.String, db.ForeignKey(
        'user_profile.username'), nullable=False)
    followed_username = db.Column(db.String, db.ForeignKey(
        'user_profile.username'), nullable=False)
