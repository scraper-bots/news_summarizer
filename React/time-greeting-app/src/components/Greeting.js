// src/Greeting.js
import React from 'react';

const Greeting = ({ greeting, color }) => {
  return (
    <h1 style={{ color }} className="heading">
      {greeting}
    </h1>
  );
};

export default Greeting;
