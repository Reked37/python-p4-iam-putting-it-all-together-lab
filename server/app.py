from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import ipdb
from config import app, db, api
from models import User, Recipe
from flask_bcrypt import bcrypt

class Signup(Resource):
    def post(self):
        json=request.get_json()
        user=User(
            username=json.get('username'),
            
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )
        user.password_hash=json.get('password')
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id']=user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {"error":"Unprocessable Entity"}, 422

class Login(Resource):
    def post(self):
        user=User.query.filter(User.username == request.get_json().get('username')).first()
        if user:
            session['user_id']=user.id
            return user.to_dict()
        else:
            return {"message":"401: Unauthorized"}, 401

class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id']=None
            return {"message": "204: No Content"}, 204
        else:
            return{"Error":"401 Unauthorized"}, 401

class CheckSession(Resource):
    def get(self):
        # user_id=session['user.id']
        user=User.query.filter(User.id == session['user_id']).first()
        if user:
            # ipdb.set_trace()
            return user.to_dict(), 200
        else:
            return {"error":"401: Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            user=User.query.filter(User.id == session['user_id']).first()
            recipe_dict=[recipe.to_dict() for recipe in user.recipes]
            
            return recipe_dict, 200
        else:
            return {"error":"401: Unauthorized"}, 401

    def post(self):
        if session['user_id']:
            json=request.get_json()
            if len(json['instructions'])>=50:
                recipe=Recipe(
                    title=json['title'],
                    instructions=json['instructions'],
                    minutes_to_complete=json['minutes_to_complete'],
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            else:
                return {"Error": "422: Unprocessable Entity"}, 422    

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')
# ipdb.set_trace()

if __name__ == '__main__':
    app.run(port=5555, debug=True)
