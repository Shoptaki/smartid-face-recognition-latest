import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from './NavBar';

const LiveFaceRecognition = () => {
  const videoRef = useRef(null);
  const [username, setUsername] = useState({ user: '', liveliness: '' });
  const [webSocket, setWebSocket] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Ensure this is run after a user action
    const handleStartCamera = async () => {
      try {
        await startCamera();
        initializeWebSocket();
      } catch (error) {
        console.error('Error starting the camera:', error);
      }
    };

    // User action required to start camera
    document.getElementById('startCameraButton').addEventListener('click', handleStartCamera);

    return () => stopMedia();
  }, []);

  const startCamera = async () => {
    const constraints = {
      video: {
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      videoRef.current.srcObject = stream;
    } catch (error) {
      console.error('Error accessing the camera:', error);
      alert('Camera access error. Please check your Safari camera settings.');
    }
  };

  const initializeWebSocket = () => {
    const ws = new WebSocket('wss://192.168.1.68:8080/ws/detection');
    setWebSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.addEventListener('message', (message) => {
      const result = JSON.parse(message.data);

      if (result['match']) {
        const randomEmoji = '😎';
        const checkEmoji = '✅';
        setUsername({
          user: `${result['user_name']} ${randomEmoji}`,
          liveliness: result['liveness'] ? `Liveness Confirmed ${checkEmoji}` : 'Liveness Failed 😩',
        });
      } else {
        setUsername({ user: 'No match found 🤔', liveliness: 'Nothing to show 🫥' });
      }
    });
  };

  const stopMedia = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (webSocket) {
      webSocket.close();
    }
  };

  const retry = () => {
    setUsername({ user: '', liveliness: '' });
    startCamera(); // Restart the camera on retry
  };

  const captureFrame = () => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
      if (blob) {
        const reader = new FileReader();
        reader.onloadend = () => {
          if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            webSocket.send(reader.result); // Send image as binary data to WebSocket
          }
        };
        reader.readAsArrayBuffer(blob);
      }
    }, 'image/jpeg');
  };

  useEffect(() => {
    const interval = setInterval(() => {
      captureFrame();
    }, 1000); // Capture and send a frame every 1 second

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [webSocket]);

  return (
    <>
      <NavBar />
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="card shadow-lg rounded-lg p-6 w-96 items-center">
          <div className="rounded-full overflow-hidden border-4 border-white shadow-lg">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-80 h-80 object-cover"
            />
          </div>
          <div id="usernameDisplay" className='w-80'>
            <div className="text-white p-3 mt-4 rounded-md text-lg text-center font-bold border w-80">
              {username.user || 'Waiting for detection...'}
            </div>
            <div className="text-white p-3 mt-4 rounded-md text-lg text-center font-bold border min-w-80">
              {username.liveliness || 'Waiting for detection...'}
            </div>
            <button className="p-3 mt-4 btn bg-white text-black hover:text-white w-80" onClick={retry}>
              Retry 🔄
            </button>
            <button className="p-3 mt-4 btn bg-white text-black hover:text-white w-80" onClick={() => navigate('/')}>
              ⬅️ Back
            </button>
            <button id="startCameraButton" className="p-3 mt-4 btn bg-blue-500 text-white hover:text-black w-80">
              Start Camera 📸
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default LiveFaceRecognition;
