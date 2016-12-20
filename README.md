# treasure-hunt-2016
A race against your opponent to collect the most time cubes!

Status:
 * mobile^W responsive frontend thanks to itsravenous
 * a web server serves templates/claim-cube.html
 * buttons for claim-cube.html now update a DB and return a score
 * UNUSED: templates/index.html (player chooses to be cake or pie)

## webserver.sh
Entry point, web server on port 5000

## debug-webserver.sh
The same flask webserver, but with the debugger enabled.
NOTE Flask debugger allows arbitrary code execution.
It will be protected with a PIN if Werkzeug is version 0.11 or later.
The simplest way to check is to run it with networking disabled
and check for a message showing the PIN :).

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
