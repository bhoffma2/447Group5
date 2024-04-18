from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# Creating Flask app
app = Flask(__name__)
app.secret_key = 'teamFive'

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


class Recipes(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, unique=True)
    ingredients = db.Column(db.String(500), nullable=False)


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)


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


@app.route("/edit", methods=['GET', 'POST'])
def edit_recipe():
    if request.method == 'POST':
        # Get updated recipe details from the form
        recipe_name = request.form.get('name')
        recipe_ingredients = request.form.get('ingredients')
        recipe_to_edit = Recipes.query.filter_by(name=recipe_name).first()

        # Update the recipe with the new details
        if recipe_to_edit:
            recipe_to_edit.name = recipe_name
            recipe_to_edit.ingredients = recipe_ingredients
            # Commit the changes to the database
            db.session.commit()

        # Redirect to the home page
        return redirect(url_for('home'))

    return render_template("edit_recipe.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="Username already exists. Please choose a different one.")

        # Create a new user
        new_user = Users(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Store the username in the session to indicate the user is logged in
        session['username'] = username

        return redirect(url_for('home'))

    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password match
        current_user = Users.query.filter_by(username=username, password=password).first()
        if current_user:
            # Store the username in the session to indicate the user is logged in
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
