import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


class AssistaTrainingModel:
    """
    Memoire d'apprentissage soeur d'ASSISTA.

    Elle stocke les demonstrations donnees par l'utilisateur professeur:
    intention naturelle -> outil/kind -> cible/commande -> explication.
    ASSISTA l'injecte ensuite dans son contexte LLM pour mieux choisir les
    commandes PC adaptees.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    user_phrase TEXT NOT NULL,
                    normalized_phrase TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    target TEXT NOT NULL DEFAULT '',
                    command TEXT NOT NULL DEFAULT '',
                    explanation TEXT NOT NULL DEFAULT '',
                    meta_json TEXT NOT NULL DEFAULT '{}',
                    success_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_lessons_norm ON lessons(normalized_phrase);
                """
            )

    def learn(
        self,
        user_phrase: str,
        kind: str,
        target: str = "",
        command: str = "",
        explanation: str = "",
        meta: Optional[Dict] = None,
    ) -> Dict:
        phrase = (user_phrase or "").strip()
        kind = (kind or "").strip()
        if not phrase or not kind:
            return {"ok": False, "message": "Lecon incomplete: phrase et kind sont requis."}
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO lessons(
                    created_at, user_phrase, normalized_phrase, kind, target,
                    command, explanation, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _now(),
                    phrase,
                    _norm(phrase),
                    kind,
                    target or "",
                    command or "",
                    explanation or "",
                    json.dumps(meta or {}, ensure_ascii=False),
                ),
            )
        return {"ok": True, "id": int(cur.lastrowid), "message": f"Lecon ASSISTA_MODEL enregistree #{cur.lastrowid}."}

    def search(self, prompt: str, limit: int = 8) -> List[Dict]:
        q_words = set(_norm(prompt).split())
        if not q_words:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, user_phrase, normalized_phrase, kind, target, command,
                       explanation, meta_json, success_count
                FROM lessons
                ORDER BY id DESC
                LIMIT 200
                """
            ).fetchall()
        scored = []
        for row in rows:
            words = set(str(row["normalized_phrase"]).split())
            if not words:
                continue
            overlap = len(q_words & words)
            score = overlap / max(len(q_words | words), 1)
            if score > 0:
                item = dict(row)
                try:
                    item["meta"] = json.loads(item.pop("meta_json") or "{}")
                except Exception:
                    item["meta"] = {}
                item["score"] = round(score, 3)
                scored.append(item)
        scored.sort(key=lambda x: (x["score"], x.get("success_count", 0), x["id"]), reverse=True)
        return scored[:limit]

    def context_for_prompt(self, prompt: str, limit: int = 6) -> List[Dict]:
        return [
            {
                "user_phrase": item["user_phrase"],
                "kind": item["kind"],
                "target": item["target"],
                "command": item["command"],
                "explanation": item["explanation"],
                "score": item["score"],
            }
            for item in self.search(prompt, limit=limit)
        ]

    def stats(self) -> Dict:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM lessons").fetchone()
        return {"lessons": int(row["c"] if row else 0), "db_path": str(self.db_path)}
