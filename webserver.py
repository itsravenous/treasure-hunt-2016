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
from werkzeug.exceptions import NotFound

def dbinit():
	# cubes = { code: claimed_by }
	cubes = {}
	with open('codes', 'r') as f:
		for line in f.readlines():
			code = line.strip()
			cubes[code] = None

	return {
		# State
		'cubes': cubes,

		# Convenient summaries to return to frontend
		#
		# (the last entry is not a requirement for Tom to implement,
		#  I just remembered the frontend didn't have any way to tell
		#  even if it wanted)

		'score': {
			'cake': 0,
			'pie': 0,
			'pizza': 0,
		},
		'game_over': False,
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


# This works, not sure it's the absolute best
class APIError(Exception):
	pass

class CubeAlreadyClaimed(APIError):
	code = 1
	description = 'This cube has already been claimed.'

class NoSuchPlayer(APIError):
	code = 2
	description = 'Player is neither CAKE, PIE, nor PIZZA.'

class NoSuchCube(APIError):
	code = 3
	description = 'Cube not found.'

@app.errorhandler(APIError)
def apierror(e):
	j = jsonify({
		'error': e.code,
		'description': e.description
	})
	j.status_code = 400
	return j


@app.route('/2016/treasure/claim-cube/<path:cube_code>')
def cube_claim(cube_code):
	# TODO: error response should (normally) be _here_,
	# in the case where cube is already claimed!

	d = db.read()
	cubes = d['cubes']
	if cube_code not in cubes:
		raise NotFound("Cube not recognized.")

	return render_template('claim-cube.html', cube_code=cube_code)


@app.route('/2016/treasure/api/score')
def score():
	d = db.read()
	return jsonify({
		'score': d['score'],
		'game_over': d['game_over'],
	})

@app.route('/2016/treasure/api/claim-cube/<path:cube_code>', methods=['POST'])
def cube_claim_for(cube_code):
	player = request.args.get('claim-for', None)

	with db.transact() as transact:
		d = db.read()

		# Update cubes with claim
		cubes = d['cubes']
		try:
			already_claimed = cubes[cube_code]
		except KeyError:
			raise NoSuchCube()
		if already_claimed:
			raise CubeAlreadyClaimed()
		cubes[cube_code] = player

		# Update count of cubes claimed
		score = d['score']
		if player not in score:
			raise NoSuchPlayer()
		score[player] += 1

		# Check if all cubes have been claimed
		if sum(score.values()) == len(cubes):
			d['game_over'] = True

		transact.write(d)

	return jsonify({
		'score': score,
		'game_over': d['game_over'],
	})


# Catch-all: serve static file
@app.route('/2016/treasure/<path:path>')
def static_file(path):
	return send_from_directory('static', path)

if __name__ == "__main__":
	app.run()
