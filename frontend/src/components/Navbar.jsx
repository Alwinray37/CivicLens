import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import DarkModeIcon from './icons/DarkModeIcon';
import LightModeIcon from './icons/LightModeIcon';

const Navbar = () => {
    const [theme, setTheme] = useState('light');

    const toggleTheme = () => {
        const htmlEl = document.getElementsByTagName('html')[0];
        const newTheme = theme === "light" ? "dark" : "light";
        htmlEl.setAttribute("data-bs-theme", newTheme);
        setTheme(newTheme);
    }

    return (
        <nav className="" >
            <div className="d-flex gap-3 logo align-items-center">
                <div >
                    <Link to="/" style={{color: "whitesmoke"}}>CivicLens</Link>
                </div>
                    {theme === "light" ?
                <button 
                    title="Toggle theme"
                    onClick={toggleTheme}
                    className="btn btn-outline-light border-0 p-1 d-flex align-items-center justify-content-center"
                    style={{
                        width: "25px",
                        height: "25px",
                    }}
                >
                    <DarkModeIcon />
                </button>
                :
                <button 
                    title="Toggle theme"
                    onClick={toggleTheme}
                    className="btn btn-outline-dark border-0 p-1 d-flex align-items-center justify-content-center"
                    style={{
                        width: "25px",
                        height: "25px",
                    }}
                >
                    <LightModeIcon />
                </button>
                }
            </div>
            <div className="searchBar">
                <input 
                    type="text" 
                    placeholder='Search for a meeting'
                    />
            </div>
        </nav>
    );
};

export default Navbar;
