import './App.css'
import CatalogPage from '@pages/CatalogPage';
import VideoPage from '@pages/VideoPage';
import Navbar from '@components/Navbar';
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
                        <Route path="/" element={<CatalogPage />} />
                        <Route path="/watch/:id" element={<VideoPage />} />
                    </Routes>
                </div>
            </Router>
        </QueryClientProvider>
	)
}

export default App
