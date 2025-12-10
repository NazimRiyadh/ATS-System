import React, { useState, useRef, useEffect } from "react";
import { Send, X } from "lucide-react";
import { chatWithCandidate } from "@/lib/api";

interface ChatBoxProps {
    candidateId: string;
    candidateName: string;
    onClose: () => void;
}

interface Message {
    role: "user" | "assistant";
    content: string;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
    candidateId,
    candidateName,
    onClose,
}) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input;
        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await chatWithCandidate(candidateId, userMessage);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: response },
            ]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Sorry, I encountered an error." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col h-[500px] z-50">
            {/* Header */}
            <div className="p-4 border-b bg-blue-600 text-white rounded-t-lg flex justify-between items-center">
                <div>
                    <h3 className="font-semibold">Chat with Profile</h3>
                    <p className="text-xs text-blue-100">Re: {candidateName}</p>
                </div>
                <button onClick={onClose} className="hover:bg-blue-700 p-1 rounded">
                    <X className="w-5 h-5" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 text-sm mt-10">
                        Ask questions about {candidateName}'s experience, skills, or background.
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                            }`}
                    >
                        <div
                            className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-br-none"
                                    : "bg-gray-100 text-gray-800 rounded-bl-none"
                                }`}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 p-3 rounded-lg rounded-bl-none text-sm text-gray-500">
                            Thinking...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-4 border-t">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 outline-none text-sm"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </form>
        </div>
    );
};
