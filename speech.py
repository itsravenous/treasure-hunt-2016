#!/usr/bin/python3

# unix socket code started from https://pymotw.com/2/socket/uds.html

import os
import socket
from select import select
import json
import traceback
import subprocess

server_address = './speech.socket'
max_message = 1024

message_classes = ['game', 'cake', 'pie', 'pizza',]
pending_messages = { m_class: None for m_class in message_classes }

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(server_address)

def pendingmsg():
	(read, _, exception) = select([sock], [], [sock], 0)
	return (read or exception)

def readmsg():
	try:
		message = sock.recv(max_message)
		text = message.decode('UTF-8')
		data = json.loads(text)

		m_class = data['class']
		m_text = data['text']

		if m_class not in pending_messages:
			raise Exception('Unknown message class')
		pending_messages[m_class] = m_text
	except Exception:
		traceback.print_exc()

while True:
	readmsg()
	while pendingmsg():
		readmsg()

	for m_class in message_classes:
		text = pending_messages[m_class]
		if not text:
			continue
		pending_messages[m_class] = None

		# WARNING
		# audio power saving breaks TTS by eating the initial sound
		# using pulseaudio RTP sender disables audio power saving
		subprocess.call(['espeak', '-vf4', text])

