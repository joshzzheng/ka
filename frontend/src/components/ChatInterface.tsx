import React, { useState } from "react";

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const newMessage: Message = {
      id: Date.now(),
      text: inputMessage,
      sender: "user",
    };

    setMessages([...messages, newMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from server");
      }

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now(),
        text: data.response,
        sender: "bot",
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        id: Date.now(),
        text: "Sorry, there was an error processing your message. Please try again.",
        sender: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#1a1a1a] rounded-lg pt-5 shadow-md">
      <div className="flex-1 overflow-y-auto max-h-150 p-5 flex flex-col gap-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-[70%] p-3 rounded-xl mb-2 ${
              message.sender === "user"
                ? "bg-[#646cff] text-white self-end"
                : "bg-[#f0f0f0] text-[#333] self-start"
            }`}
          >
            <div className="flex flex-col">
              <p className="m-0 break-words">{message.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="max-w-[70%] p-3 rounded-xl mb-2 bg-[#f0f0f0] text-[#333] self-start">
            <div className="flex flex-col">
              <p className="m-0">Thinking...</p>
            </div>
          </div>
        )}
      </div>
      <form
        onSubmit={handleSendMessage}
        className="flex p-4 border-t border-[#e0e0e0] bg-[#1a1a1a]"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 px-3 py-2 border border-[#ddd] rounded-full mr-2 text-sm outline-none focus:border-[#007bff] transition-colors duration-200"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="px-5 py-2 bg-[#646cff] text-white border-none rounded-full cursor-pointer font-medium transition-colors duration-200 hover:bg-[#535bf2] disabled:opacity-50"
          disabled={isLoading}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
