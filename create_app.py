import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.api import *
from flask_login import LoginManager
from flask_restful import Api

basedir = os.path.abspath(os.path.dirname(__file__))
db = db
login_manager = LoginManager()
api = Api()


def create_app():
    app = Flask(__name__)
    if os.getenv('ENV', "development") == "production":
        raise Exception("currently no production config is setup.")
    else:
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    # Adding Api Resources
    api.add_resource(User_profile_API, '/api/User_profile',
                     '/api/User_profile/<string:username>')
    api.add_resource(Posts_API, '/api/Posts', '/api/Posts/<int:p_id>')
    api.add_resource(Comments_API, '/api/Comments/<int:p_id>',
                     '/api/Comments/<int:c_id>')
    api.add_resource(Likes_API, '/api/Likes/<int:p_id>',
                     '/api/Likes/<int:l_id>', '/api/Likes/<string:username>/<int:p_id>')
    api.add_resource(Follow_API, '/api/Follow/<string:username>',
                     '/api/Likes/<string:follower_username>/<string:followed_username>')
    api.init_app(app)
    login_manager.init_app(app)

    return app
