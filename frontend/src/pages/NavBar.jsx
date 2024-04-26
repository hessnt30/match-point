import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import "../styles/navbar.css";

function NavBar({ loggedIn }) {
  return (
    <Navbar className="navbar" bg="dark" data-bs-theme="dark" fixed="top">
      <Container className="nav-container">
        <Navbar.Brand href="/dashboard">Navbar</Navbar.Brand>
        <Nav className="me-auto">
          {loggedIn && (
            <>
              <Nav.Link className="nav-link" href="/dashboard">
                Dashboard
              </Nav.Link>
              <Nav.Link className="nav-link" href="#groups">
                Groups
              </Nav.Link>
              <Nav.Link className="nav-link" href="#profile">
                Profile
              </Nav.Link>
            </>
          )}
        </Nav>
      </Container>
    </Navbar>
  );
}

export default NavBar;
