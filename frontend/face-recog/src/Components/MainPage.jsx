import React from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from './NavBar';

const MainPage = () => {
  const navigate = useNavigate();

  return (
    <>
    <NavBar/>
    <div className="flex flex-col items-center justify-center h-screen">
        {/* <div className ='flex justify-center'>
                <h1 className="text-white text-4xl font-bold">Face ID</h1>
            </div> */}
        <div className='p-4 rounded-lg mb-4 flex flex-col w-1/4'>
            <div className ='flex flex-col justify-center p-10'>
                <button className="btn bg-white text-black hover:text-white mb-4" onClick={() => navigate('/upload')}>Upload Photo ⬆️</button>
                <button className="btn bg-white text-black hover:text-white" onClick={() => navigate('/detection')}>Go to Detection 👀</button>
            </div>
        </div>
    </div>
    </>
  );
};

export default MainPage;
