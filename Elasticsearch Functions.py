from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Text, Date, Integer, String
from sqlalchemy.orm import relationship
from elasticsearch import Elasticsearch

#########################################
# NOTE TO TEAMMATES:
# Do not run this code directly from the file. Take functions you need for your part instead.
# The only functions designed for use outside of this program are search(), update_elasticsearch(), and hard_update_elasticsearch()
# You also need to setup elasticsearch on your machine. Here are the steps to do it:
#    1. Download the elasticsearch client from this link - https://www.elastic.co/downloads/elasticsearch
#    2. Unzip elasticsearch
#    3. From the elasticsearch folder, go to the config folder. Open the elasticsearch YAML source file
#    4. In this file, change all of these parameters to FALSE. Make sure to save the file, otherwise it will not apply these changes:
#        - xpack.security
#        - xpack.security.enrollment
#        - xpack.security.http.ssl
#        - xpack.security.transport.ssl
#    5. Open the command line. Navigate to the elasticsearch/bin folder.
#    6. type 'elasticsearch' into the command line from this folder. It should run elasticsearch
# Note that the command line window running elasticsearch should be unusable if successful. To exit, just command C.
#########################################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://CMSC447Team5:teamFive@localhost/recipes_db'

db = SQLAlchemy(app)

es = Elasticsearch(['http://localhost:9200'])


# Define the tables in python classes
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(500), unique=True, nullable=False)
    password = db.Column('password', db.String(500), nullable=False)
    email = db.Column('email', db.String(500), nullable=False)

    recipe = relationship("Recipe", backref='user')


class Recipe(db.Model):
    __tablename__ = 'recipe'
    recipe_id = db.Column('recipe_id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, ForeignKey('user.user_id'))
    title = db.Column('title', db.String(500), nullable=False)
    description = db.Column('description', db.Text, nullable=False)
    equipment = db.Column('equipment', db.Text, nullable=False)
    ingredients = db.Column('ingredients', db.Text, nullable=False)
    instructions = db.Column('instructions', db.Text, nullable=False)
    upload_date = db.Column('upload_date', db.Date, nullable=True)


# FUNCTION: search_recipe
# searches the recipe portion of Elasticsearch's database for the search_term paramter
# paramters:
# string search_term - character(s) that will be searched.
# returns a jsonified list of dictionaries
def search_recipe(search_term):
    search_query = {
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["title", "description", "equipment", "ingredients", "instructions"],
                "fuzziness": "AUTO"
            }
        }
    }
    result = es.search(index='recipe_index', body=search_query)
    hits = result["hits"]["hits"]
    return jsonify(hits)


def print_search_results(hits):
    for hit in hits:
        print(hit["_source"]["title"])
    return


# makes sure elasticsearch database matches the MySQL database
# This can be used at startup and periodically
# Use this after adding or modifying a recipe
def update_elasticsearch():
    all_users = User.query.all()  # In order to access data from all_users, do all_users[n].column, to get specific data
    for user in all_users:
        user_entity = {
            'user_id': user.user_id,
            'username': user.username,
            'password': user.password,
            'email': user.email
        }
        es.index(index='user_index', id=user.user_id, body=user_entity)
        es.indices.refresh(index='user_index')

    all_recipes = Recipe.query.all()
    for recipe in all_recipes:
        recipe_entity = {
            'recipe_id': recipe.recipe_id,
            'user_id': recipe.user_id,
            'title': recipe.title,
            'description': recipe.description,
            'equipment': recipe.equipment,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'upload_date': recipe.upload_date
        }
        es.index(index='recipe_index', id=recipe.recipe_id, body=recipe_entity)
        es.indices.refresh(index='recipe_index')
    return


# Same as update_elasticsearch, except it clears elasticsearch first
# Use after adding, modifying or removing a recipe, or for testing purposes
def hard_update_elasticsearch():
    es.indices.delete(index='user_index')
    es.indices.delete(index='recipe_index')
    update_elasticsearch()
    return


# Testing code for each helper function
with app.app_context():

    update_elasticsearch()

    hits = search_recipe("pasta")
    print(hits)
    #print_search_results(hits)
    # delete entries for next testing run
    #es.indices.delete(index='user_index')

    user = User.query.get(1)
    recipe = Recipe.query.get(1)

    print(user)
    print(recipe)

# close elasticsearch
es.close()
