import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Layout from '../Templates/Layout';

// import { API_HOST } from '../consts';

var mqtt    = require('mqtt');
var options = {
    protocol: 'mqtts',
    clientId: 'b0908853'    
};
var client  = mqtt.connect('mqtt://test.mosquitto.org:8081', options);

// preciouschicken.com is the MQTT topic
client.subscribe('preciouschicken.com');


const HomePage = () => {
  const [message, setMessage] = useState('All output will be displayed here.');

  var note;
  client.on('message', function (topic, message) {
    note = message.toString();
    // Updates React state with message 
    setMessage(note);
    console.log(note);
    client.end();
    });

  return (
    <Layout>
      <div className="container fixed-bg-3 text-center">
        <h1 className="text-center display-4 pb-5 pt-5">YesNope</h1>
        <a href="/help">
          <Button variant="primary" size="lg" className="pp-button">
            Help
          </Button>
        </a>
        {/* <img className="page-icon" src="/logo.png" alt="Logo" /> */}
        <h1 className="text-center pb-4 pt-5">{message}</h1>
      </div>
      <br />

    </Layout>
  )};

export default HomePage;
