import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import logo from '@assets/images/logo lrg.png';

import DarkModeIcon from './icons/DarkModeIcon';
import LightModeIcon from './icons/LightModeIcon';

const Navbar = () => {
    const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

    useEffect(() => {
        const htmlEl = document.documentElement;
        htmlEl.setAttribute('data-bs-theme', theme);
        htmlEl.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme((currentTheme) => currentTheme === 'light' ? 'dark' : 'light');
    };

    return (
        <nav>
            <div className="d-flex gap-3 logo align-items-center">
                <div>
                    <Link to="/" className="navbar-brand-link">
                        <img src={logo} alt="CivicLens Logo" className="navbar-logo" />
                        <span>CivicLens</span>
                    </Link>
                </div>
                {theme === 'light' ? (
                <button 
                    title="Toggle theme"
                    onClick={toggleTheme}
                    className="btn theme-toggle-btn border-0 p-1 d-flex align-items-center justify-content-center"
                >
                    <DarkModeIcon />
                </button>
                ) : (
                <button 
                    title="Toggle theme"
                    onClick={toggleTheme}
                    className="btn theme-toggle-btn border-0 p-1 d-flex align-items-center justify-content-center"
                >
                    <LightModeIcon />
                </button>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
