---
project_name: med_coach
github_url: https://github.com/neural-arun/med_coach
language: Python
stars: 0
topics: [None]
updated_at: 2026-06-16T18:29:39Z
---

# med_coach

> **GitHub Repository:** [https://github.com/neural-arun/med_coach](https://github.com/neural-arun/med_coach)  
> **Primary Language:** Python | **Stars:** 0 | **Forks:** 0  
> **Description:** AI Clinical Reasoning Tutor for medical students — trains diagnostic thinking through realistic, LLM-driven simulated patient encounters with graph-based evaluation and teaching.

---

# Medical Tutor (MedCoach)

An AI Clinical Reasoning Tutor where medical students practice diagnosing virtual patients through realistic clinical encounters. Most medical education tools evaluate whether the student got the diagnosis right — MedCoach evaluates **how they thought**.

## Goal

Train clinical reasoning using simulated patient interaction. Students learn by running a full diagnosis loop:

Student → Receives Case → Asks Questions → Builds Diagnosis → Gets Evaluation → Learns

## How a Practice Encounter Works

1. **Generate a patient case** — An LLM creates a unique patient with a history, symptoms, vitals, and a hidden diagnosis.
2. **Interview the patient** — Students ask questions naturally. The Patient Agent only reveals information that was actually asked and stays consistent with all previous answers throughout the encounter.
3. **Submit diagnosis + reasoning** — Students explain both the diagnosis and their clinical thinking.
4. **Get evaluated** — The Evaluator Agent scores the entire process out of 10, including question quality, missed history, reasoning gaps, cognitive bias, dangerous assumptions, and actionable feedback.
5. **Learn** — The Teacher Agent explains the disease, highlights the missed signals, and shows a stronger diagnostic approach.

## Architecture (LangGraph)

- **START → Evaluator → Teacher → Memory (SQLite) → END**
- Interactive patient conversations run **outside the graph** for real-time responsiveness.
- The flow separates **Thinking** (agents/schemas) from **Flow** (graph) from **Storage** (memory) from **Interface** (UI) as its core design principle.

## Roles / Agent Workflow

**Patient Agent** — role-plays the virtual patient; reveals only what is asked; keeps answers consistent.

**Evaluator Agent** — grades the student's whole reasoning process out of 10, focusing on how they think rather than just the final diagnosis label.

**Teacher Agent** — explains the underlying disease, points out missed clinical signals, and demonstrates the stronger diagnostic reasoning path.

## Project Layout

```
app/
agents/
graph/
schemas/
memory/
ui/
```

Separated by the core principle of keeping **Thinking / Flow / Storage / Interface** decoupled.

## Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Orchestration**: LangGraph
- **Storage**: SQLite (conversation + memory persistence)
- **Streaming responses**

## Status & Roadmap

- **V1 (current)**: Focused on simulated patient reasoning — the interactive diagnosis loop described above.
- **V2 (planned)**: Richer clinical workflows, external knowledge retrieval, and stronger diagnostic support.