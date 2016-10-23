# import the Flask class from the flask module
# import wraps from functools
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps  # wraps allows you to define and use decorators such as login_required
import sqlite3


# create the application object
app = Flask(__name__)

#use a random key generator
app.secret_key = "my precious"
app.database = "sample.db"


# login_required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    g.db = connect_db()  # g is an object specific to flask used to store a temporary object using a request #resets after each request
    cur = g.db.execute('select * from posts')  # query the database # fetches the data from posts
    posts = []
    for row in cur.fetchall():
        posts.append(dict(title=row[0], description=row[1]))

    # posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]  # cast to a dictionary

    g.db.close()  # close the database
    return render_template('index.html', posts=posts)  # render a template


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were just logged in!')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('welcome'))


def connect_db():
    return sqlite3.connect(app.database)  # create database object

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
