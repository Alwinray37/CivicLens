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
        <nav className="bg-body-secondary" style={styles.nav}>
            <div className="d-flex gap-3">
                <div style={styles.logo}>
                    <Link to="/" className="link-body-emphasis" style={styles.link}>CivicLens</Link>
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
            <ul style={styles.navLinks}>
                <li><Link to="/" className="link-body-emphasis" style={styles.link}>Home</Link></li>
            </ul>
        </nav>
    );
}

const styles = {
    // nav: {
    //     display: 'flex',
    //     justifyContent: 'space-between',
    //     alignItems: 'center',
    //     background: '#222',
    //     padding: '1rem 2rem',
    // },
    // logo: {
    //     fontWeight: 'bold',
    //     fontSize: '1.5rem',
    // },
    // navLinks: {
    //     listStyle: 'none',
    //     display: 'flex',
    //     gap: '1.5rem',
    //     margin: 0,
    //     padding: 0,
    // },
    // link: {
    //     color: '#fff',
    //     textDecoration: 'none',
    //     fontSize: '1rem',
    // },
};

export default Navbar;
