# StaDB-client

[StaDB-client](https://github.com/ASiCo1116/StaDB-client) StaDB client for Python, modified from [SQLFlow](https://github.com/sql-machine-learning/sqlflow).


## Tutorial

In my_sqlflow/app.py, please set up ip or sqlflow server.

```python
...
client = MyClient(server_url='IP_TO_SQLFLOW_SERVER') # set up ip or sqlflow server
...

if __name__ == '__main__':
    app.debug = True
    socketio.run(app) # set up host and port if needed
```

In my_sqlflow/client.py, please set up ip of mysql.

```python
...
os.environ['SQLFLOW_DATASOURCE'] = "mysql://root:root@tcp(IP_TO_MYSQL)/?maxAllowedPacket=0" # set up ip of mysql
...
```

In App.js, please set up client host.

```javascript
...
  const executeHandler = () => {
    //initialize socket connection
    const socket = io.connect("HOST"); //set up client host
   ...
  };
...

```


