from pprint import pprint
from sre_constants import error

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from typing_extensions import MappingView
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Website the Movie database API
API_Key = os.environ.get("API_Key")
url =os.environ.get("URL")
headers = {"accept": "application/json"}



# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APP_SECRETE_KEY")
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

# Configure the SQlite database, relative to the app instance folder.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies-collection.db"

# Create the Extension
db = SQLAlchemy(model_class=Base)

# Initialize the app
db.init_app(app)

# Flask-WTF Forms
class RateMovieForm(FlaskForm):
    """Form for rating and reviewing movies."""
    your_rating = StringField('Your Rating upto 10')
    your_review = StringField('Your Review')
    submit = SubmitField("Done")

class AddMovieForm(FlaskForm):
    """Form for adding a new movie by title."""
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

# CREATE TABLE
class Movies(db.Model):
   """Model representing a movie in the database."""
   id: Mapped[int] = mapped_column(Integer, primary_key=True)
   title: Mapped[str]= mapped_column(String(250), unique= True, nullable=False)
   year: Mapped[str] = mapped_column(String(10),nullable=False)
   description:Mapped[str] = mapped_column(String(500),nullable=False)
   rating:Mapped[float] = mapped_column(Float,nullable = True)
   ranking:Mapped[float] = mapped_column(Float,nullable=True)
   review:Mapped[str] = mapped_column(String(1000),nullable=True)
   img_url:Mapped[str] = mapped_column(String(1000), nullable=False)


   def __repr__(self):
       return f" <Movie {self.title}>"

# Create table schema in the database,Requires application context
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()

    return render_template("index.html",movies=movies)

@app.route("/edit",methods=["GET","POST"])
def edit():
    edit_form = RateMovieForm()
    movie_id =int(request.args.get("id"))

    if not movie_id:
       return redirect(url_for('home'))

    movie = db.session.execute(db.select(Movies).where(Movies.id == int(movie_id))).scalar()
    if not movie:
        return  redirect(url_for('home'))

    if edit_form.validate_on_submit() and request.method=="POST":
        try:
             new_rating = edit_form.your_rating.data
             new_review = edit_form.your_review.data
             print(new_rating)
             print(new_review)
             movie.rating = new_rating
             movie.review = new_review
             db.session.commit()
             return  redirect(url_for('home'))
        except Exception as e:
            print(f"Error updating movie: {e}")
            db.session.rollback()
            return render_template("error.html", error="Failed to update movie.")



    # Prefill form with existing data
    edit_form.your_rating.data = movie.rating
    edit_form.your_review.data = movie.review

    return render_template('edit.html',form= edit_form)

@app.route("/delete",methods=["GET","POST"])
def delete():
    """Delete a movie from the database."""
    movie_id = request.args.get("id")
    movie = db.session.execute(db.select(Movies).where(Movies.id==int(movie_id))).scalar()
    name = movie.title
    db.session.delete(movie)
    db.session.commit()
    print(f"Movie {name} has been deleted!!" )
    return redirect((url_for('home')))

@app.route("/add",methods = ["GET","POST"])
def add():
    """Add a new movie using TMDb API."""
    add_form = AddMovieForm()
    if add_form.validate_on_submit() and request.method== "POST":
        movie_name = add_form.title.data
        try:
            response = requests.get(url, params={"api_key": API_Key, "query": movie_name}, headers=headers)
            data = response.json()["results"]
            print(data)
            return render_template('select.html',data = data)
        except Exception as e:
            print(f"Error fetching movie data: {e}")
            return render_template('error.html',error = "Failed to fetch movie data. Try again later.")


    return render_template('add.html',form = add_form)

@app.route("/find")
def find_movie():
    """Find a movie using its TMDb ID and add it to the database."""
    movie_api_id = request.args.get("id")
    if movie_api_id:
        url = f"https://api.themoviedb.org/3/movie/{movie_api_id}?language=en-US/"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyNzIxNGJlNDJkNWI3N2Y3YTBkOGRkY2I1NDFhMWIwYyIsIm5iZiI6MTczMjcwNjM4Mi4yMTMzODQ5LCJzdWIiOiI2NzQ2ZmJlMGQ3YTIwNTcxNWI2MTY1NzgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.pmmtQezfR5qzUXion3XV6F7Y7dF5YfaYrD9lsFs9380"
        }

        try:
            response = requests.get(url,params={"api_key" :API_Key,"language": "en-US"})
            data = response.json()
            pprint(data)
            new_movie = Movies(
                title= data["title"],
                year= data["release_date"].split("-")[0],
                description = data["overview"],
                rating = 0,
                ranking = 10,
                review = "Your Review",
                img_url=f"https://image.tmdb.org/t/p/original/{data['poster_path']}"

            )

            db.session.add(new_movie)
            db.session.commit()
            return redirect((url_for("home")))

        except Exception as e:
            print(f"Error adding movie: {e}")
            db.session.rollback()
            return  render_template('error.html', error ="Failed to add movie. Try again later.")



if __name__ == '__main__':
    app.run(debug=True)
