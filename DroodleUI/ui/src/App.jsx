// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vitejs.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

/////////////////////////////////////////////////////////////////////////////////////

// import React from 'react';
// import ChatWindow from './components/ChatWindow';
// import ImageDisplay from './components/ImageDisplay';
// import './styles/App.css';

// function App() {
//   return (
//     <div className="app-container">
//       <div className="left-pane">
//         <ChatWindow />
//       </div>
//       <div className="right-pane">
//         <ImageDisplay />
//       </div>
//     </div>
//   );
// }

// export default App;

/////////////////////////////////////////////////////////////////////////////////////

import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ImageDisplay from './components/ImageDisplay';
import './styles/App.css';

function App() {
  // State to track the current image index
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  return (
    <div className="app-container">
      <div className="left-pane">
        {/* Pass currentImageIndex to ChatWindow */}
        <ChatWindow currentImageIndex={currentImageIndex} />
      </div>
      <div className="right-pane">
        {/* Pass currentImageIndex and setCurrentImageIndex to ImageDisplay */}
        <ImageDisplay 
          currentImageIndex={currentImageIndex} 
          setCurrentImageIndex={setCurrentImageIndex} 
        />
      </div>
    </div>
  );
}

export default App;