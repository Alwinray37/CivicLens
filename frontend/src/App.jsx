import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import VideoListPage from './components/VideoListPage'
import VideoPage from './components/VideoPage'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient();

function App() {
  

	return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <div className="main">
                    <Navbar/>
                    
                    <Routes>
                        <Route path="/" element={<VideoListPage />} />
                        <Route path="/video/:id" element={<VideoPage />} />
                    </Routes>
                </div>
            </Router>
        </QueryClientProvider>
		
	)
}

export default App
