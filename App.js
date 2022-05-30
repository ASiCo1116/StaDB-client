import "./App.css";
import { io } from "socket.io-client";

const App = () => {
  const stream_query = `SELECT * FROM boston.train
                       TO TRAIN xgboost.gbtree
                       WITH
                           objective="reg:squarederror",
                           train.num_boost_round = 10
                       COLUMN crim, zn, indus, chas, nox, rm, age, dis, rad, tax, ptratio, b, lstat
                       LABEL medv
                       INTO sqlflow_models.my_xgb_regression_model;`;

  const img_query = `SELECT * FROM boston.train
                    TO EXPLAIN sqlflow_models.my_xgb_regression_model
                    WITH
                        summary.plot_type="dot",
                        summary.alpha=1,
                        summary.sort=True
                    USING TreeExplainer;`;

  const executeHandler = () => {
    //initialize socket connection
    const socket = io.connect("HOST"); //set up client host
    socket.on("connect", () => {
      socket.emit("execute", img_query);
      console.log("Connected !");
    });
    socket.on("log", (msg) => {
      console.log("From python " + String(msg));
    });
    socket.on("result", () => {
      socket.send("Disconnected !");
      socket.disconnect();
    });
  };
  return (
    <div className="App">
      <header className="App-header">
        <button onClick={executeHandler}> click me</button>
      </header>
    </div>
  );
};

export default App;
