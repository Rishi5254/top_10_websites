from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, URL

from sqlalchemy import create_engine, Column, String, Integer, Float, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

import moviedata


engine = create_engine('sqlite:///movies-database.sqlite')
base = declarative_base()


class MoviesDb(base):
    __tablename__ = 'Movie'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(Integer)
    description = Column(String)
    rating = Column(Float)
    ranking = Column(Integer)
    review = Column(String)
    img_url = Column(Unicode)

    def __init__(self, id, title, year, description, rating, ranking, review, img_url):
        self.id = id
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.review = review
        self.img_url = img_url


base.metadata.create_all(engine)


class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired(), Length(min=8, max=20, message="limit 8-20 words")])
    submit = SubmitField("Add Movie")


class EditForm(FlaskForm):
    rating = FloatField('Edit Rating', validators=[DataRequired(), NumberRange(min=0, max=10, message='min and max is 0 to 10')])
    review = StringField('Edit Review', validators=[Length(min=5, max=20, message='limit 5 - 20 words only')])
    submit = SubmitField('Submit')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretcode'
Bootstrap(app)


@app.route("/")
def home():
    movies = []
    session = sessionmaker(engine)
    session = session()
    rank = 1
    for data in session.query(MoviesDb).order_by(MoviesDb.rating.desc()).all():
        movies.append(
            {
                "id": data.id,
                "title": data.title,
                "year": data.year,
                "description": data.description,
                "rating": data.rating,
                "ranking": rank,
                "review": data.review,
                "img_url": f"https://www.themoviedb.org/t/p/original{data.img_url}",
            }
        )
        rank += 1
    print(movies)
    lent = len(movies)
    print(lent)
    if lent > 0:
        for movie in movies:
            print(movie['title'])
    return render_template("index.html", movies=movies, length=lent)


@app.route('/add', methods=['GET', 'POST'])
def adding():
    form = AddForm()
    if form.validate_on_submit():
        session = sessionmaker(engine)
        session = session()
        try:
            id = [n for n in session.query(MoviesDb).all()][-1].id
        except IndexError:
            id = 0
        data = moviedata.search(form.title.data)
        tr = MoviesDb(id=id + 1, title=data['title'], year=data['release_date'].split('-')[0], description=data['overview'],
                      rating=data['vote_average'], ranking=None, review=form.review.data, img_url=data['poster_path'])
        session.add(tr)
        session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


@app.route('/delete/<int:num>')
def delete(num):
    session = sessionmaker(bind=engine)
    session = session()
    session.query(MoviesDb).filter(MoviesDb.id == num).delete()
    session.commit()
    return redirect(url_for('home'))


@app.route('/update/<int:num>/<title>/<float:rating>/<review>', methods=['GET', 'POST'])
def update(num, title, rating, review):
    form = EditForm()
    if form.validate_on_submit():
        new_rating = form.rating.data
        review= form.review.data
        session = sessionmaker(bind=engine)
        session = session()
        session.query(MoviesDb).filter(MoviesDb.id == num).update({MoviesDb.rating: new_rating, MoviesDb.review : review}, synchronize_session=False)
        session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, title=title, rating=rating, review=review)


if __name__ == '__main__':
    app.run(debug=True)