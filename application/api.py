from flask_restful import Resource, request
from flask_restful import fields, marshal_with

from application.database import db
from application.models import User, User_profile, Posts, Likes, Comments, Follow
from application.errors import *

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class User_profile_API(Resource):

    output = {"username": fields.String, "first_name": fields.String, "last_name": fields.String, "profile_image": fields.String}

    @marshal_with(output)
    def get(self,username):
        u_obj = User_profile.query.filter_by(username=username).first()
        if u_obj:
            return u_obj, 200
        else:
            raise UserNotFound(status_code=404)
    def delete(self,username):
        u_obj = User.query.filter_by(username=username).first()
        if u_obj:
            db.session.delete(u_obj)
            db.session.commit()
            return f"{username} profile deleted", 200
        else:
            raise UserNotFound(status_code=404)
    
    @marshal_with(output)
    def put(self,username):
        u_obj = User_profile.query.filter_by(username=username).first()
        if u_obj:
            form_data = request.get_json()
            if form_data.get("profile_image") != u_obj.profile_image:
                file_path = os.path.join(basedir,'../static/profile_images/'+f'{username}_'+f'{u_obj.profile_image}')
                cmd = 'rm ' + f'{file_path}'
                os.system(cmd)
            u_obj.first_name = form_data.get("first_name")
            u_obj.last_name = form_data.get("last_name")
            u_obj.email = form_data.get("email")
            u_obj.profile_image = form_data.get("profile_image")

            db.session.commit()

            return u_obj, 200
        else:
            raise UserNotFound(status_code=404)
    
    @marshal_with(output)
    def post(self):
        form_data = request.get_json()
        username = form_data.get("username")
        if not User_profile.query.filter_by(username=username).first():
            if username:
                u_obj = User_profile()
                u = User(username = form_data.get("username"), password = form_data.get("password"), email = form_data.get("email"))
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
                raise ValidationError(status_code=400,error_code="user_2",error_message="username not given.")
        else:
            raise ValidationError(status_code=400,error_code="user_1",error_message="username already exists.")

class Posts_API(Resource):
    def get(self,username):
        pass
    def delete(self,username):
        pass
    def put(self,username):
        pass
    def post(self):
        pass

class Follow_API(Resource):
    def get(self,username):
        pass
    def delete(self,username):
        pass
    def put(self,username):
        pass
    def post(self):
        pass

class Comments_API(Resource):
    def get(self,username):
        pass
    def delete(self,username):
        pass
    def put(self,username):
        pass
    def post(self):
        pass

class Likes_API(Resource):
    def get(self,username):
        pass
    def delete(self,username):
        pass
    def put(self,username):
        pass
    def post(self):
        pass

class Follow_API(Resource):
    def get(self,username):
        pass
    def delete(self,username):
        pass
    def put(self,username):
        pass
    def post(self):
        pass