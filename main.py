from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies-collection.db'
db = SQLAlchemy(app)
api_key = '7cfa3101988db1f1049eaa0e04d076ed'


class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


class RateMovieForm(FlaskForm):
    rating_input = StringField("Your Rating Out of 10 e.g. 7.5")
    review_input = StringField("Your Review")
    submit = SubmitField("Done")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000))
    rating = db.Column(db.Float(10))
    ranking = db.Column(db.Integer, unique=True)
    review = db.Column(db.String(500))
    img_url = db.Column(db.String(500))

    def __repr__(self):
        return f'< {self.title} >'


db.create_all()


@app.route("/")
def home():
    all_movie = db.session.query(Movie).order_by(Movie.rating)
    for movie in all_movie:
        movie.ranking = len(list(all_movie)) - list(all_movie).index(movie)
    return render_template("index.html", movies=all_movie)


@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating_input.data)
        movie.review = form.review_input.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        parameter = {
            'api_key': '7cfa3101988db1f1049eaa0e04d076ed',
            'language': 'en-US',
            'query': form.title.data,
        }
        response = requests.get('https://api.themoviedb.org/3/search/movie?', params=parameter).json()['results']
        return render_template('select.html', response=response)
    return render_template("add.html", form=form)


@app.route("/get_detail", methods=["GET", "POST"])
def get_detail():
    movie_id = request.args.get("ids")
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US')
    data = response.json()
    new_movie = Movie(
                title=data['title'],
                year=data['release_date'][0:4],
                description=data['overview'],
                img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('rate_movie', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
