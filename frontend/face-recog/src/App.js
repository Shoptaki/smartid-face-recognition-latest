import React from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import MainPage from './Components/MainPage';
import LiveFaceRecognition from './Components/LiveFaceRecognition';
import Upload from './Components/Upload';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/detection" element={<LiveFaceRecognition />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Router>
  );
};

export default App;
