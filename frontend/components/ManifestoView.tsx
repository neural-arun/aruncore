"use client";

import React from "react";
import Image from "next/image";

export const ManifestoView: React.FC = () => {
  return (
    <div className="h-full overflow-y-auto px-4 py-6 sm:py-8 sm:px-8">
      <div className="mx-auto max-w-4xl space-y-8">
        {/* Profile Intro Card */}
        <div className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-6 sm:p-8 backdrop-blur-md shadow-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            <div className="h-20 w-20 overflow-hidden rounded-2xl border-2 border-[var(--border-accent)] bg-slate-800 shrink-0 shadow-md">
              <Image
                src="/profile_photo.png"
                alt="Arun Yadav"
                width={80}
                height={80}
                className="h-full w-full object-cover"
              />
            </div>
            <div className="space-y-1">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[var(--text-main)] tracking-tight">
                Arun Yadav
              </h1>
              <p className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                AI Systems Architect • Healthcare & Education
              </p>
              <p className="text-sm sm:text-base text-[var(--text-muted)] font-medium">
                I design AI software that people can trust I also work on RAG pipelines and automated workflows.
              </p>
            </div>
          </div>
        </div>

        {/* Quote Block */}
        <div className="rounded-xl border-l-4 border-[var(--accent-green)] bg-[var(--bg-surface)] p-5 shadow-sm">
          <p className="text-base sm:text-lg text-[var(--text-main)] leading-relaxed font-semibold">
            "I create AI-powered software systems for Healthcare and Education that organizations trust to make decisions, automate complex workflows and scale expertise."
          </p>
        </div>

        {/* Technical Skills & Expertise Section */}
        <section>
          <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-main)] border-b border-[var(--border-subtle)] pb-2 mb-4">
            Technical Skills & Core Stack
          </h2>
          <p className="text-sm sm:text-base text-[var(--text-muted)] mb-4 font-medium leading-relaxed">
            I have worked extensively across the AI software stack, building production pipelines, stateful agents, and reliable backend infrastructure:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Core Engineering</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                Python & FastAPI Backend
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I write clean, async Python code and engineer stateful backend microservices using FastAPI, Pydantic, and Uvicorn for low-latency streaming endpoints.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Retrieval Systems</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                Hybrid RAG Architecture
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I design zero-hallucination RAG pipelines combining dense vector embeddings (ChromaDB), keyword retrieval (BM25), and neural rerankers (Cohere V3).
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Agent Systems</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                Stateful Agentic Workflows
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I build autonomous multi-step AI agents equipped with tool calling, memory compression loops, and human-in-the-loop escalation guardrails.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Quality & Reliability</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                LLM Evaluation & Guardrails
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I set up rigorous LLM evaluation frameworks, safety verification layers, hallucination checks, and schema validation to ensure model outputs are accurate.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Protocol Standards</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                Model Context Protocol (MCP)
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I build custom MCP server integrations that allow AI systems to securely query local databases, inspect code repositories, and automate external APIs.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[var(--accent-amber)] uppercase tracking-wider">Infrastructure</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-[var(--accent-green)]">
                Monitoring & Telegram Alerts
              </h3>
              <p className="text-sm text-[var(--text-muted)] leading-relaxed font-normal">
                I build background event queues, automated lead handoffs, and instant Telegram alert channels to keep human operators informed in real time.
              </p>
            </div>
          </div>
        </section>

        {/* Bio Essay */}
        <div className="space-y-8">
          <section>
            <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-main)] border-b border-[var(--border-subtle)] pb-2 mb-3">
              My Engineering Approach
            </h2>
            <p className="text-base sm:text-lg text-[var(--text-muted)] leading-relaxed font-normal">
              Most people just build a chatbot and stop there. But I build software systems. I combine AI models, data pipelines, verification layers, human oversight and reliable infrastructure to make sure everything works well.
            </p>
          </section>

          <section>
            <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-main)] border-b border-[var(--border-subtle)] pb-2 mb-4">
              Core Operating Principles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-2">
                <h3 className="text-base sm:text-lg font-bold text-[var(--accent-amber)]">
                  1. I Look At Problems
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
                  I start by looking at real problems in healthcare and education problems that cost a lot of money rather than just following the latest trend.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-2">
                <h3 className="text-base sm:text-lg font-bold text-[var(--accent-amber)]">
                  2. Trust Is More Important Than Hype
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
                  Healthcare and education need systems that're reliable. So every system I build includes verification, guardrails and human oversight to make sure everything is safe and trustworthy.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-2">
                <h3 className="text-base sm:text-lg font-bold text-[var(--accent-amber)]">
                  3. I Build Complete Products
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
                  Software is only useful if people actually use it. That means I have to think about infrastructure, security and user experience not the AI model.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm space-y-2">
                <h3 className="text-base sm:text-lg font-bold text-[var(--accent-amber)]">
                  4. I Ship, Learn, And Improve
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
                  When I release my software to users I get feedback faster than if I just planned everything out for months without showing it to anyone.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-main)] border-b border-[var(--border-subtle)] pb-2 mb-4">
              Primary Focus Sectors
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm">
                <h3 className="text-lg font-bold text-[var(--text-main)]">
                  Healthcare Systems
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] mt-2 leading-relaxed">
                  I work on reducing tasks for doctors organizing medical knowledge and automating clinical workflows.
                </p>
              </div>

              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-5 shadow-sm">
                <h3 className="text-lg font-bold text-[var(--text-main)]">
                  Medical & Professional Education
                </h3>
                <p className="text-sm sm:text-base text-[var(--text-muted)] mt-2 leading-relaxed">
                  I create personalized learning tools, question generators and trusted search engines, for institutions and students so they can learn better.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
