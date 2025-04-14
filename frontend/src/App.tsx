import { Routes, Route, Link } from "react-router-dom";
import "./App.css";
import { useEffect, useState } from "react";
import FileUpload from "./components/FileUpload";

function Home() {
  //const [message, setMessage] = useState("");
  useEffect(() => {
    fetch("http://localhost:8000/api/hello/")
      .then((response) => response.text())
      .then((data) => setMessage(data));
  }, []);
  return (
    <div className="page-container">
      <div className="content-wrapper">
        <FileUpload />
        <div className="main-content">{/* Main content goes here */}</div>
      </div>
    </div>
  );
}

function About() {
  return (
    <div className="page-container">
      <div className="about-text">About Page</div>
    </div>
  );
}

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-title">
          App
        </Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">
            Home
          </Link>
          <Link to="/about" className="nav-link">
            About
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </div>
  );
}

export default App;
