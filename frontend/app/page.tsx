"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { ChatPanel } from "../components/ChatPanel";
import { ProjectsView } from "../components/ProjectsView";
import { ManifestoView } from "../components/ManifestoView";
import { HandoffModal } from "../components/HandoffModal";
import { Message, ActiveTab, HandoffFormData } from "../lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" && window.location.hostname !== "localhost" ? "https://neural-arun-aruncore.hf.space" : "http://localhost:8000");

export default function Home() {
  const [sessionId, setSessionId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>("chat");
  const [isHandoffOpen, setIsHandoffOpen] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [activePrompt, setActivePrompt] = useState<string>("");
  const [theme, setTheme] = useState<"dark" | "light">("light");

  useEffect(() => {
    const newSession = `session_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    setSessionId(newSession);

    // Default to Light Mode
    setTheme("light");
    localStorage.setItem("aruncore_theme", "light");
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
      root.classList.remove("light");
    } else {
      root.classList.remove("dark");
      root.classList.add("light");
    }
    localStorage.setItem("aruncore_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const handleResetSession = () => {
    const newSession = `session_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    setSessionId(newSession);
    setMessages([]);
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const userMessageId = `msg_user_${Date.now()}`;
    const timestampStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const userMsg: Message = {
      id: userMessageId,
      sender: "user",
      text,
      timestamp: timestampStr,
    };

    const twinMessageId = `msg_twin_${Date.now()}`;
    const twinMsgPlaceholder: Message = {
      id: twinMessageId,
      sender: "twin",
      text: "",
      timestamp: timestampStr,
      thoughts: [],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMsg, twinMsgPlaceholder]);
    setIsStreaming(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: text,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Server returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            if (data.type === "status") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === twinMessageId
                    ? { ...m, thoughts: [...(m.thoughts || []), data.content] }
                    : m
                )
              );
            } else if (data.type === "token") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === twinMessageId
                    ? {
                        ...m,
                        text: (m.text || "") + data.content,
                        isStreaming: true,
                      }
                    : m
                )
              );
            } else if (data.type === "final") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === twinMessageId
                    ? {
                        ...m,
                        text: data.reply || m.text,
                        thoughts: data.thoughts && data.thoughts.length > 0 ? data.thoughts : m.thoughts,
                        isStreaming: false,
                      }
                    : m
                )
              );
            } else if (data.type === "error") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === twinMessageId
                    ? {
                        ...m,
                        text: `Error: ${data.content}`,
                        isStreaming: false,
                        error: true,
                      }
                    : m
                )
              );
            }
          } catch (e) {
            console.error("NDJSON parse error:", e);
          }
        }
      }
    } catch (err: any) {
      // Offline fallback simulation streaming
      const fallbackText = `I am **ArunCore**, the AI Digital Assistant of Arun Yadav.

Think of me as Arun's interactive AI representative. I can answer questions about his work, technical background, engineering philosophy, current focus, and the AI systems he builds.

Arun specializes in building trustworthy AI infrastructure for Healthcare and Education—combining large language models, knowledge retrieval, backend engineering, and intelligent automation into production-ready systems.

My goal is to help you quickly understand Arun's expertise, explore collaboration opportunities, and answer questions about his work with clarity and accuracy.

### Direct Contact
- **Phone / Call:** +91 8881109193
- **WhatsApp:** https://wa.me/918881109193
- **Email:** neural.arun.dev@gmail.com`;

      // Stream fallback tokens for visualization
      const tokens = fallbackText.split(" ");
      let currentText = "";
      for (const tok of tokens) {
        currentText += tok + " ";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === twinMessageId
              ? {
                  ...m,
                  text: currentText,
                  thoughts: ["Searching Arun's systems knowledge base..."],
                  isStreaming: true,
                }
              : m
          )
        );
        await new Promise((r) => setTimeout(r, 25));
      }

      setMessages((prev) =>
        prev.map((m) =>
          m.id === twinMessageId
            ? {
                ...m,
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSendHandoff = async (formData: HandoffFormData) => {
    const leadMessage = `[DIRECT CONTACT]\nName: ${formData.name}\nContact: ${formData.emailOrPhone}\nMessage: ${formData.message}`;
    await handleSendMessage(leadMessage);
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[var(--bg-main)] text-[var(--text-main)] transition-colors duration-200">
      {/* Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        openHandoffModal={() => setIsHandoffOpen(true)}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      {/* Main Content View */}
      <main className="flex-1 overflow-hidden">
        {activeTab === "chat" && (
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isStreaming={isStreaming}
            onResetSession={handleResetSession}
            activePrompt={activePrompt}
            setActivePrompt={setActivePrompt}
            openHandoffModal={() => setIsHandoffOpen(true)}
          />
        )}

        {activeTab === "projects" && (
          <ProjectsView
            onSelectPrompt={(p) => setActivePrompt(p)}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === "manifesto" && <ManifestoView />}
      </main>

      {/* Contact Handoff Modal */}
      <HandoffModal
        isOpen={isHandoffOpen}
        onClose={() => setIsHandoffOpen(false)}
        onSendHandoff={handleSendHandoff}
      />
    </div>
  );
}
