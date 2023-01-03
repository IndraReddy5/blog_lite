from flask_restful import Resource, request
from flask_restful import fields, marshal_with , marshal

from application.database import db
from application.models import User, User_profile, Posts, Likes, Comments, Follow
from application.errors import *

import os
from datetime import datetime as dt

def prettify_date(date):
    date = dt.strptime(date,"%Y_%m_%d_%H_%M_%S")
    day = date.strftime("%d/%m/%Y")
    time = date.strftime("%I:%M %p")

    return [day,time]

def get_usernames_object(f_object,key="following"):
    if key == "following":
        output = [x.followed_username for x in f_object]
    if key == "followers":
        output = [x.follower_username for x in f_object]
    return output

class User_profile_API(Resource):

    output = {"username": fields.String, "first_name": fields.String,
              "last_name": fields.String, "profile_image": fields.String,
              "followers_count": fields.Integer, "following": fields.Integer, "total_posts":fields.Integer}

    @marshal_with(output)
    def get(self, username):
        u_obj = User_profile.query.filter_by(username=username).first()
        if u_obj:
            u_obj.followers_count = Follow.query.filter_by(
                followed_username=username).count()
            u_obj.following = Follow.query.filter_by(
                follower_username=username).count()
            u_obj.total_posts = Posts.query.filter_by(
                    author_name=username).count()
            return u_obj, 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    def delete(self, username):
        u_obj = User.query.filter_by(username=username).first()
        u_p_obj = User_profile.query.filter_by(username=username).first()
        if u_obj and u_p_obj:
            db.session.delete(u_obj)
            db.session.delete(u_p_obj)
            # profile pic to be deleted
            file_path = f'static/profile_images/{username}_' + u_p_obj.profile_image
            cmd = 'rm ' + f'{file_path}'
            os.system(cmd)
            db.session.commit()
            return f"{username} profile deleted", 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    @marshal_with(output)
    def put(self, username):
        u_obj = User.query.filter_by(username=username).first()
        u_p_obj = User_profile.query.filter_by(username=username).first()
        if u_p_obj and u_obj:
            form_data = request.get_json()
            if form_data.get("profile_image") != u_obj.profile_image:
                file_path = f'static/profile_images/{username}_' + u_p_obj.profile_image
                cmd = 'rm ' + f'{file_path}'
                os.system(cmd)
            u_p_obj.first_name = form_data.get("first_name")
            u_p_obj.last_name = form_data.get("last_name")
            u_p_obj.email = form_data.get("email")
            u_p_obj.profile_image = form_data.get("profile_image")
            u_obj.email = form_data.get("email")
            u_obj.profile_image = form_data.get("profile_image")
            db.session.commit()
            u_p_obj.followers_count = Follow.query.filter_by(
                followed_username=username).count()
            u_p_obj.following = Follow.query.filter_by(
                follower_username=username).count()
            u_obj.total_posts = Posts.query.filter_by(
                author_name=username).count()

            return u_p_obj, 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    @marshal_with(output)
    def post(self):
        form_data = request.get_json()
        username = form_data.get("username")
        if not User_profile.query.filter_by(username=username).first():
            if username:
                u_obj = User_profile()
                u = User(username=form_data.get("username"), password=form_data.get(
                    "password"), email=form_data.get("email"), profile_image=form_data.get("profile_image"))
                u_obj.username = form_data.get("username")
                u_obj.first_name = form_data.get("first_name")
                u_obj.last_name = form_data.get("last_name")
                u_obj.email = form_data.get("email")
                u_obj.profile_image = form_data.get("profile_image")
                db.session.add(u)
                db.session.add(u_obj)
                db.session.commit()
                u_obj.followers_count = Follow.query.filter_by(
                    followed_username=username).count()
                u_obj.following = Follow.query.filter_by(
                    follower_username=username).count()
                u_obj.total_posts = Posts.query.filter_by(
                    author_name=username).count()
                return u_obj, 200
            else:
                raise ValidationError(
                    status_code=400, error_code="user_2", error_message="username not given.")
        else:
            raise ValidationError(
                status_code=400, error_code="user_1", error_message="username already exists.")


class Posts_API(Resource):

    output = {"author_name": fields.String,
              "title": fields.String,
              "description": fields.String,
              "post_image": fields.String,
              "p_timestamp": fields.List(fields.String),
              "total_comments": fields.Integer,
              "total_likes": fields.Integer,
              "total_dislikes":fields.Integer}

    @marshal_with(output)
    def get(self, p_id):
        post_object = Posts.query.filter_by(p_id=p_id).first()
        if post_object:
            post_object.total_comments = Comments.query.filter_by(
                post_id=p_id).count()
            post_object.total_likes = Likes.query.filter_by(
                post_id=p_id,likes=1).count()
            post_object.total_dislikes = Likes.query.filter_by(
                post_id=p_id,dislikes=1).count()
            post_object.p_timestamp = prettify_date(post_object.timestamp)
            return post_object, 200
        else:
            raise NotFound(status_code=404, error_message="Post not found")

    def delete(self, p_id):
        post_object = Posts.query.filter_by(p_id=p_id).first()
        if post_object:
            db.session.delete(post_object)
            db.session.commit()
            return "post deleted", 200
        else:
            raise NotFound(status_code=404, error_message="Post not found")

    @marshal_with(output)
    def put(self, p_id):
        # updates a comment
        post_object = Posts.query.filter_by(p_id=p_id).first()
        if post_object:
            data = request.get_json()
            post_object.author_name = data.get('author_name')
            post_object.title = data.get('title')
            post_object.description = data.get('description')
            post_object.post_image = data.get('post_image')
            db.session.commit()
            post_object.total_comments = Comments.query.filter_by(
                post_id=p_id).count()
            post_object.total_likes = Likes.query.filter_by(
                post_id=p_id,likes=1).count()
            post_object.total_dislikes = Likes.query.filter_by(
                post_id=p_id,dislikes=1).count()
            post_object.p_timestamp = prettify_date(post_object.timestamp)
            return post_object, 200
        else:
            raise NotFound(status_code=404, error_message="Post not found")

    @marshal_with(output)
    def post(self):
        data = request.get_json()
        title = data.get('title')
        post_object = Posts()
        if not Posts.query.filter_by(title=title).first():
            if title:
                post_object.author_name = data.get('author_name')
                post_object.title = data.get('title')
                post_object.description = data.get('description')
                post_object.post_image = data.get('post_image')
                post_object.timestamp = dt.now().strftime("%Y_%m_%d_%H_%M_%S")

                db.session.add(post_object)
                db.session.commit()
                post_object = Posts.query.filter_by(title=title).first()
                post_object.p_timestamp = prettify_date(post_object.timestamp)
                return post_object, 200
            else:
                raise ValidationError(status_code=400, error_code="post_2",
                                      error_message="Please add a title for your blog post")
        else:
            raise ValidationError(status_code=400, error_code="post_1",
                                  error_message="Please choose another title, someone has chosen same title as you before.")


class Comments_API(Resource):
    output = {"post_id": fields.Integer,
              "commenter": fields.String,
              "comment_description": fields.String,
              "p_timestamp":fields.List(fields.String)}

    @marshal_with(output)
    def get(self, p_id):
        # gets all comments of a particular post
        comments_list = Comments.query.filter_by(post_id=p_id).all()
        if comments_list:
            comments_list.p_timestamp = prettify_date(comments_list.timestamp)
            return comments_list, 200
        else:
            raise NotFound(status_code=404,
                           error_message="There are no comments for this post")

    def delete(self, c_id):
        # deletes a given comment
        comment = Comments.query.filter_by(c_id=c_id).first()
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return 'comment deleted', 200
        else:
            raise NotFound(status_code=404,
                           error_message="There are no comments for this post")

    @marshal_with(output)
    def put(self, c_id):
        # updates a comment
        comment_object = Comments.query.filter_by(c_id=c_id).first()
        if comment_object:
            data = request.get_json()
            comment_object.commenter = data.get('commenter')
            comment_object.comment_description = data.get(
                'comment_description')
            db.session.commit()
            comment_object.p_timestamp = prettify_date(comment_object.timestamp)
            return comment_object, 200
        else:
            raise NotFound(status_code=404,
                           error_message='Comment doesn\'t exist')

    def post(self, p_id):
        # adds a new comment to the post
        post_object = Posts.query.filter_by(p_id=p_id).first()
        if post_object:
            data = request.get_json()
            comment_object = Comments()
            comment_object.post_id = data.get('post_id')
            comment_object.commenter = data.get('commenter')
            comment_object.comment_description = data.get(
                'comment_description')
            comment_object.timestamp = dt.now().strftime("%Y_%m_%d_%H_%M_%S")
            db.session.add(comment_object)
            db.session.commit()
            comment_object.p_timestamp = prettify_date(comment_object.timestamp)
            return comment_object, 200
        else:
            raise NotFound(
                status_code=404, error_message="post doesn't exist")


class Likes_API(Resource):
    output = {"users_liked": fields.List(
        fields.String), "users_disliked": fields.List(fields.String)}

    @marshal_with(output)
    def get(self, p_id):
        # gets all usernames of the persons who liked the post and usernames of the persons who disliked the post
        if Posts.query.filter_by(p_id=p_id).first():
            likes_object = Likes.query.filter_by(post_id=p_id, likes=1).all()
            dislikes_object = Likes.query.filter_by(
                post_id=p_id, dislikes=1).all()
            users_liked = [x.engaged_user for x in likes_object]
            users_disliked = [x.engaged_user for x in dislikes_object]
            x = {"users_liked": users_liked, "users_disliked": users_disliked}
            return x, 200
        else:
            raise NotFound(status_code=404, error_message="Post not found")

    def delete(self, l_id):
        # deletes a like/dislike entry
        x = Likes.query.filter_by(l_id=l_id).first()
        if x:
            db.session.delete(x)
            db.session.commit(x)
            return "like/dislike entry deleted", 200
        else:
            raise NotFound(status_code=404,
                           error_message="This entry has been deleted before")

    def post(self, username, p_id):
        # adds a like/dislike to a post
        post_object = Posts.query.filter_by(p_id=p_id).first()
        user_object = User_profile.query.filter_by(username=username).first()
        if user_object:
            if post_object:
                form_data = request.get_json()
                like_object = Likes()
                like_object.username = username
                like_object.post_id = p_id
                like_object.likes = form_data.get('likes')
                like_object.dislikes = form_data.get('dislikes')
                db.session.add(like_object)
                db.session.commit()
                return f"{username} like/dislike for post {post_object.title} has been added to database", 200
            else:
                raise NotFound(status_code=404,
                               error_message=" Post not found")
        else:
            raise NotFound(status_code=404, error_message="Username not found")


class Follow_API(Resource):
   
    output = {"following":fields.List(fields.String),
              "followers": fields.List(fields.String)}

    @marshal_with(output)
    def get(self, username):
        # gets all followers a particular user
        user_object = User_profile.query.filter_by(username=username).first()
        if user_object:
            followed_object = Follow.query.filter_by(
                followed_username=username).all()
            follower_object = Follow.query.filter_by(
                follower_username=username).all()
            followers = get_usernames_object(followed_object, key="followers")
            following = get_usernames_object(follower_object, key="following")
            output = {"following":following,"followers":followers}
            return output, 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    def delete(self, follower_username, followed_username):
        # removes a follower from the user
        like1_object = Follow.query.filter_by(
            follower_username=follower_username, followed_username=followed_username).first()
        if like1_object:
            db.session.delete(like1_object)
            db.session.commit()
            return f"Now {follower_username} doesn't follow {followed_username}", 200
        else:
            raise ValidationError(status_code=404, error_code="Like_1",
                                  error_message=f"{follower_username} doesn't follow {followed_username}")

    def post(self, follower_username, followed_username):
        # adds a follower to a user
        like1_object = Follow()
        like1_object.follower_username = follower_username
        like1_object.followed_username = followed_username
        db.session.add(like1_object)
        db.session.commit()
        return f"{follower_username} now follows {followed_username}", 200

class Get_Feed_API(Resource):
    # get post_feed of a user
    output = {"author_name": fields.String,
              "title": fields.String,
              "description": fields.String,
              "post_image": fields.String,
              "p_timestamp": fields.List(fields.String),
              "total_comments": fields.Integer,
              "total_likes": fields.Integer,
              "total_dislikes":fields.Integer}
    
    @marshal_with(output)
    def get(self, username):
        follower_object = Follow.query.filter_by(
                follower_username=username).all()
        following = get_usernames_object(follower_object, key="following")
        f_output = []
        for i in following:
            posts = Posts.query.filter_by(author_name=i).all()
            f_output += posts
        f_output.sort(key=lambda r: r.timestamp, reverse=True)
        for i in f_output:
            i.p_timestamp = prettify_date(i.timestamp)
            i.total_likes = Likes.query.filter_by(
                    post_id=i.p_id,likes=1).count()
            i.total_dislikes = Likes.query.filter_by(
                    post_id=i.p_id,dislikes=1).count()
        return f_output, 200

class Get_User_Posts_API(Resource):
    output = {"author_name": fields.String,
              "title": fields.String,
              "description": fields.String,
              "post_image": fields.String,
              "p_timestamp": fields.List(fields.String),
              "total_comments": fields.Integer,
              "total_likes": fields.Integer,
              "total_dislikes":fields.Integer}
    
    @marshal_with(output)
    def get(self, username):
        post_object = Posts.query.filter_by(author_name=username).all()
        if post_object:
            for x in post_object:
                x.total_comments = Comments.query.filter_by(
                    post_id=x.p_id).count()
                x.total_likes = Likes.query.filter_by(
                    post_id=x.p_id,likes=1).count()
                x.total_dislikes = Likes.query.filter_by(
                    post_id=x.p_id,dislikes=1).count()
                x.p_timestamp = prettify_date(x.timestamp)
            return post_object, 200
        else:
            raise NotFound(status_code=404, error_message="user not found")

class Search_API(Resource):
    output = {"username": fields.String, "first_name": fields.String,
              "last_name": fields.String, "profile_image": fields.String}
    
    @marshal_with(output)
    def get(self, query):
        user_object = User_profile.query.filter(User_profile.username.like("%"+query+"%")).all()
        if user_object:
            return user_object, 200
        else:
            raise NotFound(status_code=404, error_message="no users found")