import React, { useState } from 'react';
import './App.css';
import Layout from './Templates/Layout';

var mqtt = require('mqtt');
var client = mqtt.connect('mqtt://test.mosquitto.org:8081', { protocol: 'mqtts' });
client.subscribe('Group_12/LSTM/predict');
// SAMPLE: mosquitto_pub -t 'Group_12/LSTM/predict' -h 'test.mosquitto.org' -m '{ "Prediction": "SHAKE", "Shown": "SHAKE", "batterylife": 10}'

function App() {
  var note;

  client.on('message', function (topic, message) {
    // console.log("message:", message);
    note = JSON.parse(message.toString());
    console.log(note)

    // Updates React state with message 
    setPredicted(note['Prediction']);
    setShown(note['Shown']);
    setBatteryLife(note['batterylife']);

    // client.end();
  });

  // Sets default React state 
  const [predicted, setPredicted] = useState("nothing heard");
  const [shown, setShown] = useState("nothing heard");
  const [batteryLife, setBatteryLife] = useState(0);

  return (
    <Layout>
      <div className="container fixed-bg-3 text-center">

        <h1 className="text-center display-4 pb-5 pt-5">Sample Outputs</h1>

        <div className="container-fluid text-center vert-center-sm">
          <div className="inner-flex-top">
            <div className="main-30">
              <img className="md-icon" src="/yes.png" alt="yes" />
              <h4 className="text-center pb-5 pt-5">User nods head</h4>

            </div>
            <div className="aside-30 vert-center-m">
              <img className="md-icon" src="/no.png" alt="no" />
              <h4 className="text-center pb-5 pt-5">User shakes head</h4>

            </div>
            <div className="aside-30 vert-center-m">
              <img className="md-icon" src="/sleeping.png" alt="idle" />
              <h4 className="text-center pb-5 pt-5">User is Idle</h4>

            </div>
          </div>
        </div>

      </div>
      <br />

      <div className="container fixed-bg-3 text-center">
        {/* <h1 className="text-center display-4 pb-3 pt-3"><b>YesNope</b></h1> */}
        {/* <img className="page-icon" src="/logo.png" alt="Logo" /> */}
        <h1 className="text-center pb-2 pt-2">Predicted: {predicted}</h1>
        <h1 className="text-center pb-2 pt-2">Shown: {shown}</h1>
        <h1 className="text-center pb-2 pt-2">Battery Life: {batteryLife}</h1>
      </div>
      <br />
      <br />

    </Layout>
  );
}

export default App;
