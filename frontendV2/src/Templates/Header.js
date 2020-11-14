import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';

const Header = () => {
  return (
    <Navbar bg="primary" variant="dark">
      <Nav className="mr-auto">
        <Nav.Link className="nav-font-size" href="/">
          DetectMe
        </Nav.Link>
      </Nav>
    </Navbar>
  );
};

export default Header;
