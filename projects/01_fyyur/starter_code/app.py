#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Artist, Show
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#migrate = Migrate(app, db)

# TODO: (Done in config file) connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  areas=[]
  data= Venue.query.all()
  for place in Venue.query.distinct(Venue.city,Venue.state).all():
    areas.append({
      'city':place.city,
      'state': place.state,
      'venues':[{
        'id': d.id,
        'name': d.name
      } for d in data if d.city == place.city and d.state == place.state]
    })
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search = request.form.get('search_term', '')
  venues=Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
  data=[]
  for venue in venues:
    data.append(venue)
  response={
    "count":len(venues),
    "data":data
    
    }
  

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, data=data,search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
 
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time > datetime.now()).all()

  data= {'id': venue_id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website,
    'genres': venue.genres,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'upcoming_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time
        } for artist, show in upcoming_shows], 
    'past_shows': [{
      'artist_id': artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
      } for artist, show in past_shows],  
    'upcoming_shows_count': len(upcoming_shows),
    'past_shows_count': len(past_shows)}
  
  

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error=False
  name=request.form.get('name', '')
  city=request.form.get('city', '')
  state=request.form.get('state', '')
  address=request.form.get('address','')
  phone=request.form.get('phone','')
  image_link=request.form.get('image_link', '')
  genres=request.form.getlist('genres')
  facebook_link=request.form.get('facebook_link','')
  website=request.form.get('website','')
  seeking_talent=request.form.get('seeking_talent')
  seeking_description=request.form.get('seeking_description','')
  if seeking_talent=='Yes':
    seeking_talent=True
  else:
    seeking_talent=False
  
  try:
    venue=Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,website=website,seeking_description=seeking_description)  
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occured. Venue could not be listed.')
  finally:
    db.session.close()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error:
    return render_template('/errors/500.html')
  else:
    return redirect(url_for('venues'))

@app.route('/venues/<venue_id>/delete', methods=['GET','POST'])
def delete_venue(venue_id):
  error=False
  try:
    d=Venue.query.filter_by(id=venue_id).first()
    db.session.delete(d)
    db.session.commit()
    flash('Venue deleted successfully!')
  except Exception:
    flash('An error occurred. The venue could not be deleted.')
    error=True
    db.session.rollback()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  finally:
    db.session.close()
  if error:
    return render_template('/errors/500.html')
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  else:
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  artists=Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  data=[]
  for artist in artists:
    data.append(artist)
  response={
    "count":len(artists),
    "data":data
    
    }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  return render_template('pages/search_artists.html', results=response, search_term=search, data=data)

@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  artist = Artist.query.filter_by(id=artist_id).first_or_404()

  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(Show.artist_id == artist_id,Show.venue_id == Venue.id,Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(Show.artist_id == artist_id,Show.venue_id == Venue.id,Show.start_time > datetime.now()).all()

  data= {'id': artist_id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website': artist.website,
    'genres': artist.genres,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'upcoming_shows': [{
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time
        } for venue, show in upcoming_shows], 
    'past_shows': [{
      'venue_id': venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time
      } for venue, show in past_shows],  
    'upcoming_shows_count': len(upcoming_shows),
    'past_shows_count': len(past_shows)}
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.image_link.data=artist.image_link
  form.genres.data=artist.genres
  form.facebook_link.data=artist.facebook_link
  form.website.data=artist.website
  form.seeking_venue.data=artist.seeking_venue
  form.seeking_description.data=artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist.name=request.form.get('name', '')
  artist.city=request.form.get('city', '')
  artist.state=request.form.get('state', '')
  artist.phone=request.form.get('phone','')
  artist.image_link=request.form.get('image_link', '')
  artist.genres=request.form.getlist('genres')
  artist.facebook_link=request.form.get('facebook_link','')
  artist.website=request.form.get('website','')
  artist.seeking_venue=request.form.get('seeking_venue')
  artist.seeking_description=request.form.get('seeking_description','')
  
  if artist.seeking_venue=='No':
    artist.seeking_venue=False
  else:
    artist.seeking_venue=True

  db.session.commit()

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', form=form, artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.image_link.data=venue.image_link
  form.genres.data=venue.genres
  form.facebook_link.data=venue.facebook_link
  form.website.data=venue.website
  form.seeking_talent.data=venue.seeking_talent
  form.seeking_description.data=venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form=VenueForm(request.form)
  venue=Venue.query.get(venue_id)
  venue.name=request.form.get('name', '')
  venue.city=request.form.get('city', '')
  venue.state=request.form.get('state', '')
  venue.address=request.form.get('address','')
  venue.phone=request.form.get('phone','')
  venue.image_link=request.form.get('image_link', '')
  venue.genres=request.form.getlist('genres')
  venue.facebook_link=request.form.get('facebook_link','')
  venue.website=request.form.get('website','')
  venue.seeking_talent=request.form.get('seeking_talent')
  venue.seeking_description=request.form.get('seeking_description','')
  
  if venue.seeking_talent=='No':
    venue.seeking_talent=False
  else:
    venue.seeking_talent=True

  
  #venue=Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,website=website,seeking_description=seeking_description)
  db.session.commit()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', form=form, venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error=False
  name=request.form.get('name', '')
  city=request.form.get('city', '')
  state=request.form.get('state', '')
  phone=request.form.get('phone','')
  image_link=request.form.get('image_link', '')
  genres=request.form.getlist('genres')
  facebook_link=request.form.get('facebook_link','')
  website=request.form.get('website','')
  seeking_venue=request.form.get('seeking_venue')
  seeking_description=request.form.get('seeking_description','')

  if seeking_venue=='Yes':
    seeking_venue=True
  else:
    seeking_venue=False
  
  try:
    artist=Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,website=website,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. The artist could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  if error:
    return render_template('/errors/500.html')
  else:
      return redirect(url_for('artists'))

@app.route('/artists/<artist_id>/delete', methods=['GET','POST'])
def delete_artist(artist_id):
  error=False
  try:
    d=Artist.query.filter_by(id=artist_id).first()
    db.session.delete(d)
    db.session.commit()
    flash('Artist deleted successfully!')
  except Exception:
    flash('An error occurred. The artist could not be deleted.')
    error=True
    db.session.rollback()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  finally:
    db.session.close()
  if error:
    return render_template('/errors/500.html')
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  else:
    return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data= Show.query.order_by(Show.start_time)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False
  artist_id=request.form.get('artist_id', '')
  venue_id=request.form.get('venue_id', '')
  start_time=request.form.get('start_time', '')
  show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  try:
    db.session.add(show)
    db.session.commit()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception:
    error=True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error:
    return render_template('/errors/500.html')
  else:
    return redirect(url_for('shows'))

@app.route('/shows/<show_id>/delete', methods=['GET','POST'])
def delete_show(show_id):
  error=False
  try:
    d=Show.query.filter_by(id=show_id).first()
    db.session.delete(d)
    db.session.commit()
    flash('Show deleted successfully!')
  except Exception:
    flash('An error occurred. The show could not be deleted.')
    error=True
    db.session.rollback()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  finally:
    db.session.close()
  if error:
    return render_template('/errors/500.html')
  else:
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(409)
def duplicate_resource(error):
    return render_template('errors/409.html'), 409




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
