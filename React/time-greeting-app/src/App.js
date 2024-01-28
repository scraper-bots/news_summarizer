// src/App.js
import React, { useState } from 'react';
import './styles.css';
import Greeting from './components/Greeting';
import TimeMessage from './components/TimeMessage';

const App = () => {
  const [greeting, setGreeting] = useState('');
  const [color, setColor] = useState('');

  const handleGreetingChange = (newGreeting, newColor) => {
    setGreeting(newGreeting);
    setColor(newColor);
  };

  return (
    <div>
      <TimeMessage onGreetingChange={handleGreetingChange} />
      <Greeting greeting={greeting} color={color} />
    </div>
  );
};

export default App;
