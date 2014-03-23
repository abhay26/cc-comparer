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
	# loadContestData("COOK42")
	# loadContestData("JAN14")
	# db = get_db()
	# t = ('abhay26',)
	# cur = db.execute("SELECT * FROM entries WHERE user=?",t)	
	# entries = cur.fetchall()
	# for row in entries:
	# 	print (row['contest'],row['user'], row['rank'], row['score'])
	return render_template('index.html')

@app.route('/users/<name1>/<name2>')
@app.route('/users/<name1>/')
def user(name1=None,name2=None):
	
	data1 = getData(name1)
	db = get_db()
	# db.execute('insert into entries (contest, user, rank, score) values (?, ?, ?, ?)', ['dgdsgs',data1['id'], data1['ranks']['short_country'],'33431'])
	# db.commit()
	# db.execute('insert into entries (contest, user, rank, score) values (?, ?, ?, ?)', ['dgdsgs',data1['id'], data1['ranks']['short_country'],'33431'])
	# db.commit()
	# cur = db.execute('select * from entries')
	# entries = cur.fetchall()
	# for entry in entries:
	# 	print (entry['contest'], entry['user'], entry['rank'], entry['score'])
	# flash('User inserted in DB')
	if 'error' in data1:
		return render_template('user.html',error="Either invalid username or some problem with the site!")
	if name2:
		data2 = getData(name2)
		if 'error' in data2:
			return render_template('user.html',error="Either invalid username or some problem with the site!")
		lis = [val for val in data1['contests'] if val in data2['contests']]
		contestData = getAllRanksMulti(lis, name1, name2)
		return render_template('users.html', data1=data1,data2=data2, contestData=contestData, union=lis)
	else:
		contestData = getAllRanks(data1['contests'], name1)
		return render_template('user.html',data1=data1,contestData=contestData)



@app.route('/display', methods=['POST'])
def display():
	if request.form['id1'] == '':
	 	return render_template('user.html',error="Enter first ID!")

	#return user(request.form['id1'],request.form['id2'])
	return redirect(url_for('user', name1=request.form['id1'], name2=request.form['id2']))


	
if __name__ == '__main__':
	# init_db()
	app.run(debug=True)