import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import VideoListPage from './components/VideoListPage'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  

	return (
		<Router>
			<div className="main">
				<Navbar/>
				
				<Routes>
					<Route path="/" element={<VideoListPage />} />
				</Routes>
			</div>
		</Router>
		
	)
}

export default App
