from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from main import MoviesDb

engine = create_engine('sqlite:///movies-database.sqlite')

session = sessionmaker(bind=engine)
session = session()

for data in session.query(MoviesDb).order_by(MoviesDb.rating.desc()).all():
    print(data.id)

session.commit()