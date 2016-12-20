#!/usr/bin/python3

from flask import Flask, request, redirect, render_template, send_from_directory
app = Flask(__name__)

# URLs of the re-usable qrcubes
@app.route('/2016/q/<path:path>')
def q(path):
    return redirect('/2016/treasure/claim-cube/' + path)

@app.route('/2016/treasure/claim-cube/<path:path>')
def cube_claim(path):
    return render_template('claim-cube.html', cube_code=path)

@app.route('/2016/treasure/claim-cube/<path:path>', methods=['POST'])
def cube_claim_for(path):
    player = request.args.get('claim-for', '')
    return player


# Catch-all: serve static file
@app.route('/2016/treasure/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run()
