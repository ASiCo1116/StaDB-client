from socket import socket
from flask import Flask, jsonify, redirect, request, abort
import json
from flask_cors import CORS
from client import MyClient
from flask_socketio import SocketIO, send, emit


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

client = MyClient(server_url='IP_TO_SQLFLOW_SERVER')

@app.route('/')
def index():
    return 'hello man'

@socketio.on('disconnect')
def handleDisconnection():
    print('Disconnected !')

@socketio.on('execute')
def handleCmd(msg):
    print('Connected !')
    result = client.execute(msg, emit)
    df = result._messages[0][0].to_dataframe()
    head = df.columns.tolist()
    table = df.to_json(orient="records")
    emit('result', jsonify({'head': head, 'table': table}))

if __name__ == '__main__':
    app.debug = True
    socketio.run(app) # set host and port if needed