import React from 'react';
// import './App.css';

function App() {
  const yourName = 'YOURNAME';
  const currentYear = new Date().getFullYear();

  return (
    <div className="App">
      <p>Created by {yourName}.</p>
      <p>Copyright {currentYear}.</p>
    </div>
  );
}

export default App;
