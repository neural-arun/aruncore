"use client";

import React from "react";
import Image from "next/image";
import { MessageCircle, Sparkles, RefreshCw, Layers, ShieldCheck, HeartPulse, GraduationCap, Scale, Briefcase } from "lucide-react";

// Inline Brand SVGs for bulletproof icon rendering
const GithubIcon = () => (
  <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

const LinkedinIcon = () => (
  <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24">
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
  </svg>
);

const TwitterIcon = () => (
  <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

interface SidebarProps {
  onSelectPrompt: (prompt: string) => void;
  onResetSession: () => void;
  messageCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  onSelectPrompt,
  onResetSession,
  messageCount,
}) => {
  const promptCategories = [
    {
      category: "Healthcare & MedTech",
      icon: <HeartPulse className="h-3.5 w-3.5 text-rose-400" />,
      prompts: [
        "How do you build trusted AI software for healthcare?",
        "Tell me about your Clinical Patient Task Manager.",
      ],
    },
    {
      category: "RAG & AI Architecture",
      icon: <Layers className="h-3.5 w-3.5 text-amber-400" />,
      prompts: [
        "Explain your zero-hallucination hybrid RAG architecture.",
        "How does ArunCore re-rank chunks using Cohere?",
      ],
    },
    {
      category: "Legal & Professional AI",
      icon: <Scale className="h-3.5 w-3.5 text-indigo-400" />,
      prompts: [
        "How did you build the Indian Legal RAG System?",
        "What is your approach to document-aware chunking?",
      ],
    },
    {
      category: "Education & Learning",
      icon: <GraduationCap className="h-3.5 w-3.5 text-cyan-400" />,
      prompts: [
        "Tell me about NEET Bot & clinical learning systems.",
        "How does your YouTube Notes Extractor work?",
      ],
    },
    {
      category: "Working With Arun",
      icon: <Briefcase className="h-3.5 w-3.5 text-emerald-400" />,
      prompts: [
        "What are your core engineering principles?",
        "How can I work with or consult Arun for a project?",
      ],
    },
  ];

  return (
    <aside className="flex flex-col gap-4 overflow-y-auto p-4 text-slate-300">
      {/* Profile Card */}
      <div className="relative overflow-hidden rounded-2xl border border-amber-500/20 bg-gradient-to-b from-slate-900/90 to-slate-950/90 p-4 shadow-xl backdrop-blur-md">
        <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-amber-500/10 blur-2xl pointer-events-none" />

        <div className="flex items-center gap-3.5">
          <div className="relative">
            <div className="h-14 w-14 overflow-hidden rounded-xl border border-amber-500/40 bg-slate-800 shadow-md">
              <Image
                src="/profile_photo.png"
                alt="Arun Yadav"
                width={56}
                height={56}
                className="h-full w-full object-cover"
              />
            </div>
            <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-slate-950">
              <span className="h-2 w-2 rounded-full bg-white" />
            </span>
          </div>

          <div className="flex-1 min-w-0">
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5 truncate">
              Arun Yadav
            </h2>
            <p className="text-xs font-medium text-amber-400 truncate">
              Systems Builder & AI Entrepreneur
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
              <ShieldCheck className="h-3 w-3 text-emerald-400 shrink-0" />
              Stateful RAG • Zero-Hallucination
            </p>
          </div>
        </div>

        <p className="mt-3 text-xs leading-relaxed text-slate-300">
          Building AI-powered software systems for Healthcare & Education that organizations trust to automate complex workflows and scale expertise.
        </p>

        {/* Social Links */}
        <div className="mt-3.5 flex items-center justify-between border-t border-white/5 pt-3">
          <a
            href="https://github.com/neural-arun"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-amber-400"
          >
            <GithubIcon />
            <span>GitHub</span>
          </a>

          <a
            href="https://linkedin.com/in/neuralarun"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-amber-400"
          >
            <LinkedinIcon />
            <span>LinkedIn</span>
          </a>

          <a
            href="https://x.com/Neural_Arun"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-[11px] font-medium text-slate-400 transition-colors hover:text-amber-400"
          >
            <TwitterIcon />
            <span>X / Twitter</span>
          </a>
        </div>
      </div>

      {/* Suggested Prompts Section */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            Ask My Digital Twin
          </span>
          {messageCount > 0 && (
            <button
              onClick={onResetSession}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-amber-400 transition-colors"
              title="Reset conversation session"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Reset</span>
            </button>
          )}
        </div>

        <div className="flex flex-col gap-3">
          {promptCategories.map((cat, idx) => (
            <div key={idx} className="rounded-xl border border-white/5 bg-slate-900/50 p-2.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200 mb-2">
                {cat.icon}
                <span>{cat.category}</span>
              </div>
              <div className="flex flex-col gap-1.5">
                {cat.prompts.map((p, pIdx) => (
                  <button
                    key={pIdx}
                    onClick={() => onSelectPrompt(p)}
                    className="text-left text-xs text-slate-300 hover:text-amber-300 hover:bg-amber-500/10 border border-transparent hover:border-amber-500/20 rounded-lg p-2 transition-all leading-snug"
                  >
                    "{p}"
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
