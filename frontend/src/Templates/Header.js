import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';

const Header = () => {
  return (
    <Navbar bg="primary" variant="dark">
      <Nav className="mr-auto">
        <Nav.Link className="nav-font-size" href="/">
          YesNope
        </Nav.Link>
      </Nav>
    </Navbar>
  );
};

export default Header;
