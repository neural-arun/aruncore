"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { ChatPanel } from "../components/ChatPanel";
import { ProjectsView } from "../components/ProjectsView";
import { ManifestoView } from "../components/ManifestoView";
import { Sidebar } from "../components/Sidebar";
import { MobileBottomNav } from "../components/MobileBottomNav";
import { HandoffModal } from "../components/HandoffModal";
import { Message, ActiveTab, HandoffFormData } from "../lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" && window.location.hostname !== "localhost" ? "https://neural-arun-aruncore.hf.space" : "http://localhost:8000");

const TELEGRAM_ALERT_BOT_TOKEN = "8847600936:AAHHy0cy98JkPo86Iuld1IRQML5NaSsMbqo";
const TELEGRAM_ALERT_CHAT_ID = "1154451605";

const sendClientTelegramAlert = (userMessage: string, category: string = "PRODUCTION ALERT") => {
  if (typeof window === "undefined") return;
  try {
    const url = `https://api.telegram.org/bot${TELEGRAM_ALERT_BOT_TOKEN}/sendMessage`;
    const escaped = userMessage.replace(/</g, "&lt;").replace(/>/g, "&gt;").substring(0, 1000);
    const text = `🚨 <b>${category}</b>\n\n<b>User Message:</b>\n${escaped}\n\n<b>Contact:</b> +91 8881109193 | neural.arun.dev@gmail.com`;

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_ALERT_CHAT_ID,
        text: text,
        parse_mode: "HTML",
        disable_web_page_preview: true,
      }),
    }).catch((err) => console.warn("Client-side Telegram dispatch error:", err));
  } catch (e) {
    console.warn("Client-side Telegram dispatch failed:", e);
  }
};

export default function Home() {
  const [sessionId, setSessionId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>("chat");
  const [isHandoffOpen, setIsHandoffOpen] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [activePrompt, setActivePrompt] = useState<string>("");
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [isAdminMode, setIsAdminMode] = useState<boolean>(false);
  const [adminToken, setAdminToken] = useState<string>("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      const urlSession = urlParams.get("session_id");
      const urlToken = urlParams.get("admin_token");

      if (urlSession) {
        setSessionId(urlSession);
        if (urlToken) {
          setAdminToken(urlToken);
          fetch(`${API_BASE_URL}/chat/verify-admin-token?session_id=${encodeURIComponent(urlSession)}&admin_token=${encodeURIComponent(urlToken)}`)
            .then((res) => res.json())
            .then((data) => {
              if (data && data.valid) {
                setIsAdminMode(true);
              }
            })
            .catch((err) => console.warn("Admin verify error:", err));
        }

        // Instantly load existing chat history for this exact session
        fetch(`${API_BASE_URL}/chat/history?session_id=${encodeURIComponent(urlSession)}`)
          .then((res) => res.json())
          .then((data) => {
            if (data && data.messages && data.messages.length > 0) {
              setMessages(data.messages);
            }
          })
          .catch((err) => console.warn("Fetch chat history error:", err));
      } else {
        const newSession = `session_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
        setSessionId(newSession);
      }
    }

    setTheme("light");
    localStorage.setItem("aruncore_theme", "light");
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    const interval = setInterval(async () => {
      if (isStreaming) return;

      try {
        const res = await fetch(`${API_BASE_URL}/chat/history?session_id=${encodeURIComponent(sessionId)}`);
        if (res.ok) {
          const data = await res.json();
          if (data.messages && data.messages.length > 0) {
            setMessages((prev) => {
              if (data.messages.length >= prev.length) {
                const prevIds = prev.map((m) => m.id).join(",");
                const newIds = data.messages.map((m: any) => m.id).join(",");
                if (prevIds !== newIds) {
                  return data.messages;
                }
              }
              return prev;
            });
          }
        }
      } catch (e) {
        // Silent poll error
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [sessionId, isStreaming]);

  const handleSendAdminMessage = async (adminText: string) => {
    if (!adminText.trim() || !isAdminMode || !sessionId || !adminToken) return;

    try {
      const response = await fetch(`${API_BASE_URL}/chat/human-message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          admin_token: adminToken,
          message: adminText,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data && data.entry) {
          setMessages((prev) => {
            if (prev.some((m) => m.id === data.entry.id)) return prev;
            return [...prev, data.entry];
          });
        }
      }
    } catch (err) {
      console.error("Failed to send admin human message:", err);
    }
  };

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
              if (
                data.content &&
                (data.content.includes("Sending notification") ||
                  data.content.includes("Triggering instant Telegram alert"))
              ) {
                sendClientTelegramAlert(text, "LIVE CHAT ALERT");
              }
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
    const leadMessage = `[DIRECT HANDOFF FORM]\nName: ${formData.name}\nContact: ${formData.emailOrPhone}\nCompany: ${formData.company || 'N/A'}\nMessage: ${formData.message}`;
    sendClientTelegramAlert(leadMessage, "💼 HANDOFF FORM LEAD");
    await handleSendMessage(leadMessage);
  };

  return (
    <div className="flex h-[100dvh] h-screen flex-col overflow-hidden bg-[var(--bg-main)] text-[var(--text-main)] transition-colors duration-200">
      {isAdminMode && (
        <div className="bg-emerald-600/90 text-white font-mono text-xs px-4 py-2 flex items-center justify-between shadow-md shrink-0">
          <span className="flex items-center gap-2 font-bold">
            <span className="h-2.5 w-2.5 rounded-full bg-white animate-ping" />
            <span>🟢 LOGGED IN AS REAL ARUN YADAV — LIVE 3-WAY CHAT ROOM</span>
          </span>
          <span className="text-[11px] font-mono opacity-90">Session: {sessionId}</span>
        </div>
      )}

      {/* Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        openHandoffModal={() => setIsHandoffOpen(true)}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      {/* Main Content View with Laptop Sidebar */}
      <main className="flex-1 overflow-hidden flex flex-col lg:flex-row">
        {/* Laptop Sidebar Navigation (Hidden on Mobile, Visible on Desktop/Laptop) */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          openHandoffModal={() => setIsHandoffOpen(true)}
          onSelectPrompt={(p) => {
            setActivePrompt(p);
            setActiveTab("chat");
          }}
          onResetSession={handleResetSession}
          messageCount={messages.length}
        />

        {/* Dynamic Content Panel */}
        <div className="flex-1 h-full overflow-hidden pb-14 lg:pb-0">
          {activeTab === "chat" && (
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              isStreaming={isStreaming}
              onResetSession={handleResetSession}
              activePrompt={activePrompt}
              setActivePrompt={setActivePrompt}
              openHandoffModal={() => setIsHandoffOpen(true)}
              isAdminMode={isAdminMode}
              onSendAdminMessage={handleSendAdminMessage}
            />
          )}

          {activeTab === "projects" && (
            <ProjectsView
              onSelectPrompt={(p) => {
                setActivePrompt(p);
                setActiveTab("chat");
              }}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === "manifesto" && <ManifestoView />}
        </div>
      </main>

      {/* Contact Handoff Modal */}
      <HandoffModal
        isOpen={isHandoffOpen}
        onClose={() => setIsHandoffOpen(false)}
        onSendHandoff={handleSendHandoff}
      />

      {/* Mobile Bottom Navigation Bar (App-like 1-tap switching on mobile) */}
      <MobileBottomNav
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        openHandoffModal={() => setIsHandoffOpen(true)}
      />
    </div>
  );
}
