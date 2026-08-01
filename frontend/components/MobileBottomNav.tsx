"use client";

import React from "react";
import { ActiveTab } from "../lib/types";
import { Bot, FolderGit2, User, PhoneCall } from "lucide-react";

interface MobileBottomNavProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  openHandoffModal: () => void;
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  activeTab,
  setActiveTab,
  openHandoffModal,
}) => {
  const tabs = [
    {
      id: "chat" as ActiveTab,
      label: "AI Assistant",
      icon: <Bot className="h-5 w-5" />,
    },
    {
      id: "projects" as ActiveTab,
      label: "Projects",
      icon: <FolderGit2 className="h-5 w-5" />,
    },
    {
      id: "manifesto" as ActiveTab,
      label: "About",
      icon: <User className="h-5 w-5" />,
    },
  ];

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-[var(--bg-sidebar)]/95 backdrop-blur-xl border-t border-[var(--border-subtle)] px-2 py-1.5 shadow-2xl transition-colors duration-200">
      <div className="flex items-center justify-around max-w-md mx-auto">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all touch-manipulation min-w-[64px] ${
                isActive
                  ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-extrabold scale-105"
                  : "text-[var(--text-dim)] hover:text-[var(--text-main)] font-medium"
              }`}
            >
              <div className={isActive ? "text-emerald-600 dark:text-emerald-400" : ""}>
                {tab.icon}
              </div>
              <span className="text-[10px] tracking-tight leading-tight mt-0.5 font-bold">
                {tab.label}
              </span>
            </button>
          );
        })}

        {/* Contact Handoff Trigger Tab */}
        <button
          onClick={openHandoffModal}
          className="flex flex-col items-center justify-center py-1 px-3 rounded-xl text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 font-bold transition-all touch-manipulation min-w-[64px]"
        >
          <div className="p-1 rounded-lg bg-emerald-500 text-white shadow-xs">
            <PhoneCall className="h-4 w-4" />
          </div>
          <span className="text-[10px] tracking-tight leading-tight mt-0.5 font-extrabold">
            Contact
          </span>
        </button>
      </div>
    </div>
  );
};
