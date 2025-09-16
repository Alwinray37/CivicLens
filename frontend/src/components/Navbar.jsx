import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => (
    <nav style={styles.nav}>
        <div style={styles.logo}>
            <Link to="/" style={styles.link}>CivicLens</Link>
        </div>
        <ul style={styles.navLinks}>
            <li><Link to="/" style={styles.link}>Home</Link></li>
        </ul>
    </nav>
);

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