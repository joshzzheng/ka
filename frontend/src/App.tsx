import { Routes, Route, Link } from "react-router-dom";
import "./App.css";
import FileUpload from "./components/FileUpload";
import ChatInterface from "./components/ChatInterface";

function Home() {
  return (
    <div className="page-container">
      <div className="content-wrapper">
        <FileUpload />
        <div className="main-content">
          <ChatInterface />
        </div>
      </div>
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
      </Routes>
    </div>
  );
}

export default App;
