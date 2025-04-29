import { Routes, Route, Link } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import ChatInterface from "./components/ChatInterface";

function Home() {
  return (
    <div className="flex gap-5 mt-15">
      <div className="flex-1 p-5">
        <FileUpload />
      </div>
      <div className="flex-2 p-5">
        <ChatInterface />
      </div>
    </div>
  );
}

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 h-[60px] bg-[#242424] shadow-md z-50">
      <div className="h-full flex items-center justify-between px-8">
        <Link to="/" className="text-xl font-bold text-white no-underline">
          App
        </Link>
        <div className="flex gap-6">
          <Link
            to="/"
            className="text-white no-underline font-medium hover:text-[#646cff]"
          >
            Home
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </>
  );
}

export default App;
