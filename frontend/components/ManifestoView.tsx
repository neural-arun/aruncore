"use client";

import React from "react";
import Image from "next/image";

export const ManifestoView: React.FC = () => {
  return (
    <div className="h-full overflow-y-auto px-4 py-8 sm:px-12 pb-24 sm:pb-12 bg-[var(--bg-main)] text-[var(--text-main)]">
      <div className="mx-auto max-w-3xl space-y-6 animate-fade-slide">
        
        {/* Header Photo & Title */}
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

          <div className="space-y-2 text-center sm:text-left min-w-0 flex-1">
            <h1 className="font-heading text-3xl sm:text-4xl font-extrabold text-[var(--text-main)] tracking-tight">
              Arun Yadav
            </h1>
            <p className="text-base sm:text-lg font-bold text-emerald-600 dark:text-emerald-400">
              AI Systems Builder • Healthcare & Education
            </p>
          </div>
        </div>

        {/* Clean Continuous Paragraph Bio (Ed Donner Style) */}
        <div className="space-y-5 text-sm sm:text-base text-[var(--text-muted)] font-medium leading-relaxed">
          <p>
            I am <strong className="text-[var(--text-main)] font-bold">Arun Yadav</strong>, an AI Systems Builder engineering trust, production-grade software. I specialize in designing systems that combine AI, robust backend architecture, and domain expertise to solve high-stakes problems in <strong className="text-emerald-600 dark:text-emerald-400 font-bold">Healthcare and Education</strong>.
          </p>

          <p>
            Over the past few years, I’ve built complete, production-ready systems — from zero-hallucination RAG engines to clinical AI tutors and automated workflow pipelines. Some of my key highlighted projects include <strong className="text-[var(--text-main)] font-bold">ArunCore</strong> (a hybrid RAG engine combining ChromaDB vector search, BM25 keyword matching, and Cohere reranking), <strong className="text-[var(--text-main)] font-bold">NEET Medical Bot</strong> (an AI practice & diagnostic ecosystem for medical entrance exams with 10,000+ NCERT questions, spaced repetition, and solution breakdowns), <strong className="text-[var(--text-main)] font-bold">MedCoach</strong> (a reasoning AI tutor and diagnostic workflow assistant built with guardrails & execution traces), and <strong className="text-[var(--text-main)] font-bold">AI Note / Legal RAG</strong> (automated structured note generation and Indian legal document retrieval pipelines).
          </p>

          <p>
            My engineering approach is simple: I always understand the domain deeply and analyze user friction before writing a single line of code. In healthcare and education, AI must be verifiable, so I build systems with strict guardrails and human oversight. Most importantly, I focus on finishing and shipping clean, deployed software that delivers real business leverage.
          </p>

          <div className="pt-4 border-t border-[var(--border-subtle)]">
            <p className="text-sm sm:text-base font-semibold text-[var(--text-main)]">
              Looking for an AI Systems Architect to build custom software for your team or agency? Let’s talk! Feel free to chat with my <strong className="text-emerald-600 dark:text-emerald-400">AI Digital Twin</strong> here on this site, or click <strong className="text-emerald-600 dark:text-emerald-400">Consult Arun</strong> to connect directly.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
