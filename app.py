#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dbm import gnu
import json
from pickle import TRUE
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)

    genres = db.relationship('Venue_Genre', backref='venues', lazy='dynamic')
    shows = db.relationship('Show', backref='venue', lazy='dynamic')

    def __repr__(self):
        return f"Venue: {self.id} - {self.name}"


class Venue_Genre(db.Model):
    __tablename__ = 'Venue_Genre'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
    genre = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Venue_Genre: {self.id} - {self.venue_id} - {self.genre}"


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)

    genres = db.relationship('Artist_Genre', backref='artists', lazy='dynamic')
    shows = db.relationship('Show', backref='artist', lazy='dynamic')

    def __repr__(self):
        return f"Artist: {self.id} - {self.name}"


class Artist_Genre(db.Model):
    __tablename__ = 'Artist_Genre'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
    genre = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Arstist_Genre: {self.id} - {self.artist_id} - {self.genre}"


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f"Show: {self.id}"

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    res_data = []
    today = datetime.now()
    venue_cities = db.session.query(Venue).distinct(Venue.city, Venue.state).all()
    for venue in venue_cities:
        data = {"city": venue.city, "state": venue.state}
        details = Venue.query.filter_by(city=venue.city, state=venue.state)
        venue_details = []
        for item in details:
            upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time >today
            ).count()
        
            venue_details.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "num_upcoming_shows": upcoming_shows
                }
            )
        data['venues'] = venue_details
        res_data.append(data)
    return render_template('pages/venues.html', areas=res_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    query = request.form.get("search_term", "").strip()
    today = datetime.now()
    data = []
    results = Venue.query.filter(Venue.name.ilike(f"%{query}%"))
    for venue in results:
        upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time >today
            ).count()

        res = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows,
        } 
        data.append(res)

    response = {
        "count": len(data),
        "data": data
    }   
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = {}
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            today = datetime.now()
            genres = [item.genre for item in venue.genres]

            upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time > today
            )
            upcoming_shows_details = []
            for show in upcoming_shows:
                artist = Artist.query.get(show.artist_id)
                artist_details = {
                    "artist_id": 4,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link,
                    "start_time": str(show.start_time)
                }
                upcoming_shows_details.append(artist_details)

            past_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time < today
            )
            past_shows_details = []
            for show in past_shows:
                artist = Artist.query.get(show.artist_id)
                artist_details = {
                    "artist_id": 4,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link,
                    "start_time": str(show.start_time)
                }
                past_shows_details.append(artist_details)
            
            data = {
                "id": venue.id,
                "name": venue.name,
                "genres": genres,
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "phone": venue.phone,
                "website": venue.website,
                "facebook_link": venue.facebook_link,
                "seeking_talent": venue.seeking_talent,
                "seeking_description": venue.seeking_description,
                "image_link": venue.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows)
            }
    except Exception as e:
        print(e)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    data = request.form
    name = data.get('name')
    city = data.get('city')
    state = data.get('state')
    address = data.get('address')
    phone = data.get('phone')
    genres = data.getlist('genres')
    seeking_talent = True if data.get('seeking_talent') == 'Yes' else False
    seeking_description = data.get('seeking_description')
    image_link = data.get('image_link')
    website = data.get('.website_link')
    facebook_link = data.get('facebook_link')

    try:
        new_venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            image_link=image_link,
            website=website,
            facebook_link=facebook_link
        )
        db.session.add(new_venue)
        db.session.commit()
        db.session.refresh(new_venue)

        for genre in genres:
            venue_genre = Venue_Genre(genre=genre)
            venue_genre.venue_id = new_venue.id
            db.session.add(venue_genre)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Venue ' + request.form['name'] + ' listing failed!', 'error')

    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            name = venue.name
            db.session.delete(venue)
            db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        print(e)
        return redirect(url_for('index'))

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist).options(load_only("id", "name")).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = {}
    try:
        artist = Artist.query.get(artist_id)
        if artist:
            today = datetime.now()
            genres = [item.genre for item in artist.genres]

            upcoming_shows = Show.query.filter_by(venue_id=artist.id).filter(
                Show.start_time > today
            )
            upcoming_shows_details = []
            for show in upcoming_shows:
                venue = Venue.query.get(show.venue_id)
                venue_details = {
                    "venue_id": 4,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": str(show.start_time)
                }
                upcoming_shows_details.append(venue_details)

            past_shows = Show.query.filter_by(venue_id=artist.id).filter(
                Show.start_time < today
            )
            past_shows_details = []
            for show in past_shows:
                venue = Venue.query.get(show.venue_id)
                venue_details = {
                    "venue_id": 4,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": str(show.start_time)
                }
                past_shows_details.append(venue_details)

            data = {
                "id": artist.id,
                "name": artist.name,
                "genres": genres,
                "city": artist.city,
                "state": artist.state,
                "phone": artist.phone,
                "website": artist.website,
                "facebook_link": artist.facebook_link,
                "seeking_talent": artist.seeking_talent,
                "seeking_description": artist.seeking_description,
                "image_link": artist.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows)
            }
    except Exception as e:
        print(e)

     # shows the artist page with the given artist_id
     # TODO: replace with real artist data from the artist table, using artist_id
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = request.form
    name = data.get('name')
    city = data.get('city')
    state = data.get('state')
    phone = data.get('phone')
    genres = data.getlist('genres')
    seeking_talent = True if data.get('seeking_talent') == 'Yes' else False
    seeking_description = data.get('seeking_description')
    image_link = data.get('image_link')
    website = data.get('.website_link')
    facebook_link = data.get('facebook_link')

    try:
        new_artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            image_link=image_link,
            website=website,
            facebook_link=facebook_link
        )
        db.session.add(new_artist)
        db.session.commit()
        db.session.refresh(new_artist)

        for genre in genres:
            artist_genre = Artist_Genre(genre=genre)
            artist_genre.artist_id = new_artist.id
            db.session.add(artist_genre)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Artist ' + request.form['name'] + ' listing failed!', 'error')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
#   flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
