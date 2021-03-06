#!/usr/bin/python3
# coding=UTF-8
#
# (I always forget, pound signs are not in ASCII :)

# But, what the Flask quickstart didn't point out, is that the `flask` command
# installed from OS packages is likely python2.  But I was writing for python3.
# Sticking with `flask` for now, because I don't know if `flask-3` is what it's
# called on Tom's computer.
#
# I only noticed because it caused a decoding error.
# Tell python2 to work more like python3.
from __future__ import unicode_literals

import os
import socket
from select import select
import json
import traceback

def speak_update(klass, text):
	try:
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		sock.setblocking(0)
		sock.connect('speech.socket')
		(_, write, _) = select([], [sock], [], 0)
		if not write:
			return
		msg = { 'class': klass, 'text': text }
		sock.send(json.dumps(msg).encode('UTF-8'))
	except Exception:
		traceback.print_exc()

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


player_names = {
	'cake': 'C.A.K.E.',
	'pie': 'P.I.E.',
	'pizza': 'P.I.Z.Z.A.',
}

def dbinit():
	# cubes = { code: claimed_by }
	cubes = {}
	with open('codes', 'r') as f:
		for line in f.readlines():
			code = line.strip()
			cubes[code] = None

	return {
		# Canonical state
		'cubes': cubes,

		# Convenient summaries to return to frontend
		#
		# (the last entry is not a requirement for Tom to implement,
		#  I just remembered the frontend didn't have any way to tell
		#  even if it wanted)
		#
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
	description = 'Cube not recognized.'

@app.errorhandler(APIError)
def apierror(e):
	j = jsonify({
		'error': e.code,
		'description': e.description
	})
	j.status_code = 400
	return j


# URL pattern of re-usable qrcubes
@app.route('/2016/q/<path:path>')
def q(path):
	return redirect('/2016/treasure/claim-cube/' + path)


@app.route('/2016/treasure/welcome/<path:player>/')
def welcome(player):
	return render_template('welcome.html', player_name=player_names[player])


@app.route('/2016/treasure/claim-cube/<path:cube_code>')
def cube_claim(cube_code):
	# TODO: error response should (normally) be _here_,
	# in the case where cube is already claimed!

	d = db.read()
	cubes = d['cubes']
	if cube_code not in cubes:
		raise NotFound('Cube not recognized.')

	claimed_by = cubes[cube_code]

	return render_template('claim-cube.html', cube_code=cube_code, claimed_by=claimed_by)

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

		# Have all cubes have been claimed?
		if sum(score.values()) == len(cubes):
			d['game_over'] = True

		transact.write(d)

	def speak_update_player(player):
		player_score = score[player]
		speak_update(player, '{0} has {1} {2}.'.format(
		                     player.capitalize(),
		                     player_score,
		                     'cube' if player_score == 1 else 'cubes'))

	if d['game_over']:
		speak_update('game',
		             'All cubes have been recovered!  Your performance assessments are now ready.  Please make sure to read them carefully.')
		for each_player in d['score'].keys():
			speak_update_player(each_player)
	else:
		speak_update_player(player)

	return jsonify({
		'score': score,
		'game_over': d['game_over'],
	})


@app.route('/2016/treasure/api/score')
def score():
	d = db.read()
	return jsonify({
		'score': d['score'],
		'game_over': d['game_over'],
	})


prizes = [
	'Collect £200!',
	'Were you sleepy, or do you just fold easily?',
	'You are a potato!',
]

def rank_players_by_score(d):
	scores = d['score'].items()
	sorted_scores = sorted(scores, reverse=True, key=lambda item: item[1])
	ranking = [player for (player, score) in sorted_scores]
	return ranking

@app.route('/2016/treasure/assessment/<path:assessed_player>')
def assessment(assessed_player):
	d = db.read()
	if not d['game_over']:
		raise BadRequest('There are still more cubes to collect')

	ranking = rank_players_by_score(d)
	ranked_players = [
		{
			'name': player_names[player],
			'score': d['score'][player],
		}
		for player in ranking
	]
	
	try:
		rank = ranking.index(assessed_player)
	except ValueError:
		raise BadRequest('Player not found')
	
	assessment = prizes[rank]
	data = {
		'ranked_players': ranked_players,
		'player_name': player_names[assessed_player],
		'player_assessment': assessment
	}
	return render_template('assessment.html', **data)


# Catch-all: serve static file
@app.route('/2016/treasure/<path:path>')
def static_file(path):
	return send_from_directory('static', path)

if __name__ == "__main__":
	app.run()
