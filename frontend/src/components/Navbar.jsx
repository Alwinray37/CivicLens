import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import logo from '@assets/images/logo lrg.png';

import DarkModeIcon from './icons/DarkModeIcon';
import LightModeIcon from './icons/LightModeIcon';

const Navbar = () => {
    const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

    // on theme change, update data attributes on html element and localStorage
    useEffect(() => {
        const htmlEl = document.documentElement;
        htmlEl.setAttribute('data-bs-theme', theme);
        htmlEl.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    // toggle between light and dark themes, also updates localStorage and data attributes on html element
    const toggleTheme = () => {
        setTheme((currentTheme) => currentTheme === 'light' ? 'dark' : 'light');
    };

    return (
        <nav>
            <Link to="/" className="navbar-brand-link">
                <img src={logo} alt="CivicLens Logo" className="navbar-logo" />
                <span>CivicLens</span>
            </Link>

            <div className="navbar-actions d-flex align-items-center gap-3">
                <div className="navbar-links d-flex align-items-center gap-3">
                    <NavLink
                        to="/"
                        end
                        className={({ isActive }) => `navbar-page-link ${isActive ? 'active' : ''}`}
                    >
                        Home
                    </NavLink>
                    <NavLink
                        to="/about"
                        className={({ isActive }) => `navbar-page-link ${isActive ? 'active' : ''}`}
                    >
                        About
                    </NavLink>
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
