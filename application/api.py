from flask_restful import Resource, request
from flask_restful import fields, marshal_with

from application.database import db
from application.models import User, User_profile, Posts, Likes, Comments, Follow
from application.errors import *

import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class User_profile_API(Resource):

    output = {"username": fields.String, "first_name": fields.String,
              "last_name": fields.String, "profile_image": fields.String}

    @marshal_with(output)
    def get(self, username):
        u_obj = User_profile.query.filter_by(username=username).first()
        if u_obj:
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
            file_path = os.path.join(basedir, u_p_obj.profile_image)
            cmd = 'rm ' + f'{file_path}'
            os.system(cmd)
            db.session.commit()
            return f"{username} profile deleted", 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    @marshal_with(output)
    def put(self, username):
        u_obj = User_profile.query.filter_by(username=username).first()
        if u_obj:
            form_data = request.get_json()
            if form_data.get("profile_image") != u_obj.profile_image:
                file_path = os.path.join(
                    basedir, 'static\\profile_images\\'+f'{username}_'+f'{u_obj.profile_image}')
                cmd = 'rm ' + f'{file_path}'
                os.system(cmd)
            u_obj.first_name = form_data.get("first_name")
            u_obj.last_name = form_data.get("last_name")
            u_obj.email = form_data.get("email")
            u_obj.profile_image = form_data.get("profile_image")

            db.session.commit()

            return u_obj, 200
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
                    "password"), email=form_data.get("email"))
                u_obj.username = form_data.get("username")
                u_obj.first_name = form_data.get("first_name")
                u_obj.last_name = form_data.get("last_name")
                u_obj.email = form_data.get("email")
                u_obj.profile_image = form_data.get("profile_image")
                db.session.add(u)
                db.session.add(u_obj)
                db.session.commit()
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
              "total_comments": fields.Integer,
              "total_likes": fields.Integer}

    @marshal_with(output)
    def get(self, p_id):
        post_object = Posts.query.filter_by(p_id=p_id).first()
        if post_object:
            post_object.total_comments = Comments.query.filter_by(
                post_id=p_id).count()
            post_object.total_likes = Likes.query.filter_by(
                post_id=p_id).count()
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
                post_id=p_id).count()
            return post_object, 200
        else:
            raise NotFound(status_code=404, error_message="Post not found")

    def post(self):
        data = request.get_json()
        title = data.get(title)
        post_object = Posts()
        if Posts.query.filter_by(title=title).first():
            if title:
                post_object.author_name = data.get('author_name')
                post_object.title = data.get('title')
                post_object.description = data.get('description')
                post_object.post_image = data.get('post_image')

                db.session.add(post_object)
                db.session.commit()
                return json.dumps(post_object), 200
            else:
                raise ValidationError(status_code=400, error_code="post_2",
                                      error_message="Please add a title for your blog post")
        else:
            raise ValidationError(status_code=400, error_code="post_1",
                                  error_message="Please choose another title, someone has chosen same title as you before.")


class Comments_API(Resource):
    output = {"post_id": fields.Integer,
              "commenter": fields.String,
              "comment_description": fields.String}

    @marshal_with(output)
    def get(self, p_id):
        # gets all comments of a particular post
        comments_list = Comments.query.filter_by(post_id=p_id).all()
        if comments_list:
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
            db.session.add(comment_object)
            db.session.commit()
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

    output = {"follower_username": fields.String,
              "follow_back": fields.Integer}

    @marshal_with(output)
    def get(self, username):
        # gets all followers a particular user
        user_object = User_profile.query.filter_by(username=username).first()
        if user_object:
            follow_object = Follow.query.filter_by(
                followed_username=username).all()
            return follow_object, 200
        else:
            raise NotFound(status_code=404, error_message="User not found")

    def delete(self, follower_username, followed_username):
        # removes a follower from the user
        like1_object = Follow.query.filter_by(
            follower_username=follower_username, followed_username=followed_username).first()
        like2_object = Follow.query.filter_by(
            follower_username=followed_username, followed_username=follower_username).first()
        if like1_object:
            db.session.delete(like1_object)
            if like2_object:
                like2_object.follow_back = 0
            db.session.commit()
            return f"Now {follower_username} doesn't follow {followed_username}", 200
        else:
            raise ValidationError(status_code=404, error_code="Like_1",
                                  error_message=f"{follower_username} doesn't follow {followed_username}")

    def post(self, follower_username, followed_username):
        # adds a follower to a user
        like1_object = Follow()
        like2_object = Follow.query.filter_by(
            follower_username=followed_username, followed_username=follower_username).first()
        if like2_object:
            like2_object.follow_back = 1
            like1_object.follow_back = 1
        else:
            like1_object.follow_back = 0
        like1_object.follower_username = follower_username
        like1_object.followed_username = followed_username
        db.session.add(like1_object)
        db.session.commit()
        return f"{follower_username} now follows {followed_username}", 200
