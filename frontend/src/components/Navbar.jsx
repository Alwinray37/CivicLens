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

        const mainEl = document.getElementsByClassName('main')[0];
        const navEl = document.getElementsByTagName('nav')[0];
        const navLinks = navEl.getElementsByTagName('a');
        if (newTheme === "dark") {
            mainEl.style.backgroundColor = "var(--color-primary)";
            mainEl.style.color = "whitesmoke";
            navEl.style.backgroundColor = "var(--color-primary)";
            navEl.style.color = "whitesmoke";
            for (let link of navLinks) {
                link.style.color = "whitesmoke";
            }

        } else {
            mainEl.style.backgroundColor = "var(--color-bg)";
            mainEl.style.color = "var(--color-primary)";
            navEl.style.backgroundColor = "var(--color-bg)";
            navEl.style.color = "var(--color-primary)";
            for (let link of navLinks) {
                link.style.color = "var(--color-primary)";
            }
        }
    }

    return (
        <nav className="" >
            <div className="d-flex gap-3 logo align-items-center">
                <div >
                    <Link to="/"><img src="/src/assets/images/logo lrg.png" alt="CivicLens Logo" style={{ height: "30px" }}></img> CivicLens</Link>
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
        </nav>
    );
};

export default Navbar;
