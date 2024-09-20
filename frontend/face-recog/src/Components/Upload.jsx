import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import NavBar from './NavBar'; 
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [userName, setUserName] = useState('');
  const [cameraOn, setCameraOn] = useState(true);
  const [showToast, setShowToast] = useState(false); 
  const [captureClicked, setCaptureClicked] = useState(false); 

 const navigate = useNavigate();
  const capture = useCallback(() => {
    const image = webcamRef.current.getScreenshot();
    setImageSrc(image);
    setCameraOn(false);
    setCaptureClicked(true); 
  }, [webcamRef]);

  
  const retry = () => {
    setImageSrc(null); 
    setCameraOn(true); 
    setCaptureClicked(false); 
  };

  
  const handleSubmit = async () => {
    if (!captureClicked) {
      
      return;
    }

    const blob = await fetch(imageSrc).then((res) => res.blob());

    const formData = new FormData();
    formData.append('file', blob, 'image.jpg');
    formData.append('user_name', userName);

    try {
      const response = await axios.post('https://192.168.1.68:8080/capture', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(response.data);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    } catch (error) {
      console.error('Error uploading image', error);
    }
  };

  return (
    <>
      <NavBar />
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="card shadow-lg rounded-lg p-6 w-96">
          <div>
            <div className="rounded-full overflow-auto border-4 border-white shadow-lg mb-4">
              {cameraOn ? (
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="p-auto m-auto w-74 h-80 object-cover"
                />
              ) : (
                <img
                  src={imageSrc}
                  alt="Captured"
                  className="w-74 h-80 object-cover"
                />
              )}
            </div>

            <div className="flex justify-center flex-col items-center w-80 space-y-4">
              <div className="relative w-full">
                <input
                  type="text"
                  placeholder="User Name"
                  className="input bg-black border-white text-white w-full focus:outline-none focus:ring-2 focus:ring-white"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  required
                />
                {!cameraOn && (
                  <button
                    type="button"
                    onClick={retry}
                    className="absolute right-2 top-2"
                  >
                    {/* Retry Icon */}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                      className="w-6 h-6 text-white mb-2 mr-2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M4 4v5h.582M4.582 9C6.708 5.856 10.236 4 14 4c5.523 0 10 4.477 10 10s-4.477 10-10 10S4 19.523 4 14"
                      />
                    </svg>
                  </button>
                )}
              </div>

              <div className="flex justify-center  flex-col w-80">
                {cameraOn ? (
                  <button
                    type="button"
                    className="btn bg-white text-black hover:text-black w-80"
                    onClick={capture}
                  >
                    Capture 📸
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn bg-white text-black hover:text-black w-80"
                    onClick={handleSubmit}
                    disabled={!captureClicked}
                  >
                    Send 🚀
                  </button>
                )}
                <button className=" mt-4 btn bg-white text-black hover:text-white w-80" onClick={() => navigate('/')}>
              ⬅️ Back
            </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showToast && (
        <div className="toast toast-bottom toast-end">
          <div className="alert bg-white text-black">
            <div>
              <span>Image uploaded successfully!</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Upload;
