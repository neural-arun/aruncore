"""Knowledge retrieval layer of the ArunCore digital twin.

Owns every read against the on-disk knowledge base:

* `data/github/<repo>/README.md` historical READMEs
* `data/linkedin/posts.md` scraped posts
* `data/static/*.md` profile, rules of engagement
* `data/raw/personal_background.md`
* `data/raw/unknown_questions.json` verified Q&A pairs

It also handles live GitHub lookups and persists newly learned Q&A pairs
(the active-learning feedback loop).
"""
import os
import re
import json
import datetime
import subprocess
from typing import Dict, Any, List, Optional, Tuple

import requests

from backend.app.services.notification_service import safe_truncate, schedule_notify_arun


def _project_root() -> str:
    """profile/ (the repository root holding `data/` and `backend/`)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# ------------------------------------------------------------------ #
# Chunking + relevance scoring helpers                                #
# ------------------------------------------------------------------ #
_QUERY_STOP_WORDS = {
    "how", "does", "the", "a", "an", "is", "for", "to", "of", "with", "work",
    "what", "tell", "me", "about", "can", "you", "who", "where", "why", "arun",
    "and", "or", "that", "this", "it", "in", "on", "at", "your", "my", "i", "we",
}

_BOILERPLATE_LINE_RE = re.compile(
    r"^(>\s*\*\*GitHub Repository:|\*\*Primary Language:|>\s*\*\*Primary Language:|"
    r">\s*\*\*Description:|>\s*\*\*Stars:|\*\*GitHub|#\s+[\w_-]+\s*$)"
)


def _query_terms(cleaned_query: str) -> List[str]:
    """Significant query words (stopwords removed, len>2)."""

    def _tok(w: str) -> str:
        return w.strip("?.,!;:'\"()[]{}")

    return [
        _tok(w) for w in cleaned_query.split()
        if _tok(w) and _tok(w).lower() not in _QUERY_STOP_WORDS and len(_tok(w)) > 2
    ]


def _relevance(score: int, alpha: float = 1.0) -> float:
    """Normalize a raw hit count into a 0..˜2 ordering score."""
    return alpha * (1.0 + min(score, 6))


def _term_hits(text: str, terms: List[str]) -> int:
    """Count word-boundary, case-insensitive term occurrences."""
    if not terms or not text:
        return 0
    lowered = text.lower()
    hits = 0
    for term in terms:
        hits += len(re.findall(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered))
    return hits


def _term_score(heading: str, body: str, terms: List[str]) -> int:
    """Weighted relevance: heading hits count double body hits."""
    if not terms:
        return 0
    return 2 * _term_hits(heading, terms) + _term_hits(body, terms)


def _score_term_streak(text: str, terms: List[str]) -> int:
    """Consecutive-significant-term density bonus (e.g. 'clinical reasoning tutor')."""
    if not terms or not text:
        return 0
    lowered = text.lower()
    streak = 0
    best = 0
    words = re.findall(r"[a-z0-9]+", lowered)
    term_set_low = {t.lower() for t in terms}
    for w in words:
        if w in term_set_low:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return 2 * best + _term_hits(text, terms)


def _clean_readme(content: str) -> str:
    """Strip YAML frontmatter + GitHub API boilerplate blockquote lines."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]
    out = []
    for line in content.splitlines():
        stripped = line.strip()
        if _BOILERPLATE_LINE_RE.match(stripped):
            continue
        if stripped.startswith("> **GitHub Repository:") or stripped.startswith("> **Primary Language:") or stripped.startswith(">-"):
            continue
        out.append(line)
    return "\n".join(out)


def _score_readme_sections(content: str, terms: List[str], max_chars: int = 1800) -> List[Tuple[str, str, int]]:
    """Split a project README into heading-level chunks, scored by query hits.

    Returns (heading, body, score) triples sorted best-first (score desc).
    """
    cleaned = _clean_readme(content)
    sections: List[Tuple[str, str]] = []
    cur_heading: Optional[str] = None
    cur_body: List[str] = []

    def _flush() -> None:
        nonlocal cur_body
        body = "\n".join(cur_body).strip()
        cur_body = []
        if body:
            sections.append((cur_heading or "Overview", body))

    for line in cleaned.splitlines():
        if re.match(r"^#{1,4} ", line):
            _flush()
            cur_heading = re.sub(r"^#{1,4} ", "", line).strip()
        else:
            cur_body.append(line)
    _flush()

    scored = []
    for heading, body in sections:
        if not body:
            continue
        score = _term_score(heading, body, terms)
        if score > 0:
            truncated = body[:max_chars].rstrip()
            if len(body) > max_chars:
                truncated += "..."
            scored.append((heading, truncated, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored


def _score_profile_sections(content: str, terms: List[str], max_chars: int = 1200) -> List[Tuple[str, str, int]]:
    """Split a profile / background doc into heading-level chunks, scored."""
    sections: List[Tuple[str, str]] = []
    current_heading = ""
    cur: List[str] = []

    def _flush() -> None:
        nonlocal cur
        body = "\n".join(cur).strip()
        cur = []
        if body:
            sections.append((current_heading, body))

    for line in content.splitlines():
        if re.match(r"^#{1,3} ", line):
            _flush()
            current_heading = line.lstrip("# ").strip()
        elif line.strip() == "---":
            _flush()
        else:
            cur.append(line)
    _flush()

    scored = []
    for heading, body in sections:
        if not body.strip():
            continue
        score = _score_term_streak(heading + "\n" + body, terms)
        if score > 0:
            truncated = body[:max_chars].rstrip()
            if len(body) > max_chars:
                truncated += "..."
            scored.append((f"### {heading}", truncated, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored


def _clean_linkedin_posts(posts_text: str) -> List[str]:
    """Strip YAML/meta boilerplate and without params, return bare post bodies."""
    if posts_text.startswith("---"):
        parts = posts_text.split("---", 2)
        if len(parts) >= 3:
            posts_text = parts[2]
    posts = []
    for block in re.split(r"(?m)^## ", posts_text):
        block = block.strip()
        if not block:
            continue
        lines: List[str] = []
        for line in block.splitlines():
            ls = line.strip()
            if ls.startswith("**Date:") or ls.startswith("**Post Title") or ls.startswith("> **Link:"):
                continue
            lines.append(line)
        body = "\n".join(lines).strip()
        if body:
            posts.append("# " + body)
    return posts


class KnowledgeService:
    """Single responsibility: every read/write against Arun's knowledge data."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir or _project_root()
        self.data_dir = os.path.join(self.root_dir, "data")

    # ------------------------------------------------------------------ #
    # Static persona documents (2-tuple used by the legacy API layer)     #
    # ------------------------------------------------------------------ #
    def load_static_profile_and_rules(self) -> Tuple[str, str]:
        profile_content = ""
        rules_content = ""

        profile_path = os.path.join(self.data_dir, "static", "public_profile.md")
        rules_path = os.path.join(self.data_dir, "static", "rules_of_engagement.md")

        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_content = f.read()

        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_content = f.read()

        return profile_content, rules_content

    # ------------------------------------------------------------------ #
    # GitHub live data
    # ------------------------------------------------------------------ #
    def fetch_live_github(self, username: str = "neural-arun") -> str:
        try:
            res = requests.get(
                f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
                timeout=5,
            )
            if res.status_code == 200:
                repos = res.json()
                lines = [
                    f"• [{r['name']}]({r['html_url']}) - {r.get('description', 'No description')} (Updated: {r['updated_at'][:10]})"
                    for r in repos
                ]
                return "### Live GitHub Repositories:\n" + "\n".join(lines)
        except Exception as e:
            return f"GitHub fetch error: {e}"
        return "Could not fetch GitHub data."

    # ------------------------------------------------------------------ #
    # Free-form knowledge search (previously search_arun_knowledge)       #
    # ------------------------------------------------------------------ #
    def search(self, query: str) -> str:
        """Retrieve a compact, relevance-ranked set of knowledge chunks.

        Every source (project READMEs, LinkedIn posts, static profile docs,
        verified Q&A pairs) is split into heading-level chunks, the YAML/GitHub
        boilerplate is stripped, each chunk is scored against the query's
        significant terms, and only the best-scoring chunks are returned. The
        tool output is therefore a bounded set of *clean sections* instead of
        whole raw files.
        """
        data_dir = self.data_dir
        cleaned_query = (query or "").lower().replace("-", " ").replace("_", " ")
        query_terms = _query_terms(cleaned_query)

        project_aliases = {
            "med_coach": ["med_coach", "medcoach", "med coach", "medical tutor", "clinical reasoning", "clinical tutor"],
            "legal_RAG_system": ["legal_rag_system", "legal rag", "legal", "ipc", "indian penal code", "chunking"],
            "neet-bot": ["neet-bot", "neet bot", "neet 2027", "cbt simulator", "ncert", "mcq"],
            "real_state_listing_scraper": ["real_state_listing_scraper", "99acres", "cloudflare", "scraper", "real estate"],
            "ArunCore": ["aruncore", "profile", "assistant", "vector database", "reranking", "fastapi"],
        }

        matched_folders = []
        for folder_name, synonyms in project_aliases.items():
            if any(syn in cleaned_query for syn in synonyms):
                matched_folders.append(folder_name)

        results: List[Tuple[float, str]] = []

        # 1. PROJECT READMES -> section-level chunks, ranked by relevance.
        for folder in matched_folders:
            target_readme = os.path.join(data_dir, "github", folder, "README.md")
            if os.path.exists(target_readme):
                with open(target_readme, "r", encoding="utf-8") as f:
                    content = f.read()
                for heading, body, score in _score_readme_sections(content, query_terms):
                    if score > 0 and body:
                        block = f"## {heading}\n{body.strip()}"
                        results.append((_relevance(score), f"--- Project README ({folder}) ---\n{block}"))

        stop_words = {"how", "does", "the", "a", "an", "is", "for", "to", "of", "with", "work", "what", "tell", "me", "about", "can", "you", "who", "where", "why", "arun"}
        significant_words = [w.strip("?,.!") for w in cleaned_query.split() if w.strip("?,.!") not in stop_words and len(w) > 2]

        # 2. LINKEDIN POSTS: strip meta boilerplate, chunk per post, rank.
        posts_path = os.path.join(data_dir, "linkedin", "posts.md")
        if os.path.exists(posts_path):
            with open(posts_path, "r", encoding="utf-8") as f:
                posts_text = f.read()
            for post in _clean_linkedin_posts(posts_text):
                body = post.strip()
                if not body:
                    continue
                score = sum(1 for w in significant_words if w.lower() in body.lower())
                if score > 0 and query_terms:
                    results.append((_relevance(score, 0.8), f"--- Relevant LinkedIn Post ---\n{body[:2200]}"))

        # 3. CORE PROFILE & BACKGROUND DOCS: heading-level chunks, ranked.
        other_static_files = [
            os.path.join(data_dir, "static", "public_profile.md"),
            os.path.join(data_dir, "static", "rules_of_engagement.md"),
            os.path.join(data_dir, "raw", "personal_background.md"),
        ]
        static_hits: List[Tuple[str, str, float]] = []
        for s_file in other_static_files:
            if os.path.exists(s_file):
                with open(s_file, "r", encoding="utf-8") as f:
                    content = f.read()
                for heading, chunk, score in _score_profile_sections(content, query_terms):
                    if score > 0:
                        block = f"{heading}\n{chunk.strip()}"
                        if len(block.strip()) > 80:
                            static_hits.append((_relevance(score, 0.9), f"--- Document Insight ({os.path.basename(s_file)}) ---\n{block.strip()}"))
        results.extend(static_hits)

        # Domain fallback: "stack/tech/language/framework/tools" queries that
        # the lexical matcher missed still deserve the Technical Stack section.
        stack_terms = {"stack", "tech", "technology", "technologies", "language", "framework", "tool", "tools", "languages"}
        if static_hits and not any(
            "Technical Stack" in block for _, block in static_hits
        ) and any(t in stack_terms for t in query_terms):
            profile_path = os.path.join(data_dir, "static", "public_profile.md")
            if os.path.exists(profile_path):
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile_content = f.read()
                for heading, chunk, score in _score_profile_sections(profile_content, stack_terms):
                    if "Technical Stack" in heading:
                        block = f"{heading}\n{chunk.strip()}"
                        results.append((2.0, f"--- Document Insight (public_profile.md) ---\n{block}"))

        # 4. VERIFIED Q&A PAIRS from the active-learning store.
        unknown_questions_path = os.path.join(data_dir, "raw", "unknown_questions.json")
        if os.path.exists(unknown_questions_path):
            try:
                with open(unknown_questions_path, "r", encoding="utf-8") as f:
                    uq_data = json.load(f)
                    if isinstance(uq_data, list):
                        for item in uq_data:
                            q_item = item.get("question", "")
                            a_item = item.get("answer", "")
                            if any(w in q_item.lower() or w in a_item.lower() for w in significant_words):
                                results.append((0.6, f"--- Verified Q&A Pair ---\nQuestion: {q_item}\nAnswer: {a_item}"))
            except Exception as e:
                print(f"[UNKNOWN QUESTIONS READ ERROR] {e}")

        # Sort by relevance score, dedupe, cap the total payload.
        results.sort(key=lambda x: x[0], reverse=True)
        unique_results = []
        seen = set()
        payload_len = 0
        for _, block in results:
            block = block.strip()
            if block in seen:
                continue
            if len(block) > 3000:
                block = block[:3000].rstrip() + "..."
            if payload_len + len(block) > 9000:
                break
            unique_results.append(block)
            seen.add(block)
            payload_len += len(block) + 2

        if unique_results:
            return "\n\n".join(unique_results)

        # Run out of chunks -> auto-trigger notification
        schedule_notify_arun(
            "UNKNOWN_QUESTION",
            f"Unknown Question (No KB Match): {query}",
        )
        return (
            "No exact match found in knowledge base. Auto-triggered UNKNOWN_QUESTION alert to Arun's phone. "
            "YOU MUST CALL notify_arun AND ASK THE USER FOR THEIR CONTACT INFO (Name, Email, Phone/WhatsApp)."
        )

    # ------------------------------------------------------------------ #
    # Active learning: persist a verified Q&A and re-ingest into memory   #
    # ------------------------------------------------------------------ #
    def save_verified_answer(self, question: str, answer: str) -> str:
        """Writes an answered unknown question into data/raw/unknown_questions.json and triggers vector DB re-ingestion."""
        target_file = os.path.join(self.data_dir, "raw", "unknown_questions.json")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        now_iso = datetime.datetime.utcnow().isoformat() + "Z"

        entry = {
            "question": question.strip(),
            "answer": answer.strip(),
            "timestamp": now_iso,
        }

        existing = []
        if os.path.exists(target_file):
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = []
            except Exception:
                existing = []

        updated = False
        for item in existing:
            if item.get("question", "").lower() == question.strip().lower():
                item["answer"] = answer.strip()
                item["timestamp"] = now_iso
                updated = True
                break

        if not updated:
            existing.append(entry)

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        ingest_script = os.path.join(self.root_dir, "backend", "app", "core", "ingest.py")
        try:
            subprocess.Popen(["python3", ingest_script])
        except Exception as e:
            print(f"[REINGEST ERROR] {e}")

        return "SUCCESS: Saved to unknown_questions.json and ingested into memory."


knowledge_service = KnowledgeService()


def load_static_context() -> Tuple[str, str]:
    """Backward-compatible 2-tuple reader (profile, rules)."""
    return knowledge_service.load_static_profile_and_rules()