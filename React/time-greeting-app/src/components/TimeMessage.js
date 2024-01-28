// src/TimeMessage.js
import React, { useEffect, useState } from 'react';

const TimeMessage = ({ onGreetingChange }) => {
  useEffect(() => {
    const updateGreeting = () => {
      const currentHour = new Date().getHours();

      if (currentHour >= 0 && currentHour < 12) {
        onGreetingChange('Good morning', 'red');
      } else if (currentHour >= 12 && currentHour < 18) {
        onGreetingChange('Good afternoon', 'green');
      } else {
        onGreetingChange('Good evening', 'blue');
      }
    };

    updateGreeting(); // Initial call
    const intervalId = setInterval(updateGreeting, 60000); // Update every minute

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [onGreetingChange]);

  return null; // No need to render anything in this component
};

export default TimeMessage;
