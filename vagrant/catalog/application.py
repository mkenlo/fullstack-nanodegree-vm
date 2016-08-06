import random
import string
import catalog
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']


@app.route('/')
@app.route('/catalog')
def home():
    params = dict()
    params["categories"] = catalog.getAllCategories()
    params["recent_items"] = catalog.getRecentItems()
    if isLogged():
        params["username"] = login_session['username']
    return render_template('index.html', **params)


@app.route('/catalog/category/<int:category_id>/items')
def itemsByCategory(category_id):
    params = dict()
    params["categories"] = catalog.getAllCategories()
    params['onecategory'], params[
        'itemsByCategory'] = catalog.getItemsCategory(category_id)
    if isLogged():
        params["username"] = login_session['username']
    #print params['category'].name
    #print params['category'].id
    return render_template('index.html', **params)


@app.route('/catalog/items/<int:item_id>')
def itemsDescription(item_id):
    params = dict()
    params["categories"] = catalog.getAllCategories()
    params['unique_item'] = catalog.getItemById(item_id)
    if isLogged():
        params["username"] = login_session['username']
    return render_template('item.html', **params)


@app.route('/catalog/items/add', methods=['GET', "POST"])
def itemsAdd():
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['item_name']
        description = request.form['item_description']
        category_id = request.form['category_id']
        if name and description and category_id:
            catalog.addItem(name, description, category_id)
            flash("New item added: %s" % name, "success")
        return redirect(url_for('itemsByCategory', category_id=category_id))
    else:
        params = dict()
        params["categories"] = catalog.getAllCategories()
        params["username"] = login_session['username']
        return render_template('item.html', **params)


@app.route('/catalog/items/edit/<int:item_id>', methods=['POST'])
def itemsEdit(item_id):
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['item_name']
        description = request.form['item_description']
        category_id = request.form['category_id']
        if name and description and category_id:
            catalog.editItem(item_id, name, description, category_id)

    return redirect(url_for('itemsDescription', item_id=item_id))


@app.route('/catalog/items/delete', methods=['POST'])
def itemsDelete():
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        item_id = request.form['item_id']
        catalog.deleteItem(item_id)
        flash("An item has been deleted", "success")
    return redirect(url_for('home'))


@app.route('/catalog/category/add', methods=['GET', 'POST'])
def categoryAdd():
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
     
    if request.method == 'POST':
        name = request.form['cat_name']
        catalog.addCategory(name)
        flash("New category added: %s"%name, "success")
        return redirect(url_for('home'))
    return render_template('category.html', username = login_session['username'])


@app.route('/catalog/category/edit/<int:category_id>', methods=['GET', 'POST'])
def categoryEdit(category_id):
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['cat_name']
        if name:
            catalog.editCategory(category_id, name)
            # flash("Category updated: %s"%name, "success")
        
    params = dict()
    params["username"] = login_session['username']
    params["category"] = catalog.getCategoryById(category_id)
    return render_template('category.html', **params)


@app.route('/catalog/category/delete', methods=['POST'])
def categoryDelete():
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    if request.method == 'POST':
        category_id = request.form['category_id']
        catalog.deleteCategory(category_id)
        flash("A category has been deleted", "success")
    return redirect(url_for('home'))


@app.route('/catalog/category/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    if not isLogged():
        flash("Login required", "warning")
        return redirect(url_for('home'))
    cat, items = catalog.getItemsCategory(category_id)
    
    return jsonify(categoryItems=[i.serialize for i in items])


@app.route('/login')
def login():
    if isLogged():
        flash("You are logged as %s" % login_session['username'], "success")
        return redirect(url_for('home'))
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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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

    # stored_credentials = login_session.get('credentials')
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # login_session['credentials'] = credentials

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

  
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
   
    
    return output


@app.route('/logout')
def logout():
      # Only disconnect a connected user.
    # credentials = login_session.get('credentials')
    access_token = login_session.get('access_token')
    if access_token is None:
        flash("User not connected.","warning")
        return redirect(url_for('home'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]   

    if result['status'] == '200':
        # Reset the user's sesson.
        # del login_session['credentials']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash("You've logout Successfully","success")
        return redirect(url_for('home'))
    else:
        # For whatever reason, the given token was invalid.
        flash("Logout Error: Failed to revoke token for given user.","danger")
        return redirect(url_for('home'))
        


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

def isLogged():
    if login_session.get('access_token') is None:
        return False
    return True

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
