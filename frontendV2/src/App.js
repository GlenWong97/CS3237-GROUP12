import React, { useState, Fragment } from 'react';
import './App.css';

var mqtt    = require('mqtt');
var client  = mqtt.connect('mqtt://test.mosquitto.org:8081', {protocol:'mqtts'});
client.subscribe('myTest');
// mosquitto_pub -t 'myTest' -h 'test.mosquitto.org' -m 'Your message heresdsds!'

function App() {
  var note;
  
  client.on('message', function (topic, message) {
    note = message.toString();
    // Updates React state with message 
    setMesg(note);
    console.log(note);
    // client.end();
    });

  // Sets default React state 
  const [mesg, setMesg] = useState("nothing heard");

  return (
    <div className="App">
    <header className="App-header">
    <h1>A taste of MQTT in React</h1>
    <p>The message is: {mesg}</p>
		<p>
		<a href="https://www.preciouschicken.com/blog/posts/a-taste-of-mqtt-in-react/"    
		style={{
			color: 'white'
		}}>preciouschicken.com/blog/posts/a-taste-of-mqtt-in-react/</a>
		</p>
		</header>
		</div>
  );
}

export default App;
