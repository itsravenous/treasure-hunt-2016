# treasure-hunt-2016
A race against your opponent to collect the most time cubes!

Status:

 * mobile^W responsive frontend thanks to itsravenous
 * a web server serves templates/claim-cube.html
 * buttons for claim-cube.html now update a DB and return a score...

## codes.py
Generate secret codes using a cryptographically secure random number generator.

    $ ./codes.py > codes

Codes are used in urls: `http://landing.duckdns.org/2016/q/$CODE`.

## cubes/cubes.html
Create a copy of this HTML.  You can edit it to include your own codes.
It will render QR cubes for you to assemble
(or you can scan them from your screen for testing purposes).

## debug-webserver.sh
Entry point, runs web server on port 5000.
NOTE Flask debugger allows arbitrary code execution.
It will be protected with a PIN if Werkzeug is version 0.11 or later.
The simplest way to check is to run it with networking disabled
and check for a message showing the PIN :).

To reset the game, delete `db.json`.

## webserver.sh
Production entry point, web server on port 5000.
Debugger (and auto-reload) are disabled.

## portforward.sh
Forward requests from port 80.
For limitations & assumptions, please read script

## webserver.py
Web server code, using Python Flask

## static/
Static files, server as is.
(This matches the flask convention, although we don't use the default-provided /static/ URL).

## templates/
Flask template files.  I.e. to generate HTML for page URLs.

## LICENSE

cube/kjua.min.js is under separate license cube/kjua.LICENSE

First-party code is under LICENSE.GPL
