import React, { useState, Fragment } from 'react';
import './App.css';
import Layout from './Templates/Layout';

var mqtt    = require('mqtt');
var client  = mqtt.connect('mqtt://test.mosquitto.org:8081', {protocol:'mqtts'});
client.subscribe('Group_12/LSTM/predict');
// mosquitto_pub -t 'myTest' -h 'test.mosquitto.org' -m 'Your message heresdsds!'

function App() {
  var note;
  
  client.on('message', function (topic, message) {
    // console.log("message:", message);
    note = JSON.parse(message.toString());
    console.log(note)
    
    // Updates React state with message 
    setPredicted(note['Prediction']);
    setShown(note['Shown']);
    
    // client.end();
    });

  // Sets default React state 
  const [predicted, setPredicted] = useState("nothing heard");
  const [shown, setShown] = useState("nothing heard");

  return (
    <Layout>        
      <div className="container fixed-bg-3 text-center">
      
        <h1 className="text-center display-4 pb-5 pt-5">Sample Outputs</h1>
        
        <div className="container-fluid text-center vert-center-sm">
          <div className="inner-flex-top">
            <div className="main-30">
              <img className="md-icon" src="/yes.png" alt="yes" />
              <h4 className="text-center pb-5 pt-5">User nods head: Yes</h4>
        
            </div>
            <div className="aside-30 vert-center-m">
              <img className="md-icon" src="/no.png" alt="no" />
              <h4 className="text-center pb-5 pt-5">User shakes head: No</h4>
        
            </div>
          </div>
        </div>
      
      </div>
      <br />      




      <div className="container fixed-bg-3 text-center">
        <h1 className="text-center display-4 pb-5 pt-5">YesNope</h1>
        {/* <img className="page-icon" src="/logo.png" alt="Logo" /> */}
        <h1 className="text-center pb-4 pt-5">Predicted: {predicted}</h1>
        <h1 className="text-center pb-4 pt-5">Shown: {shown}</h1>
      </div>

      <br />
      <br />

    </Layout>
  );
}

export default App;
