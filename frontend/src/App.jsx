import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import CatalogPage from './components/CatalogPage'
import VideoPage from './components/VideoPage'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  

	return (
		<Router>
			<div className="main">
				<Navbar/>
				
				<Routes>
					<Route path="/" element={<CatalogPage />} />
                    <Route path="/watch/:id" element={<VideoPage />} />
				</Routes>
			</div>
		</Router>
		
	)
}

export default App
