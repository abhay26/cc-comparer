import os
import requests
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from bs4 import BeautifulSoup
from userdata import *

app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'cc.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('CC_SETTINGS', silent=True)


def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/users/<name1>/<name2>')
@app.route('/users/<name1>/')
def user(name1=None,name2=None):
	db = get_db()
	data1 = getData(name1)
	if 'error' in data1:
		return render_template('user.html',error="Either invalid username or some problem with the site!")
	compute(data1['contests'])
	if name2:
		data2 = getData(name2)
		compute(data2['contests'])
		if 'error' in data2:
			return render_template('user.html',error="Either invalid username or some problem with the site!")
		lis = [val for val in data1['contests'] if val in data2['contests']]
		contestData = getAllRanksMulti(lis, name1, name2, db)
		return render_template('users.html', data1=data1,data2=data2, contestData=contestData, union=lis)
	else:
		contestData = getAllRanks(data1['contests'], name1, db)
		return render_template('user.html',data1=data1,contestData=contestData)

def compute(contests):
	db = get_db()
	for cont in contests:
		cur = db.execute('select * from entries where contest=?',(cont, ))
		entries = cur.fetchall()
		entries = list(entries)
		if len(entries) > 0:
			continue
		print cont
		data = loadContestData(cont)
		for row in data:
			db.execute('insert into entries (contest, user, rank, score) values (?, ?, ?, ?)', row)
		db.commit()

@app.route('/display', methods=['POST'])
def display():
	return redirect(url_for('user', name1=request.form['id1'], name2=request.form['id2']))


if __name__ == '__main__':
	# init_db()
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
	#app.run(debug=True)