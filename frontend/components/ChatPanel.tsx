"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Image from "next/image";
import { Message } from "../lib/types";
import { Send, Copy, Check, ChevronDown, ChevronRight, Sparkles, Terminal, PhoneCall, ArrowRight, Activity, Cpu, Volume2, Square, Loader2, Mic, MicOff } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isStreaming: boolean;
  onResetSession: () => void;
  activePrompt: string;
  setActivePrompt: (prompt: string) => void;
  openHandoffModal: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  isStreaming,
  onResetSession,
  activePrompt,
  setActivePrompt,
  openHandoffModal,
}) => {
  const [inputText, setInputText] = useState("");
  const [expandedThoughts, setExpandedThoughts] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [isLoadingAudio, setIsLoadingAudio] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  useEffect(() => {
    if (activePrompt) {
      setInputText(activePrompt);
      setActivePrompt("");
    }
  }, [activePrompt, setActivePrompt]);

  // Clean up audio & speech recognition on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!inputText.trim() || isStreaming) return;
    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
    }
    onSendMessage(inputText.trim());
    setInputText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const baseTextRef = useRef<string>("");

  // Speech-To-Text (STT) Microphone Handler
  const handleToggleListening = () => {
    if (typeof window === "undefined") return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in your browser. Please try Chrome or Edge.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      setIsListening(false);
      return;
    }

    try {
      baseTextRef.current = inputText.trim();
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event: any) => {
        let currentSpeech = "";
        for (let i = 0; i < event.results.length; i++) {
          currentSpeech += event.results[i][0].transcript;
        }

        const base = baseTextRef.current;
        const newText = base ? `${base} ${currentSpeech.trim()}` : currentSpeech.trim();
        setInputText(newText);

        if (textareaRef.current) {
          textareaRef.current.style.height = "auto";
          textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error !== "no-speech" && event.error !== "aborted") {
          console.warn("Speech recognition notice:", event.error);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
      setIsListening(true);
    } catch (e) {
      console.error("Failed to start speech recognition:", e);
      setIsListening(false);
    }
  };

  // Text-To-Speech (TTS) Voice Synthesis
  const handleToggleSpeech = async (msgId: string, text: string) => {
    if (playingMessageId === msgId) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      setPlayingMessageId(null);
      setIsLoadingAudio(null);
      return;
    }

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    setIsLoadingAudio(msgId);

    const cleanText = text
      .replace(/[*_#`~\[\]()]/g, " ")
      .replace(/https?:\/\/\S+/g, "")
      .replace(/\n+/g, ". ")
      .trim();

    if (!cleanText) {
      setIsLoadingAudio(null);
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: cleanText, voice: "alloy" }),
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        const audio = new Audio(url);
        audioRef.current = audio;

        audio.onended = () => {
          setPlayingMessageId(null);
          setIsLoadingAudio(null);
        };
        audio.onerror = () => {
          fallbackBrowserSpeech(msgId, cleanText);
        };

        setIsLoadingAudio(null);
        setPlayingMessageId(msgId);
        await audio.play();
        return;
      }
    } catch (e) {
      console.warn("Neural TTS endpoint fallback:", e);
    }

    fallbackBrowserSpeech(msgId, cleanText);
  };

  const fallbackBrowserSpeech = (msgId: string, cleanText: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setIsLoadingAudio(null);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.05;

    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(
      (v) =>
        v.name.includes("Google") ||
        v.name.includes("Natural") ||
        v.name.includes("Samantha") ||
        v.name.includes("Daniel") ||
        v.lang.startsWith("en")
    );
    if (naturalVoice) utterance.voice = naturalVoice;

    utterance.onend = () => {
      setPlayingMessageId(null);
      setIsLoadingAudio(null);
    };
    utterance.onerror = () => {
      setPlayingMessageId(null);
      setIsLoadingAudio(null);
    };

    setIsLoadingAudio(null);
    setPlayingMessageId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  const starterPrompts = [
    {
      title: "Healthcare Systems & Automation",
      query: "How can your AI systems automate clinical workflows and reduce operational costs?",
    },
    {
      title: "Zero-Hallucination RAG Architecture",
      query: "How do you build zero-hallucination RAG engines for trusted knowledge search?",
    },
    {
      title: "Recent Work & Live Repositories",
      query: "What has Arun been working on recently? Fetch his latest GitHub activity and commits!",
    },
    {
      title: "Consulting & Project Collaboration",
      query: "How can our team hire or consult with Arun to build custom AI software?",
    },
  ];

  return (
    <div className="flex h-full flex-col justify-between overflow-hidden bg-[var(--bg-main)]">
      {messages.length === 0 ? (
        /* Symmetrical Single-Viewport Landing (Mobile & Laptop Optimized) */
        <div className="flex-1 flex flex-col justify-center px-3 py-2 sm:px-8 sm:py-3 overflow-y-auto sm:overflow-hidden">
          <div className="mx-auto max-w-4xl w-full flex flex-col justify-center gap-3 sm:gap-4 my-auto">
            
            {/* Hero Card */}
            <div className="rounded-2xl border-2 border-[var(--border-subtle)] bg-[var(--bg-surface)] p-3.5 sm:p-6 backdrop-blur-md shadow-lg space-y-3 sm:space-y-3.5">
              <div className="flex flex-row items-center sm:items-center gap-3 sm:gap-4">
                <div className="relative h-14 w-14 sm:h-20 sm:w-20 overflow-hidden rounded-2xl border-2 border-[var(--accent-green)] bg-slate-800 shrink-0 shadow-md">
                  <Image
                    src="/profile_photo.png"
                    alt="Arun Yadav"
                    width={80}
                    height={80}
                    className="h-full w-full object-cover"
                    priority
                  />
                </div>

                <div className="space-y-0.5 sm:space-y-1 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h1 className="font-heading text-xl sm:text-3xl font-extrabold text-[var(--text-main)] tracking-tight">
                      Arun Yadav
                    </h1>
                    <span className="rounded-md border border-[var(--border-accent)] bg-[var(--bg-main)] px-2 py-0.5 font-mono text-[10px] sm:text-xs font-semibold text-[var(--accent-green)] flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                      <span>Arun's Assistant Online</span>
                    </span>
                  </div>

                  <p className="text-xs sm:text-base font-bold text-[var(--accent-amber)] leading-tight">
                    AI Systems Architect • Healthcare & Education
                  </p>

                  <p className="hidden sm:block text-xs sm:text-sm text-[var(--text-muted)] leading-relaxed font-medium">
                    I build AI-powered software systems that automate complex workflows, structure medical knowledge, and help organizations scale expertise.
                  </p>
                </div>
              </div>

              <p className="sm:hidden text-xs text-[var(--text-muted)] leading-relaxed font-medium">
                I build AI software systems that automate complex workflows, structure knowledge, and scale expertise.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-2.5 pt-2.5 sm:pt-3 border-t border-[var(--border-subtle)]">
                <button
                  onClick={openHandoffModal}
                  className="flex items-center justify-center gap-2 rounded-xl bg-[var(--accent-green)] px-4 py-2 text-xs sm:text-sm font-bold text-white shadow-sm hover:opacity-90 transition-all w-full sm:w-auto"
                >
                  <PhoneCall className="h-4 w-4" />
                  <span>Contact & Consult Arun</span>
                </button>

                <a
                  href="mailto:neural.arun.dev@gmail.com"
                  className="flex items-center justify-center gap-1.5 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-main)] px-3.5 py-2 text-xs sm:text-sm font-bold text-[var(--text-main)] hover:border-[var(--border-accent)] transition-all w-full sm:w-auto"
                >
                  <span>neural.arun.dev@gmail.com</span>
                </a>
              </div>
            </div>

            {/* 2x2 Question Grid */}
            <div className="space-y-1.5 sm:space-y-2">
              <span className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-[var(--text-dim)] px-1">
                Click to Ask Arun's AI Assistant
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                {starterPrompts.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(item.query)}
                    className="group text-left rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-3 sm:p-4 transition-all hover:border-[var(--accent-green)] hover:bg-[var(--bg-surface-hover)] hover:shadow-sm active:scale-[0.99]"
                  >
                    <div className="flex items-center justify-between gap-2 text-xs sm:text-sm font-bold text-[var(--accent-green)] mb-0.5 sm:mb-1">
                      <div className="flex items-center gap-1.5 sm:gap-2">
                        <Sparkles className="h-3.5 w-3.5 shrink-0" />
                        <span className="line-clamp-1">{item.title}</span>
                      </div>
                      <ArrowRight className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 hidden sm:block" />
                    </div>
                    <p className="text-xs sm:text-sm text-[var(--text-main)] font-medium leading-relaxed line-clamp-2">
                      "{item.query}"
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Prominent Input Bar with STT Microphone Button */}
            <div>
              {isListening && (
                <div className="mb-2 flex items-center justify-center gap-2 rounded-xl bg-rose-500/10 border border-rose-500/30 py-1.5 text-xs font-mono font-bold text-rose-600 animate-pulse">
                  <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
                  <span>Listening to your voice... Speak now!</span>
                </div>
              )}

              <div className="input-box-container relative flex items-center px-3 py-1.5 sm:px-4 sm:py-2">
                <textarea
                  ref={textareaRef}
                  value={inputText}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder={isListening ? "Listening..." : "Ask Arun's AI Assistant..."}
                  rows={1}
                  className="flex-1 resize-none bg-transparent py-1.5 text-xs sm:text-base text-[var(--text-main)] placeholder-[var(--text-dim)] font-medium focus:outline-none max-h-28 min-h-[38px] sm:min-h-[40px]"
                />

                {/* Microphone STT Button */}
                <button
                  onClick={handleToggleListening}
                  className={`ml-1.5 sm:ml-2 flex h-9 w-9 sm:h-9 sm:w-9 items-center justify-center rounded-xl font-bold transition-all shadow-sm shrink-0 touch-manipulation ${
                    isListening
                      ? "bg-rose-500 text-white animate-pulse"
                      : "bg-[var(--bg-surface-hover)] border border-[var(--border-subtle)] text-[var(--text-main)] hover:border-[var(--border-accent)]"
                  }`}
                  title={isListening ? "Stop listening" : "Click to speak (Voice to text)"}
                >
                  {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </button>

                {/* Send Message Button */}
                <button
                  onClick={handleSend}
                  disabled={!inputText.trim() || isStreaming}
                  className="ml-1.5 sm:ml-2 flex h-9 w-9 sm:h-9 sm:w-9 items-center justify-center rounded-xl bg-[var(--accent-green)] text-white font-bold transition-all hover:opacity-95 active:scale-95 disabled:opacity-30 shadow-md shrink-0 touch-manipulation"
                  title="Send Message"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>

              <div className="mt-1 flex justify-between text-[10px] sm:text-[11px] text-[var(--text-dim)] font-medium px-1">
                <span>Press <kbd className="rounded bg-[var(--bg-surface-hover)] px-1 py-0.5 text-[9px] sm:text-[10px] font-mono border border-[var(--border-subtle)] text-[var(--text-main)] font-semibold">Enter</kbd> or 🎙️ Mic</span>
              </div>
            </div>

          </div>
        </div>
      ) : (
        /* Active Conversation View */
        <>
          <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-8">
            <div className="mx-auto max-w-4xl space-y-5">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col gap-1.5 ${
                    msg.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[95%] sm:max-w-[88%] rounded-2xl px-5 py-4 text-sm sm:text-base ${
                      msg.sender === "user"
                        ? "bg-[var(--bg-surface-hover)] text-[var(--text-main)] font-medium border border-[var(--border-subtle)] shadow-md"
                        : "border border-[var(--border-subtle)] bg-[var(--bg-surface)] text-[var(--text-main)] shadow-lg"
                    }`}
                  >
                    {/* Sender & Real-Time Stream Status Bar */}
                    <div className="flex items-center justify-between gap-4 mb-2.5 pb-1.5 border-b border-[var(--border-subtle)] text-xs text-[var(--text-muted)]">
                      <span className="font-semibold text-[var(--accent-green)] flex items-center gap-2">
                        {msg.sender === "user" ? (
                          "You"
                        ) : (
                          <>
                            <span>Arun's AI Assistant</span>
                            {msg.isStreaming && (
                              <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-600 animate-pulse">
                                <Activity className="h-3 w-3 animate-spin" />
                                <span>STREAMING RESPONSE BUFFER</span>
                              </span>
                            )}
                          </>
                        )}
                      </span>
                      <span className="font-mono text-[11px] text-[var(--text-dim)]">
                        {msg.timestamp}
                      </span>
                    </div>

                    {/* Reasoning steps trace */}
                    {msg.sender === "twin" && msg.thoughts && msg.thoughts.length > 0 && (
                      <div className="mb-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-main)] p-3 space-y-2">
                        <button
                          onClick={() =>
                            setExpandedThoughts((prev) => ({
                              ...prev,
                              [msg.id]: !prev[msg.id],
                            }))
                          }
                          className="flex items-center gap-2 font-mono text-xs text-[var(--accent-amber)] hover:text-[var(--accent-green)] transition-colors w-full"
                        >
                          <Cpu className="h-3.5 w-3.5 text-amber-500 animate-pulse" />
                          <span className="font-bold">Engine Execution Trace ({msg.thoughts.length} steps)</span>
                          {expandedThoughts[msg.id] ? (
                            <ChevronDown className="h-3.5 w-3.5 ml-auto" />
                          ) : (
                            <ChevronRight className="h-3.5 w-3.5 ml-auto" />
                          )}
                        </button>

                        {(expandedThoughts[msg.id] || msg.isStreaming) && (
                          <div className="space-y-1 font-mono text-xs text-[var(--text-muted)] border-t border-[var(--border-subtle)] pt-2">
                            {msg.thoughts.map((th, idx) => (
                              <div key={idx} className="flex items-center gap-2">
                                <span className="text-[var(--accent-amber)] font-bold">[{idx + 1}]</span>
                                <span>{th}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Real-time Streaming Content */}
                    {msg.sender === "user" ? (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                    ) : (
                      <div className="prose-professional relative">
                        {msg.isStreaming && !msg.text ? (
                          <div className="py-2 text-xs font-mono text-[var(--accent-green)] flex items-center gap-2.5">
                            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping" />
                            <span>Retrieving vector embeddings & initializing token buffer...</span>
                          </div>
                        ) : (
                          <>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.text}
                            </ReactMarkdown>
                            {msg.isStreaming && (
                              <span className="inline-block h-4 w-2 bg-[var(--accent-green)] animate-pulse ml-1 align-middle rounded-xs" />
                            )}
                          </>
                        )}
                      </div>
                    )}

                    {/* Action Bar: High Quality Speech & Copy Button */}
                    {msg.sender === "twin" && msg.text && !msg.isStreaming && (
                      <div className="mt-3 flex items-center justify-end gap-3 border-t border-[var(--border-subtle)] pt-2">
                        {/* High-Quality Text-To-Speech Button */}
                        <button
                          onClick={() => handleToggleSpeech(msg.id, msg.text)}
                          disabled={isLoadingAudio === msg.id}
                          className={`flex items-center gap-1.5 text-xs font-bold transition-colors ${
                            playingMessageId === msg.id
                              ? "text-rose-500 animate-pulse"
                              : "text-[var(--accent-green)] hover:opacity-80"
                          }`}
                          title={playingMessageId === msg.id ? "Stop voice playback" : "Listen in HD neural voice"}
                        >
                          {isLoadingAudio === msg.id ? (
                            <>
                              <Loader2 className="h-3.5 w-3.5 animate-spin text-[var(--accent-green)]" />
                              <span>Loading Voice...</span>
                            </>
                          ) : playingMessageId === msg.id ? (
                            <>
                              <Square className="h-3.5 w-3.5 fill-current text-rose-500" />
                              <span>Stop Voice</span>
                            </>
                          ) : (
                            <>
                              <Volume2 className="h-3.5 w-3.5" />
                              <span>Listen (HD Voice)</span>
                            </>
                          )}
                        </button>

                        <span className="text-[var(--border-subtle)]">|</span>

                        {/* Copy Text Button */}
                        <button
                          onClick={() => copyToClipboard(msg.id, msg.text)}
                          className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors font-medium"
                          title="Copy Response"
                        >
                          {copiedId === msg.id ? (
                            <>
                              <Check className="h-3.5 w-3.5 text-emerald-500" />
                              <span className="text-emerald-500 font-semibold">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3.5 w-3.5" />
                              <span>Copy Text</span>
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Active Input Bar with STT Microphone Button */}
          <div className="border-t border-[var(--border-subtle)] bg-[var(--bg-main)] px-4 py-4 sm:px-8">
            <div className="mx-auto max-w-4xl">
              {isListening && (
                <div className="mb-2 flex items-center justify-center gap-2 rounded-xl bg-rose-500/10 border border-rose-500/30 py-1.5 text-xs font-mono font-bold text-rose-600 animate-pulse">
                  <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
                  <span>Listening to your voice... Speak now!</span>
                </div>
              )}

              <div className="input-box-container relative flex items-center px-4 py-2">
                <textarea
                  ref={textareaRef}
                  value={inputText}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder={isListening ? "Listening..." : "Ask Arun's AI Assistant about systems engineering, RAG architecture, or hiring Arun..."}
                  rows={1}
                  className="flex-1 resize-none bg-transparent py-1.5 text-sm sm:text-base text-[var(--text-main)] placeholder-[var(--text-dim)] font-medium focus:outline-none max-h-28 min-h-[40px]"
                />

                {/* Microphone STT Button */}
                <button
                  onClick={handleToggleListening}
                  className={`ml-2 flex h-9 w-9 items-center justify-center rounded-xl font-bold transition-all shadow-sm shrink-0 ${
                    isListening
                      ? "bg-rose-500 text-white animate-pulse"
                      : "bg-[var(--bg-surface-hover)] border border-[var(--border-subtle)] text-[var(--text-main)] hover:border-[var(--border-accent)]"
                  }`}
                  title={isListening ? "Stop listening" : "Click to speak (Voice to text)"}
                >
                  {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </button>

                {/* Send Message Button */}
                <button
                  onClick={handleSend}
                  disabled={!inputText.trim() || isStreaming}
                  className="ml-2 flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-green)] text-white font-bold transition-all hover:opacity-95 active:scale-95 disabled:opacity-30 shadow-md shrink-0"
                  title="Send Message (Enter)"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>

              <div className="mt-1 flex items-center justify-between text-[11px] text-[var(--text-dim)] font-medium px-1">
                <span>Press <kbd className="rounded bg-[var(--bg-surface-hover)] px-1.5 py-0.5 text-[10px] font-mono border border-[var(--border-subtle)] text-[var(--text-main)] font-semibold">Enter</kbd> to send or use 🎙️ Mic</span>
                <button
                  onClick={onResetSession}
                  className="hover:text-[var(--accent-amber)] transition-colors"
                >
                  Clear conversation
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
