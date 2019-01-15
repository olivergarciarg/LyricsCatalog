from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from dbmodel import Base, User, MusicCategory, Song
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from functools import wraps
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets1.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///lyricscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Force login for API end point URI
def login_required(arguments):
    @wraps(arguments)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return arguments(*args, **kwargs)
        else:
            return redirect('/login')
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets1.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                   'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset user session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['provider']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps(
                   'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all users in JSON
@app.route('/users.json')
@login_required
def userJSON():
    users = session.query(User).all()
    return jsonify(User=[eachUser.serialize for eachUser in users])


# Show all categories and songs in JSON
@app.route('/categoriesfull.json')
@login_required
def catalogJSON():
    categories = session.query(MusicCategory).all()
    songs = session.query(Song).all()
    return jsonify(Songs=[eachSong.serialize for eachSong in songs],
                   Categories=[eachCategory.serialize
                   for eachCategory in categories])


# Show all categories in JSON
@app.route('/categories.json')
@login_required
def categoriesJSON():
    categories = session.query(MusicCategory).all()
    return jsonify(Categories=[eachCategory.serialize
                   for eachCategory in categories])


# API endpoints for all items of a specific category.
@app.route('/<string:category_name>/items.json')
@login_required
def itemsJSON(category_name):
    category = session.query(MusicCategory).filter_by(name=category_name).one()
    songs = session.query(Song).filter_by(music_category=category).all()
    return jsonify(Items=[eachSong.serialize for eachSong in songs])


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(MusicCategory).order_by(asc(MusicCategory.name))
    songs = session.query(Song).order_by(desc(Song.id)).limit(10).all()
    return render_template('categories.html',
                           categories=categories, songs=songs)


# Shows all the songs of a category
# Category name is an unique index
@app.route('/category/<string:category_name>/songs')
def showSongs(category_name):
    categories = session.query(MusicCategory).order_by(asc(MusicCategory.name))
    selected_category = session.query(MusicCategory).filter_by(
                        name=category_name).one()
    songs = session.query(Song).filter_by(
            category_id=selected_category.id).order_by(asc(Song.name)).all()
    return render_template('songs.html', categories=categories,
                           selected_category=selected_category, songs=songs)


# Shows the description of the selected item
# song_band together with song_name form an unique index
@app.route('/category/<string:category_name>/<string:song_band>'
           '/<string:song_name>')
def showSongsLyrics(category_name, song_band, song_name):
    song = session.query(Song).filter_by(band=song_band, name=song_name).one()
    if 'username' not in login_session:
        authorized_user = 0
    else:
        user_id = getUserID(login_session['email'])
        authorized_user = (user_id == song.user_id)
    return render_template('songlyrics.html', category_name=category_name,
                           song=song, authorized_user=authorized_user)


# Add a song
@app.route('/category/<string:category_name>/add', methods=['GET', 'POST'])
def addSong(category_name):
    # Checking that the user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    selected_category = session.query(
                        MusicCategory).filter_by(name=category_name).one()
    if request.method == 'POST':
        band_name = request.form['bandname']
        song_name = request.form['songname']
        newlyrics = request.form['lyrics']
        # Check for complete inputs
        if not band_name or not song_name or not newlyrics:
            flash('Band name, Song Name and Lyrics are mandatory')
            return render_template('addsong.html',
                                   selected_category=selected_category)
        # Verify that the song is not duplicated:
        # band_name + song_name must be unique
        song_id = getSongId(band_name, song_name)
        if not song_id:
            # Valid inputs
            user_id = getUserID(login_session['email'])
            newSong = Song(band=band_name, name=song_name, lyrics=newlyrics,
                           user_id=user_id, category_id=selected_category.id)
            session.add(newSong)
            session.commit()
            flash('%s - %s Has been added' % (newSong.band, newSong.name))
            return redirect(url_for('showSongsLyrics',
                            category_name=category_name,
                            song_band=newSong.band, song_name=newSong.name))
        else:
            flash('The song %s from %s is already registered, '
                  'enter a different song' % (song_name, band_name))
            return render_template('addsong.html',
                                   selected_category=selected_category)
    else:
        # if method = GET
        return render_template('addsong.html',
                               selected_category=selected_category)


def getSongId(band_name, song_name):
    try:
        song = session.query(Song).filter_by(
               band=band_name, name=song_name).one()
        return song.id
    except:
        return None


# Edit a song
@app.route('/category/<string:category_name>/<string:song_band>'
           '/<string:song_name>/edit', methods=['GET', 'POST'])
def editSong(category_name, song_band, song_name):
    # Double checking that the user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    editedSong = session.query(Song).filter_by(
                 band=song_band, name=song_name).one()
    selected_category = session.query(MusicCategory).filter_by(
                        name=category_name).one()
    user_id = getUserID(login_session['email'])
    # Double check if logged user is equal to song's user
    if editedSong.user_id != user_id:
        flash('You are not authorized to edit this song. '
              'Please create your own song in order to edit.')
        return redirect(url_for('showSongsLyrics', category_name=category_name,
                        song_band=editedSong.band, song_name=editedSong.name))
    if request.method == 'POST':
        band_name_new = request.form['bandname']
        song_name_new = request.form['songname']
        newlyrics = request.form['lyrics']
        # Check for complete inputs
        if not band_name_new or not song_name_new or not newlyrics:
            flash('Band name, Song Name and Lyrics are mandatory')
            return render_template('editsong.html',
                                   selected_category=selected_category,
                                   edited_song=editedSong)
        # Verify that the song is not duplicated:
        # band_name + song_name must be unique
        song_id = getSongId(band_name_new, song_name_new)
        if not song_id or song_id == editedSong.id:
            # Valid inputs
            editedSong.band = band_name_new
            editedSong.name = song_name_new
            editedSong.lyrics = newlyrics
            session.add(editedSong)
            session.commit()
            flash('%s - %s Has been edited'
                  % (editedSong.band, editedSong.name))
            return redirect(url_for('showSongsLyrics',
                            category_name=category_name,
                            song_band=editedSong.band,
                            song_name=editedSong.name))
        else:
            flash('The song %s from %s is already registered, enter a '
                  'different song' % (song_name_new, band_name_new))
            return render_template('editsong.html',
                                   selected_category=selected_category,
                                   edited_song=editedSong)
    else:
        # if method = GET
        return render_template('editsong.html',
                               selected_category=selected_category,
                               edited_song=editedSong)


# Delete a song
@app.route('/category/<string:category_name>/<string:song_band>/'
           '<string:song_name>/delete', methods=['GET', 'POST'])
def deleteSong(category_name, song_band, song_name):
    # Double checking that the user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    deletedSong = session.query(Song).filter_by(
                  band=song_band, name=song_name).one()
    selected_category = session.query(MusicCategory).filter_by(
                        name=category_name).one()
    user_id = getUserID(login_session['email'])
    # Double check if logged user is equal to song's user
    if deletedSong.user_id != user_id:
        flash('You are not authorized to delete this song. Please create your '
              'own song in order to delete.')
        return redirect(url_for('showSongsLyrics', category_name=category_name,
                        song_band=deletedSong.band,
                        song_name=deletedSong.name))
    if request.method == 'POST':
        # Verify that the song exist in the database
        song_id = getSongId(song_band, song_name)
        if not song_id:
            flash('Error: Could not find %s from %s in the database'
                  % (song_name, song_band))
            return redirect(url_for('showCategories'))
        else:
            session.delete(deletedSong)
            session.commit()
            flash('%s - %s Has been deleted'
                  % (deletedSong.band, deletedSong.name))
            return redirect(url_for('showSongs', category_name=category_name))
    else:
        # if method = GET
        return render_template('deletesong.html',
                               selected_category=selected_category,
                               deleted_song=deletedSong)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
