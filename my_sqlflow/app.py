import os
from flask import Flask, jsonify
from client import MyClient
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

sqlflow_server = os.environ.get("SQLFLOW_SERVER") or "127.0.0.1:50051"
client = MyClient(server_url=sqlflow_server)

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
    socketio.run(app, host="0.0.0.0") # set host and port if needed