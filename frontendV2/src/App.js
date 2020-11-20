import React, { useState } from 'react';
import Webcam from "react-webcam";
import './App.css';
import Layout from './Templates/Layout';

const imagePaths = {
  "NOD": "/yes.png",
  "SHAKE": "/no.png",
  "IDLE": "/sleeping.png",
  "TILT": "/thinking.png",
  "RAISE": "/raised_hand.jpg",
  "NORAISE": "/transparent.png"
}

const WebcamComponent = () => <Webcam 
                        audio={false}
                        height={480}
                        width={854}
                        />;

var mqtt = require('mqtt');

// TEST SERVER (OLD): var client = mqtt.connect('mqtt://test.mosquitto.org:8081', { protocol: 'mqtts' });

// Add .env file with "REACT_APP_EC2_PASSWORD" in /frontendV2 to store 

var temp = "ws://";
var CONNECTION_STRING =  temp.concat(process.env.REACT_APP_EC2_PUBLIC_IP, ":9001")
var client = mqtt.connect(CONNECTION_STRING, {
  username:process.env.REACT_APP_EC2_USER,
  password:process.env.REACT_APP_EC2_PASSWORD
});
console.log("Connected");
client.subscribe('Group_12/LSTM/predict/Glen');
client.subscribe('Group_12/LSTM/predict/Sean');
client.subscribe('Group_12/LSTM/predict/Nicholas');

// EC2 SAMPLE: mosquitto_pub -t 'Group_12/LSTM/predict/Glen' -h '13.229.102.188' -u 'permasteo' -P 'cs3237g23' -m '{ "Prediction": "SHAKE", "Shown": "SHAKE", "batterylife": 10}'

function App() {
  var note;

  // TO ADD HAND GESTURES WHEN IMPLEMENTED
  client.on('message', function (topic, message) {
    note = JSON.parse(message.toString());
    console.log(note);
    console.log(topic);
    if (topic === 'Group_12/LSTM/predict/Glen') {
      setStatusGlen("Online");
      setHeadGlen(note['Shown']);
      setBatteryLifeA(note['batterylife']);
    }
    if (topic === 'Group_12/LSTM/predict/Sean') { 
      setStatusSean("Online");
      setHeadSean(note['Shown']);
      setBatteryLifeSean(note['batterylife']); 
    }
    if (topic === 'Group_12/LSTM/predict/Nicholas') { 
      setStatusNic("Online");
      setHeadNic(note['Shown']);
      setBatteryLifeNic(note['batterylife']); 
    }
  });

  const [statusGlen, setStatusGlen] = useState("Offline");
  const [headGlen, setHeadGlen] = useState("nothing heard");
  const [handGlen, setHandGlen] = useState("nothing heard");
  const [batteryLifeA, setBatteryLifeA] = useState(0);

  const [statusSean, setStatusSean] = useState("Offline");
  const [headSean, setHeadSean] = useState("nothing heard");
  const [handSean, setHandSean] = useState("nothing heard");
  const [batteryLifeSean, setBatteryLifeSean] = useState(0);

  const [statusNic, setStatusNic] = useState("Offline");
  const [headNic, setHeadNic] = useState("nothing heard");
  const [handNic, setHandNic] = useState("nothing heard");
  const [batteryLifeNic, setBatteryLifeNic] = useState(0);

  function selectColor(text) {
    return text === 'Online' ? {"color": "green"} : {"color": "red"};
  }

  function isOnline(text) {
    return text === "Online";
  }

  return (
    <Layout>
      <br />

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

      <div className="container-fluid text-center">
        <WebcamComponent/>
      </div>

      <br />

      <div className="container-fluid text-center vert-center-sm">
        <div className="inner-flex-top">

          <div className="flex-33 container fixed-bg-3 text-center">
          <h4 className="text-left" style={selectColor(statusGlen)}><b>{statusGlen} <span className={`${isOnline(statusGlen) ? "dot" : ""}`}>●</span></b></h4>
          <h1 className="text-center display-4 pb-3 pt-3"><b>Glen</b></h1>
            <div className="inner-flex-top">
              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Head:</h4>
                <img className="sm-icon" src={imagePaths[headGlen] ? imagePaths[headGlen] : "/sleeping.png" } alt="HeadGlen" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Hand:</h4>
                <img className="sm-icon" src={imagePaths[handGlen] ? imagePaths[handGlen] : "/transparent.png" } alt="HandGlen" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Battery:</h4>
                <h1 className="pb-2 pt-2 mb-mid">{batteryLifeA}%</h1>
              </div>  
            </div>
          </div>

          <div className="flex-33 container fixed-bg-3 text-center">
          <h4 className="text-left" style={selectColor(statusSean)}><b>{statusSean} <span className={`${isOnline(statusSean) ? "dot" : ""}`}>●</span></b></h4>
          <h1 className="text-center display-4 pb-3 pt-3"><b>Sean</b></h1>
            <div className="inner-flex-top">
              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Head:</h4>
                <img className="sm-icon" src={imagePaths[headSean] ? imagePaths[headSean] : "/sleeping.png" } alt="HeadSean" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Hand:</h4>
                <img className="sm-icon" src={imagePaths[handSean] ? imagePaths[handSean] : "/transparent.png" } alt="HandSean" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Battery:</h4>
                <h1 className="pb-2 pt-2 mb-mid">{batteryLifeSean}%</h1>
              </div>  
            </div>
          </div>

          <div className="flex-33 container fixed-bg-3 text-center">
          <h4 className="text-left" style={selectColor(statusNic)}><b>{statusNic} <span className={`${isOnline(statusNic) ? "dot" : ""}`}>●</span></b></h4>
          <h1 className="text-center display-4 pb-3 pt-3"><b>Nicholas</b></h1>
            <div className="inner-flex-top">
              <div className="flex-13 vert-center-m">
                <h4 className=" pb-3 pt-2">Head:</h4>
                <img className="sm-icon" src={imagePaths[headNic] ? imagePaths[headNic] : "/sleeping.png" } alt="HeadNic" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Hand:</h4>
                <img className="sm-icon" src={imagePaths[handNic] ? imagePaths[handNic] : "/transparent.png" } alt="HandNic" />
              </div>

              <div className="flex-13 vert-center-m">
                <h4 className="pb-3 pt-2">Battery:</h4>
                <h1 className="pb-2 pt-2 mb-mid">{batteryLifeNic}%</h1>
              </div>  
            </div>
          </div>

        </div>
      </div>

      <br />
      <br />

    </Layout>
  );
}

export default App;
