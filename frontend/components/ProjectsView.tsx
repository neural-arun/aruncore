"use client";

import React, { useState } from "react";
import { PROJECTS_DATA } from "../lib/projectsData";
import { ActiveTab } from "../lib/types";
import { ExternalLink, Search, Sparkles, ArrowRight } from "lucide-react";

const GithubIcon = () => (
  <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

interface ProjectsViewProps {
  onSelectPrompt: (prompt: string) => void;
  setActiveTab: (tab: ActiveTab) => void;
}

export const ProjectsView: React.FC<ProjectsViewProps> = ({
  onSelectPrompt,
  setActiveTab,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const categories = ["All", "Healthcare", "Education", "RAG & AI", "Agents & Tools", "Automation & Scraping"];

  const filteredProjects = PROJECTS_DATA.filter((project) => {
    const matchesCategory = selectedCategory === "All" || project.category === selectedCategory;
    const matchesSearch =
      project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.techStack.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleCardClick = (githubUrl: string) => {
    window.open(githubUrl, "_blank", "noopener,noreferrer");
  };

  const handleAskTwin = (e: React.MouseEvent, title: string, repoName: string) => {
    e.stopPropagation(); // Don't trigger GitHub redirect on button click
    const prompt = `Can you give me a comprehensive summary of the ${title} project (${repoName}) based on its repository README and technical architecture?`;
    onSelectPrompt(prompt);
    setActiveTab("chat");
  };

  return (
    <div className="h-full overflow-y-auto px-4 py-6 sm:py-8 sm:px-8">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[var(--text-main)] tracking-tight">
              Projects & Engineering Repositories
            </h1>
            <p className="text-sm sm:text-base text-[var(--text-muted)] mt-1.5 font-medium">
              Click any project card to view its live GitHub repository, or ask my AI Twin for a summary.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-3 h-4 w-4 text-[var(--text-dim)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search stack or project..."
              className="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] py-2.5 pl-9 pr-4 text-xs sm:text-sm text-[var(--text-main)] placeholder-[var(--text-dim)] focus:border-[var(--border-accent)] focus:outline-none"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-lg px-3.5 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
                selectedCategory === cat
                  ? "bg-[var(--accent-teal)] text-white shadow-sm"
                  : "bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface-hover)]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Project Cards */}
        <div className="space-y-5">
          {filteredProjects.map((proj) => (
            <div
              key={proj.id}
              onClick={() => handleCardClick(proj.githubUrl)}
              className="group cursor-pointer rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-6 transition-all hover:border-[var(--border-accent)] hover:bg-[var(--bg-surface-hover)] hover:shadow-xl"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-main)] px-2.5 py-0.5 font-mono text-xs font-semibold text-[var(--accent-amber)]">
                      {proj.category}
                    </span>
                  </div>
                  {/* Larger Title */}
                  <h3 className="font-heading text-xl sm:text-2xl font-bold text-[var(--text-main)] group-hover:text-[var(--accent-green)] transition-colors">
                    {proj.title}
                  </h3>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--text-muted)] group-hover:text-[var(--text-main)] transition-colors shrink-0">
                  <GithubIcon />
                  <span className="font-mono">{proj.name}</span>
                  <ExternalLink className="h-3.5 w-3.5 ml-1" />
                </div>
              </div>

              {/* Larger Description */}
              <p className="mt-3 text-sm sm:text-base text-[var(--text-muted)] leading-relaxed font-normal">
                {proj.description}
              </p>

              {/* Highlights */}
              <div className="mt-3.5 space-y-1">
                {proj.highlights.map((hl, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs sm:text-sm text-[var(--text-muted)]">
                    <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent-green)] shrink-0" />
                    <span>{hl}</span>
                  </div>
                ))}
              </div>

              {/* Footer Tech Badges & Ask Twin Button */}
              <div className="mt-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-t border-[var(--border-subtle)] pt-4">
                <div className="flex flex-wrap gap-1.5">
                  {proj.techStack.map((tech, tIdx) => (
                    <span
                      key={tIdx}
                      className="rounded-md bg-[var(--bg-main)] px-2.5 py-1 font-mono text-xs text-[var(--text-muted)] border border-[var(--border-subtle)]"
                    >
                      {tech}
                    </span>
                  ))}
                </div>

                {/* Ask Twin Summary Action */}
                <button
                  onClick={(e) => handleAskTwin(e, proj.title, proj.name)}
                  className="flex items-center gap-1.5 rounded-xl border border-[var(--border-accent)] bg-[var(--bg-surface-hover)] px-3.5 py-2 text-xs sm:text-sm font-bold text-[var(--accent-green)] transition-all hover:bg-[var(--accent-green)] hover:text-white shrink-0"
                  title="Ask Twin for a summary based on README"
                >
                  <Sparkles className="h-4 w-4" />
                  <span>Ask Assistant for Summary</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
