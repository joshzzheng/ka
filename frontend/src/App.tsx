import { Routes, Route, Link } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import ChatInterface from "./components/ChatInterface";

function Home() {
  return (
    <div className="flex flex-col h-[calc(100vh-60px)]">
      <div className="flex flex-1 gap-5 mt-5">
        <FileUpload />
        <div className="flex-1 bg-[#1a1a1a] rounded-lg p-5">
          <ChatInterface />
        </div>
      </div>
    </div>
  );
}

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 h-[60px] bg-[#242424] shadow-md z-50">
      <div className="max-w-7xl mx-auto h-full flex items-center justify-between px-8">
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
    <div className="pt-[60px]">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </div>
  );
}

export default App;
