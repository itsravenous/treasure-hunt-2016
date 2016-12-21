#!/usr/bin/python3

import os
import json

# BSD file locks.  See
# "On the Brokenness of File Locking"
# http://0pointer.de/blog/projects/locking
from fcntl import flock, LOCK_EX

# Doubtless I should have used sqlite
# I just forget how to describe SQL with serializable transactions.
class DB:
	"""Database with serializable transactions."""
	def __init__(self, filename, init):
		self.__filename = filename
		with self.transact() as transact:
			if not os.path.isfile(filename):
				if callable(init):
					init = init()
				transact.write(init)

	def read(self):
		"""Read the database."""
		with open(self.__filename, 'r') as f:
			return json.load(f)

	def transact(self):
		"""Open an atomic write transaction"""
		return DBTransaction(self.__filename)

class DBTransaction:
	def __init__(self, filename):
		self.__filename = filename

		self.__flocked = open(filename+'.lock', 'w');
		flock(self.__flocked.fileno(), LOCK_EX)

	def write(self, data):
		newfilename = self.__filename + '.new'
		with open(newfilename, 'w') as f:
			json.dump(data, f, sort_keys=True, indent=4)
			# f.flush()
			# os.fsync(f.fileno())
		os.rename(newfilename, self.__filename)

	def close(self):
		self.__flocked.close()
		self.__filename = None

	def __enter__(self):
		return self
	def __exit__(self, type, value, tb):
		self.close()


from flask import (
	Flask,
	request,
	redirect,
	abort,
	render_template,
	send_from_directory,
	jsonify
)
from werkzeug.exceptions import NotFound, BadRequest

def dbinit():
	# cubes = { code: claimed_by }
	cubes = {}
	with open('codes', 'r') as f:
		for line in f.readlines():
			code = line.strip()
			cubes[code] = None

	return {
		'cubes': cubes,
		'score': { 'cake': 0, 'pie': 0 }
	}

# And just now I notice this db is initialized at web server start,
# and the db variable persists.  I assume this is expected,
# the alternative seems just too much magic.
#
# I might have gotten away without storing a file altogether!
# (I don't know what sort of locking is required,
#  although surely multiprocess.Lock would be safe).

db = DB('db.json', init=dbinit)
app = Flask(__name__)


# URL pattern of re-usable qrcubes
@app.route('/2016/q/<path:path>')
def q(path):
	return redirect('/2016/treasure/claim-cube/' + path)

# FIXME
# Error reporting.
# There should be some feedback for "Cube already claimed".
# On the other hand, NoSuchCube can occur both
# for browser requests and for AJAX requests.
# Sounds like it should be easy to resolve and I was just a bit confused.

# Cubes are URLs
class NoSuchCube(NotFound):
	description = 'Error: cube not found.'

class NoSuchPlayer(BadRequest):
	description = 'Error: player is neither CAKE nor PIE.'


@app.route('/2016/treasure/claim-cube/<path:cube_code>')
def cube_claim(cube_code):
	# TODO: error response _here_ when cube is already claimed!

	d = db.read()
	cubes = d['cubes']
	if cube_code not in cubes:
		raise NoSuchCube()

	return render_template('claim-cube.html', cube_code=cube_code)

@app.route('/2016/treasure/claim-cube/<path:cube_code>', methods=['POST'])
def cube_claim_for(cube_code):
	player = request.args.get('claim-for', '')

	with db.transact() as transact:
		d = db.read()
		cubes = d['cubes']

		try:
			already_claimed = cubes[cube_code]
		except KeyError:
			raise NoSuchCube()
		if already_claimed:
			abort(400) # TODO
		cubes[cube_code] = player

		score = d['score']
		if player not in score:
			abort(400) # TODO
		score[player] += 1

		transact.write(d)

	return jsonify(score)
		

# Catch-all: serve static file
@app.route('/2016/treasure/<path:path>')
def static_file(path):
	return send_from_directory('static', path)

if __name__ == "__main__":
	app.run()
