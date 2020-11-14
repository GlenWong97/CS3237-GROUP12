import React, { useState } from 'react';
import './App.css';
import Layout from './Templates/Layout';

const imagePaths = {
  "NOD": "/yes.png",
  "SHAKE": "/no.png",
  "IDLE": "/sleeping.png"
}

var mqtt = require('mqtt');
var client = mqtt.connect('mqtt://test.mosquitto.org:8081', { protocol: 'mqtts' });
client.subscribe('Group_12/LSTM/predict');
// SAMPLE: mosquitto_pub -t 'Group_12/LSTM/predict' -h 'test.mosquitto.org' -m '{ "Prediction": "SHAKE", "Shown": "SHAKE", "batterylife": 10}'

function App() {
  var note;

  client.on('message', function (topic, message) {
    note = JSON.parse(message.toString());
    console.log(note)

    if (topic === 'Group_12/LSTM/predict') {
      setPredictedA(note['Prediction']);
      setShownA(note['Shown']);
      setBatteryLifeA(note['batterylife']);
     } else if (topic === 'Group_12/LSTM/predictB') { // *** CHANGE TOPIC FOR USER B HERE ***
      setPredictedB(note['Prediction']);
      setShownB(note['Shown']);
      setBatteryLifeB(note['batterylife']); 
    }
  });

  const [predictedA, setPredictedA] = useState("nothing heard");
  const [shownA, setShownA] = useState("nothing heard");
  const [batteryLifeA, setBatteryLifeA] = useState(0);

  const [predictedB, setPredictedB] = useState("nothing heard");
  const [shownB, setShownB] = useState("nothing heard");
  const [batteryLifeB, setBatteryLifeB] = useState(0);

  return (
    <Layout>
      <div className="container fixed-bg-3 text-center">

        <h1 className="text-center display-4 pb-5 pt-5">Sample Outputs</h1>

        <div className="container-fluid text-center vert-center-sm">
          <div className="inner-flex-top">
            <div className="flex-30">
              <img className="md-icon" src="/yes.png" alt="yes" />
              <h4 className="text-center pb-5 pt-5">User nods head</h4>

            </div>
            <div className="flex-30 vert-center-m">
              <img className="md-icon" src="/no.png" alt="no" />
              <h4 className="text-center pb-5 pt-5">User shakes head</h4>

            </div>
            <div className="flex-30 vert-center-m">
              <img className="md-icon" src="/sleeping.png" alt="idle" />
              <h4 className="text-center pb-5 pt-5">User is Idle</h4>

            </div>
          </div>
        </div>

      </div>
      <br />

      <div className="container fixed-bg-3 text-center">
        <h1 className="text-center display-4 pb-3 pt-3"><b>User A</b></h1>

        <div className="inner-flex-top">
          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Predicted:</h4>
            <img className="sm-icon" src={imagePaths[predictedA] ? imagePaths[predictedA] : "/sleeping.png" } alt="predict" />
          </div>

          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Shown:</h4>
            <img className="sm-icon" src={imagePaths[shownA] ? imagePaths[shownA] : "/sleeping.png" } alt="Shown" />
          </div>

          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Battery:</h4>
            <h1 className="text-center pb-2 pt-2 mb-mid">{batteryLifeA}%</h1>
          </div>
          
          
        </div>
      </div>
      <br />

      <div className="container fixed-bg-3 text-center">
        <h1 className="text-center display-4 pb-3 pt-3"><b>User B</b></h1>

        <div className="inner-flex-top">
          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Predicted:</h4>
            <img className="sm-icon" src={imagePaths[predictedB] ? imagePaths[predictedB] : "/sleeping.png" } alt="predict" />
          </div>

          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Shown:</h4>
            <img className="sm-icon" src={imagePaths[shownB] ? imagePaths[shownB] : "/sleeping.png" } alt="Shown" />
          </div>

          <div className="flex-13 vert-center-m">
            <h4 className="text-center pb-2 pt-2">Battery:</h4>
            <h1 className="text-center pb-2 pt-2 mb-mid">{batteryLifeB}%</h1>
          </div>
          
          
        </div>
      </div>


      <br />
      <br />

    </Layout>
  );
}

export default App;
