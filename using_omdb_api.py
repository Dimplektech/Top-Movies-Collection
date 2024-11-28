from pprint import pprint

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

# Website the Movie database API
API_Key ="9525e82d"


url = " http://www.omdbapi.com/"

headers = {"accept": "application/json"}


class RateMovieForm(FlaskForm):
    your_rating = StringField('Your Rating upto 10')
    your_review = StringField('Your Review')
    submit = SubmitField("Done")

class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

# Configure the SQlite database, relative to the app instance folder.

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies-collection.db"

# Create the Extension
db = SQLAlchemy(model_class=Base)

# Initialize the app
db.init_app(app)

# CREATE TABLE
class Movies(db.Model):
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


# with app.app_context():
# First movie
#     new_movie = Movies(title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#    db.session.add(new_movie)
 #   db.session.commit()
#
# with app.app_context():
#     # Second Movie
#
#     second_movie = Movies(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()



@app.route("/")
def home():
    movies = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars()

    return render_template("index.html",movies=movies)

@app.route("/edit",methods=["GET","POST"])
def edit():
    edit_form = RateMovieForm()
    movie_id =int(request.args.get("id"))
    print(movie_id)

    if not movie_id:
        print("no movie_id")
        return redirect(url_for('home'))

    movie = db.session.execute(db.select(Movies).where(Movies.id == int(movie_id))).scalar()


    if edit_form.validate_on_submit() and request.method=="POST":
         new_rating = edit_form.your_rating.data
         new_review = edit_form.your_review.data
         print(new_rating)
         print(new_review)
         movie.rating = new_rating
         movie.review = new_review
         db.session.commit()
         return  redirect(url_for('home'))
    else:

        edit_form.your_rating.data = movie.rating
        edit_form.your_review.data = movie.review

    return render_template('edit.html',form= edit_form)

@app.route("/delete",methods=["GET","POST"])
def delete():
    movie_id = request.args.get("id")
    movie = db.session.execute(db.select(Movies).where(Movies.id==int(movie_id))).scalar()
    name = movie.title
    db.session.delete(movie)
    db.session.commit()
    print(f"Movie {name} has been deleted!!" )
    return redirect((url_for('home')))

@app.route("/add",methods = ["GET","POST"])
def add():
    add_form = AddMovieForm()
    if add_form.validate_on_submit() and request.method== "POST":
        movie_name = add_form.title.data
        response = requests.get(url, params={"apikey": API_Key, "t": movie_name})
        data = response.json()
        pprint(data)
        return render_template('select.html',data = data)

    # with app.app_context():
    #
    #     second_movie = Movies(
    #         title="Avatar The Way of Water",
    #         year=2022,
    #         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    #         rating=7.3,
    #         ranking=9,
    #         review="I liked the water.",
    #         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    #     )
    #     db.session.add(second_movie)
    #     db.session.commit()
    # return redirect(url_for('home'))
    return render_template('add.html',form = add_form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        url = f"https://api.themoviedb.org/3/movie/{movie_api_id}?language=en-US/"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyNzIxNGJlNDJkNWI3N2Y3YTBkOGRkY2I1NDFhMWIwYyIsIm5iZiI6MTczMjcwNjM4Mi4yMTMzODQ5LCJzdWIiOiI2NzQ2ZmJlMGQ3YTIwNTcxNWI2MTY1NzgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.pmmtQezfR5qzUXion3XV6F7Y7dF5YfaYrD9lsFs9380"
        }

        response = requests.get(url,params={"api_key" :API_Key,"language": "en-US"})
        data = response.json()
        print(data)
        # new_movie = Movies(
        #     title= data["title"],
        #     year= data["release_date"].split("-")[0],
        #     description= data["overview"],
        #     rating = 0,
        #     ranking = 10,
        #     review = "Your Review",
        #     img_url=f"https://image.tmdb.org/t/p/original/{data['poster_path']}"
        #
        # )

        #db.session.add(new_movie)
        db.session.commit()
        return redirect((url_for("home")))



if __name__ == '__main__':
    app.run(debug=True)
