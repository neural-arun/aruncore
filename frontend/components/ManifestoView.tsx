"use client";

import React from "react";
import Image from "next/image";
import { Sparkles } from "lucide-react";

export const ManifestoView: React.FC = () => {
  return (
    <div className="h-full overflow-y-auto px-4 py-8 sm:px-12 pb-24 sm:pb-12 bg-[var(--bg-main)] text-[var(--text-main)]">
      <div className="mx-auto max-w-3xl space-y-8 animate-fade-slide">
        
        {/* Header Hero Layout (Ed Donner Style) */}
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 pb-6 border-b border-[var(--border-subtle)]">
          <div className="relative h-32 w-32 sm:h-36 sm:w-36 overflow-hidden rounded-full border-4 border-emerald-500/40 shadow-xl shrink-0">
            <Image
              src="/profile_photo.png"
              alt="Arun Yadav"
              width={144}
              height={144}
              className="h-full w-full object-cover"
              priority
            />
          </div>

          <div className="space-y-3 text-center sm:text-left min-w-0 flex-1">
            <h1 className="font-heading text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tracking-tight">
              Who Am I. Arun Yadav
            </h1>
            <p className="text-base sm:text-lg font-bold text-emerald-600 dark:text-emerald-400">
              AI Systems Builder • Healthcare & Education
            </p>
            <p className="text-sm sm:text-base text-[var(--text-muted)] font-medium leading-relaxed">
              Well, hi there! 👋
            </p>
            <p className="text-sm sm:text-base text-[var(--text-muted)] font-medium leading-relaxed">
              I am Arun Yadav, an AI Systems Builder engineering trust, production-grade software. From zero-hallucination RAG engines and clinical reasoning AI tutors to automated workflow pipelines that solve high-stakes problems in Healthcare and Education.
            </p>
          </div>
        </div>

        {/* Highlighted Projects */}
        <div className="space-y-4">
          <h2 className="text-xl sm:text-2xl font-extrabold text-[var(--text-main)] tracking-tight flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-emerald-500" />
            <span>🚀 Highlighted Projects:</span>
          </h2>

          <div className="grid grid-cols-1 gap-3">
            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs transition-all hover:border-emerald-500/40">
              <h3 className="font-bold text-base sm:text-lg text-[var(--text-main)] flex items-center gap-2">
                <span>🤖 ArunCore</span>
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] mt-1 font-medium leading-relaxed">
                Zero-hallucination hybrid RAG engine combining ChromaDB vector search, BM25 keyword matching and Cohere reranking.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs transition-all hover:border-emerald-500/40">
              <h3 className="font-bold text-base sm:text-lg text-[var(--text-main)] flex items-center gap-2">
                <span>🏥 NEET Medical Bot</span>
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] mt-1 font-medium leading-relaxed">
                AI practice & diagnostic ecosystem for entrance exams with 10,000+ NCERT questions, spaced repetition and solution breakdowns.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs transition-all hover:border-emerald-500/40">
              <h3 className="font-bold text-base sm:text-lg text-[var(--text-main)] flex items-center gap-2">
                <span>🩺 MedCoach</span>
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] mt-1 font-medium leading-relaxed">
                Reasoning AI tutor and diagnostic workflow assistant built with guardrails & execution traces.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs transition-all hover:border-emerald-500/40">
              <h3 className="font-bold text-base sm:text-lg text-[var(--text-main)] flex items-center gap-2">
                <span>📝 AI Note. Legal RAG</span>
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] mt-1 font-medium leading-relaxed">
                Automated structured note generation and Indian legal document retrieval pipelines.
              </p>
            </div>
          </div>
        </div>

        {/* How I Work */}
        <div className="space-y-4 pt-2">
          <h2 className="text-xl sm:text-2xl font-extrabold text-[var(--text-main)] tracking-tight">
            🧭 How I Work:
          </h2>

          <div className="space-y-3">
            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs space-y-1">
              <h3 className="font-bold text-sm sm:text-base text-emerald-600 dark:text-emerald-400">
                1. Understand Before Building
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] font-medium leading-relaxed">
                Deep domain understanding and user friction analysis before writing code.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs space-y-1">
              <h3 className="font-bold text-sm sm:text-base text-emerald-600 dark:text-emerald-400">
                2. High Trust & Verification
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] font-medium leading-relaxed">
                In healthcare and education AI must be verifiable. I build systems with guardrails and human oversight.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-xs space-y-1">
              <h3 className="font-bold text-sm sm:text-base text-emerald-600 dark:text-emerald-400">
                3. Finish & Ship
              </h3>
              <p className="text-xs sm:text-sm text-[var(--text-muted)] font-medium leading-relaxed">
                Clean, deployed, production-ready software that delivers business leverage.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action (Ed Donner Style) */}
        <div className="rounded-3xl border border-emerald-500/40 bg-emerald-500/5 p-6 sm:p-8 space-y-3 text-center sm:text-left">
          <h3 className="text-lg sm:text-xl font-extrabold text-[var(--text-main)]">
            Looking for an AI Systems Architect to build custom software for your team or agency? Let’s talk!
          </h3>
          <p className="text-xs sm:text-sm text-[var(--text-muted)] font-medium leading-relaxed">
            Feel free to chat with my AI Digital Twin here, on this site or click Consult Arun to connect directly.
          </p>
        </div>

      </div>
    </div>
  );
};
