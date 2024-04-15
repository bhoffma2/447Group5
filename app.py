from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Creating Flask app
app = Flask(__name__)

# Creating SQLAlchemy instance
db = SQLAlchemy()

user = "root"
pin = "teamFive"
host = "localhost"
db_name = "recipes_db"

# Configuring database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{pin}@{host}/{db_name}"

# Disable modification tracking
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing Flask app with SQLAlchemy
db.init_app(app)


# Creating recipe model
class Recipes(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, unique=True)
    ingredients = db.Column(db.String(500), nullable=False)


def create_db():
    with app.app_context():
        db.create_all()


# Home route, displays all recipes
@app.route("/")
def home():
    details = Recipes.query.all()
    return render_template("home.html", details=details)


@app.route("/add", methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        recipe_name = request.form.get('name')
        recipe_ingredients = request.form.get('ingredients')

        new_recipe = Recipes(
            name=recipe_name,
            ingredients=recipe_ingredients
        )
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("add_recipe.html")


@app.route("/remove", methods=['GET', 'POST'])
def remove_recipe():
    if request.method == 'POST':
        recipe_name = request.form.get('name')
        recipe_to_delete = Recipes.query.filter_by(name=recipe_name).first()

        if recipe_to_delete:
            # Delete the recipe
            db.session.delete(recipe_to_delete)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            # Recipe not found, handle accordingly (e.g., display an error message)
            return render_template("remove_recipe.html", error="Recipe not found")

    return render_template("remove_recipe.html")


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
