import { useState, useRef, useEffect } from "react";
import { Send, Bot, X, Sparkles } from "lucide-react";
import { getToken } from "@/lib/api";

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
  time: string;
}

export function AIChat({ incidentId, onClose }: { incidentId: string; onClose: () => void }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "ai",
      text: "I'm IncidentOps AI. I've analyzed this incident. What would you like to know?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  
  const apiBase = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);
    
    try {
      const res = await fetch(`${apiBase}/chat/${incidentId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify({ message: userMsg.text })
      });
      
      if (!res.ok) throw new Error("Failed to send message");
      
      const data = await res.json();
      
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: data.reply,
        time: data.time
      };
      
      setMessages(prev => [...prev, aiMsg]);
    } catch (e) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: "Sorry, I encountered an error connecting to the intelligence backend.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[500px] w-96 flex-col overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-900/95 shadow-2xl shadow-black/50 backdrop-blur-xl animate-enter">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-700/60 bg-slate-800/50 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-sky-500/10 text-sky-400">
            <Bot size={16} />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Ask AI</h3>
            <p className="text-[10px] text-slate-400">Context: {incidentId}</p>
          </div>
        </div>
        <button onClick={onClose} className="rounded-md p-1 text-slate-400 hover:bg-slate-700 hover:text-slate-200">
          <X size={16} />
        </button>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-xl p-3 text-sm ${msg.sender === "user" ? "bg-sky-500 text-white rounded-br-sm" : "bg-slate-800/80 text-slate-200 border border-slate-700/50 rounded-bl-sm"}`}>
              {msg.text}
              <div className={`mt-1 text-[9px] ${msg.sender === "user" ? "text-sky-200" : "text-slate-500"}`}>{msg.time}</div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex w-full justify-start">
            <div className="max-w-[85%] rounded-xl rounded-bl-sm border border-slate-700/50 bg-slate-800/80 p-3 text-sm text-slate-200">
              <span className="flex items-center gap-1">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]"></span>
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]"></span>
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"></span>
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      
      {/* Input */}
      <div className="border-t border-slate-700/60 bg-slate-900 p-3">
        <form 
          onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about logs, root cause..."
            className="focus-ring w-full rounded-xl border border-slate-700/60 bg-slate-800/50 py-2.5 pl-3 pr-10 text-sm text-slate-200 placeholder-slate-500 transition focus:bg-slate-800"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isTyping}
            className="absolute right-1.5 rounded-lg bg-sky-500 p-1.5 text-white transition hover:bg-sky-400 disabled:opacity-50"
          >
            <Send size={14} />
          </button>
        </form>
        <div className="mt-2 text-center text-[9px] text-slate-500 flex items-center justify-center gap-1">
          <Sparkles size={10} /> AI can make mistakes. Verify critical info.
        </div>
      </div>
    </div>
  );
}
