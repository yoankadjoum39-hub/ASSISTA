import json
import os
import sqlite3
import threading
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AssistaSQLiteStore:
    def __init__(self, db_path: Path, memory_json_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path)
        self.memory_json_path = Path(memory_json_path) if memory_json_path else None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()
        self._migrate_legacy_memory()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    user_text TEXT NOT NULL,
                    assistant_text TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'ui'
                );
                CREATE TABLE IF NOT EXISTS action_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    target TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS routines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS routine_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    routine_id INTEGER NOT NULL,
                    ts TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    FOREIGN KEY(routine_id) REFERENCES routines(id)
                );
                CREATE TABLE IF NOT EXISTS pc_scan_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    scanned_dirs INTEGER NOT NULL DEFAULT 0,
                    scanned_files INTEGER NOT NULL DEFAULT 0,
                    notes_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS pc_scan_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    root_label TEXT NOT NULL,
                    path TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL DEFAULT 0,
                    ext TEXT NOT NULL DEFAULT '',
                    depth INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(run_id) REFERENCES pc_scan_runs(id)
                );
                CREATE TABLE IF NOT EXISTS agents (
                    key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    mission TEXT NOT NULL,
                    capabilities_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    text_value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    agent_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS security_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                """
            )

    def _migrate_legacy_memory(self) -> None:
        if not self.memory_json_path or not self.memory_json_path.exists():
            return
        if self.get_fact_count() or self.get_turn_count():
            return
        try:
            payload = json.loads(self.memory_json_path.read_text(encoding="utf-8"))
        except Exception:
            return
        for fact in payload.get("facts", []):
            self.add_fact(str(fact))
        for turn in payload.get("turns", []):
            self.remember_turn(turn.get("user", ""), turn.get("assistant", ""), turn.get("ts"))

    def save_preference(self, key: str, value) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO preferences(key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json=excluded.value_json,
                    updated_at=excluded.updated_at
                """,
                (key, json.dumps(value, ensure_ascii=False), now_iso()),
            )

    def load_preference(self, key: str, default=None):
        with self._connect() as conn:
            row = conn.execute("SELECT value_json FROM preferences WHERE key=?", (key,)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row["value_json"])
        except Exception:
            return default

    def add_fact(self, fact: str, limit: int = 50) -> None:
        fact = (fact or "").strip()
        if not fact:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO memory_facts(fact, created_at) VALUES (?, ?)",
                (fact, now_iso()),
            )
            rows = conn.execute("SELECT id FROM memory_facts ORDER BY id DESC").fetchall()
            for row in rows[limit:]:
                conn.execute("DELETE FROM memory_facts WHERE id=?", (row["id"],))

    def get_facts(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT fact FROM memory_facts ORDER BY id DESC").fetchall()
        return [row["fact"] for row in reversed(rows)]

    def get_fact_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM memory_facts").fetchone()
        return int(row["c"] if row else 0)

    def remember_turn(self, user_text: str, assistant_text: str, ts: Optional[str] = None, limit: int = 30) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO memory_turns(ts, user_text, assistant_text) VALUES (?, ?, ?)",
                (ts or now_iso(), user_text, assistant_text),
            )
            rows = conn.execute("SELECT id FROM memory_turns ORDER BY id DESC").fetchall()
            for row in rows[limit:]:
                conn.execute("DELETE FROM memory_turns WHERE id=?", (row["id"],))

    def get_recent_turns(self, limit: int = 10) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ts, user_text, assistant_text FROM memory_turns ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"ts": row["ts"], "user": row["user_text"], "assistant": row["assistant_text"]}
            for row in reversed(rows)
        ]

    def get_turn_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM memory_turns").fetchone()
        return int(row["c"] if row else 0)

    def forget_all_memory(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM memory_facts")
            conn.execute("DELETE FROM memory_turns")

    def append_message(self, role: str, text: str, source: str = "ui") -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO conversation_messages(ts, role, text, source) VALUES (?, ?, ?, ?)",
                (now_iso(), role, text, source),
            )

    def load_history(self, limit: int = 40) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ts, role, text FROM conversation_messages ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"ts": row["ts"], "role": row["role"], "text": row["text"]} for row in reversed(rows)]

    def log_action(self, kind: str, title: str, target: str, risk: str, status: str, message: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO action_log(ts, kind, title, target, risk, status, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (now_iso(), kind, title, target, risk, status, message),
            )

    def add_routine(self, name: str, schedule: str, payload: Dict, status: str = "active") -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO routines(name, schedule, payload_json, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, schedule, json.dumps(payload, ensure_ascii=False), status, now_iso()),
            )
            return int(cur.lastrowid)

    def list_routines(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, schedule, payload_json, status, created_at FROM routines ORDER BY id DESC"
            ).fetchall()
        result = []
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except Exception:
                payload = {}
            result.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "schedule": row["schedule"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "payload": payload,
                }
            )
        return result

    def log_routine_run(self, routine_id: int, status: str, message: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO routine_runs(routine_id, ts, status, message) VALUES (?, ?, ?, ?)",
                (routine_id, now_iso(), status, message[:4000]),
            )

    def get_recent_routine_runs(self, limit: int = 20) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT rr.id, rr.routine_id, rr.ts, rr.status, rr.message, r.name
                FROM routine_runs rr
                LEFT JOIN routines r ON r.id = rr.routine_id
                ORDER BY rr.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "routine_id": row["routine_id"],
                "name": row["name"] or f"Routine {row['routine_id']}",
                "ts": row["ts"],
                "status": row["status"],
                "message": row["message"],
            }
            for row in rows
        ]

    def replace_agents(self, agents: List[Dict]) -> None:
        with self._lock, self._connect() as conn:
            for agent in agents:
                conn.execute(
                    """
                    INSERT INTO agents(key, name, mission, capabilities_json, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        name=excluded.name,
                        mission=excluded.mission,
                        capabilities_json=excluded.capabilities_json,
                        updated_at=excluded.updated_at
                    """,
                    (
                        agent["key"],
                        agent["name"],
                        agent["mission"],
                        json.dumps(agent.get("capabilities", []), ensure_ascii=False),
                        now_iso(),
                    ),
                )

    def list_agents(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT key, name, mission, capabilities_json, updated_at FROM agents ORDER BY key"
            ).fetchall()
        result = []
        for row in rows:
            try:
                capabilities = json.loads(row["capabilities_json"])
            except Exception:
                capabilities = []
            result.append(
                {
                    "key": row["key"],
                    "name": row["name"],
                    "mission": row["mission"],
                    "capabilities": capabilities,
                    "updated_at": row["updated_at"],
                }
            )
        return result

    def start_agent_session(self, agent_key: str, title: str, status: str, details: Dict) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO agent_sessions(ts, agent_key, title, status, details_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (now_iso(), agent_key, title, status, json.dumps(details, ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def list_agent_sessions(self, limit: int = 20) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, ts, agent_key, title, status, details_json FROM agent_sessions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result = []
        for row in rows:
            try:
                details = json.loads(row["details_json"])
            except Exception:
                details = {}
            result.append(
                {
                    "id": row["id"],
                    "ts": row["ts"],
                    "agent_key": row["agent_key"],
                    "title": row["title"],
                    "status": row["status"],
                    "details": details,
                }
            )
        return result

    def save_security_audit(self, severity: str, summary: str, payload: Dict) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO security_audits(ts, severity, summary, payload_json) VALUES (?, ?, ?, ?)",
                (now_iso(), severity, summary, json.dumps(payload, ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def get_latest_security_audit(self) -> Dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, ts, severity, summary, payload_json FROM security_audits ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if not row:
            return {}
        try:
            payload = json.loads(row["payload_json"])
        except Exception:
            payload = {}
        return {
            "id": row["id"],
            "ts": row["ts"],
            "severity": row["severity"],
            "summary": row["summary"],
            "payload": payload,
        }

    def get_recent_actions(self, limit: int = 30) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ts, kind, title, target, risk, status, message FROM action_log ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def begin_scan_run(self, notes: Dict) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO pc_scan_runs(started_at, status, notes_json) VALUES (?, ?, ?)",
                (now_iso(), "running", json.dumps(notes, ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def finish_scan_run(self, run_id: int, status: str, scanned_dirs: int, scanned_files: int, notes: Dict) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE pc_scan_runs
                SET finished_at=?, status=?, scanned_dirs=?, scanned_files=?, notes_json=?
                WHERE id=?
                """,
                (now_iso(), status, scanned_dirs, scanned_files, json.dumps(notes, ensure_ascii=False), run_id),
            )

    def store_scan_entries(self, run_id: int, entries: List[Dict]) -> None:
        if not entries:
            return
        with self._lock, self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO pc_scan_entries(run_id, root_label, path, item_type, size_bytes, ext, depth)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        entry["root_label"],
                        entry["path"],
                        entry["item_type"],
                        int(entry.get("size_bytes", 0)),
                        entry.get("ext", ""),
                        int(entry.get("depth", 0)),
                    )
                    for entry in entries
                ],
            )

    def get_latest_scan_summary(self) -> Dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM pc_scan_runs ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if not row:
            return {"available": False}
        try:
            notes = json.loads(row["notes_json"] or "{}")
        except Exception:
            notes = {}
        return {
            "available": True,
            "run_id": row["id"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "status": row["status"],
            "scanned_dirs": row["scanned_dirs"],
            "scanned_files": row["scanned_files"],
            "notes": notes,
        }

    def add_clipboard_entry(self, text_value: str) -> None:
        text_value = (text_value or "").strip()
        if not text_value:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO clipboard_history(ts, text_value) VALUES (?, ?)",
                (now_iso(), text_value[:8000]),
            )

    def get_clipboard_history(self, limit: int = 20) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ts, text_value FROM clipboard_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"ts": row["ts"], "text": row["text_value"]} for row in rows]

    def get_stats(self) -> Dict:
        with self._connect() as conn:
            tables = {
                "facts": "memory_facts",
                "turns": "memory_turns",
                "messages": "conversation_messages",
                "actions": "action_log",
                "routines": "routines",
                "routine_runs": "routine_runs",
                "agents": "agents",
                "agent_sessions": "agent_sessions",
                "clipboard": "clipboard_history",
                "security_audits": "security_audits",
            }
            stats = {}
            for key, table in tables.items():
                row = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
                stats[key] = int(row["c"] if row else 0)
        stats["db_path"] = str(self.db_path)
        return stats


class AssistaAgentDirectory:
    DEFAULT_AGENTS = [
        {"key": "files", "name": "Agent Fichiers", "mission": "Cartographier, chercher, lire et organiser les fichiers.", "capabilities": ["list_dir", "search_files", "search_file_content", "read_file", "create_text_file", "move_file", "copy_file"]},
        {"key": "dev", "name": "Agent Dev", "mission": "Comprendre le code, préparer des commandes de build, git et installation.", "capabilities": ["read_file", "run_shell", "git", "install_package"]},
        {"key": "network", "name": "Agent Réseau", "mission": "Observer la connectivité, les ports et les diagnostics réseau.", "capabilities": ["network_scan", "system_info", "list_processes"]},
        {"key": "system", "name": "Agent Système", "mission": "Observer l'état du PC, les processus et les applications.", "capabilities": ["system_info", "list_processes", "kill_process", "open_app"]},
        {"key": "automation", "name": "Agent Automatisation", "mission": "Préparer et mémoriser des routines et actions répétitives.", "capabilities": ["schedule", "run_shell", "create_text_file"]},
        {"key": "web", "name": "Agent Web", "mission": "Ouvrir le web, suivre les liens et préparer des actions navigateur.", "capabilities": ["open_url", "capture_screen", "analyze_screen"]},
        {"key": "clipboard", "name": "Agent Clipboard", "mission": "Lire, écrire et historiser le presse-papiers.", "capabilities": ["clipboard_read", "clipboard_write"]},
        {"key": "notifications", "name": "Agent Notifications", "mission": "Remonter des alertes et confirmations visibles.", "capabilities": ["notify", "speak_text"]},
        {"key": "planner", "name": "Agent Planificateur", "mission": "Structurer les plans multi-étapes et les routines persistées.", "capabilities": ["context", "schedule", "system_info"]},
        {"key": "security", "name": "Agent Sécurité", "mission": "Surveiller les risques d'actions et diagnostics sensibles.", "capabilities": ["network_scan", "kill_process", "run_shell"]},
    ]

    def __init__(self, store: AssistaSQLiteStore) -> None:
        self.store = store
        self.store.replace_agents(self.DEFAULT_AGENTS)

    def all(self) -> List[Dict]:
        return self.store.list_agents()


class AssistaPCMapper:
    EXCLUDED_DIRS = {
        ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
        ".mypy_cache", ".pytest_cache", ".idea", ".vscode", "dist", "build",
        "generated", "aria-generated", "site-packages",
    }

    def __init__(self, store: AssistaSQLiteStore, roots: List[Dict], max_entries: int = 15000) -> None:
        self.store = store
        self.roots = roots
        self.max_entries = max_entries
        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._status = {
            "running": False,
            "started_at": "",
            "finished_at": "",
            "message": "Mapper inactif",
            "progress_percent": 0,
            "scanned_dirs": 0,
            "scanned_files": 0,
            "current_root": "",
            "current_path": "",
        }

    def configure(self, roots: Optional[List[Dict]] = None, max_entries: Optional[int] = None) -> None:
        with self._lock:
            if roots is not None:
                self.roots = roots
            if max_entries is not None:
                self.max_entries = max(100, int(max_entries))

    def start(self, force: bool = False) -> Dict:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return self.status()
            if not force:
                latest = self.store.get_latest_scan_summary()
                if latest.get("available") and latest.get("status") == "done":
                    self._status.update(
                        {
                            "running": False,
                            "started_at": latest.get("started_at", ""),
                            "finished_at": latest.get("finished_at", ""),
                            "message": "Dernière cartographie réutilisée",
                            "progress_percent": 100,
                        }
                    )
                    return self.status()
            self._status.update(
                {
                    "running": True,
                    "started_at": now_iso(),
                    "finished_at": "",
                    "message": "Cartographie du PC en cours",
                    "progress_percent": 1,
                    "scanned_dirs": 0,
                    "scanned_files": 0,
                    "current_root": "",
                    "current_path": "",
                }
            )
            self._thread = threading.Thread(target=self._scan_worker, daemon=True)
            self._thread.start()
            return self.status()

    def status(self) -> Dict:
        with self._lock:
            status = dict(self._status)
        status["last_scan"] = self.store.get_latest_scan_summary()
        return status

    def _scan_worker(self) -> None:
        roots = [root for root in self.roots if root.get("exists") == "yes"]
        notes = {"roots": roots, "excluded_dirs": sorted(self.EXCLUDED_DIRS)}
        run_id = self.store.begin_scan_run(notes)
        scanned_dirs = 0
        scanned_files = 0
        entries: List[Dict] = []
        extension_counter: Counter = Counter()
        max_entries = self.max_entries
        try:
            total_roots = max(1, len(roots))
            for root_index, root in enumerate(roots, start=1):
                root_path = Path(root["path"])
                if not root_path.exists():
                    continue
                with self._lock:
                    self._status["current_root"] = root["label"]
                for current, dirnames, filenames in os.walk(root_path):
                    dirnames[:] = [d for d in dirnames if d.lower() not in self.EXCLUDED_DIRS]
                    current_path = Path(current)
                    rel_depth = max(0, len(current_path.parts) - len(root_path.parts))
                    with self._lock:
                        self._status["current_path"] = str(current_path)
                    entries.append(
                        {
                            "root_label": root["label"],
                            "path": str(current_path),
                            "item_type": "dir",
                            "size_bytes": 0,
                            "ext": "",
                            "depth": rel_depth,
                        }
                    )
                    scanned_dirs += 1
                    if scanned_dirs % 10 == 0 or scanned_files % 50 == 0:
                        with self._lock:
                            root_progress = (root_index - 1) / total_roots
                            inner_bonus = min(0.9 / total_roots, (scanned_dirs + scanned_files) / max_entries / total_roots)
                            progress = min(95, int((root_progress + inner_bonus) * 100))
                            self._status.update(
                                {
                                    "progress_percent": max(progress, 1),
                                    "scanned_dirs": scanned_dirs,
                                    "scanned_files": scanned_files,
                                    "message": f"Scan {root['label']} — {scanned_files} fichiers / {scanned_dirs} dossiers",
                                }
                            )
                    if len(entries) >= max_entries:
                        break
                    for filename in filenames:
                        if len(entries) >= max_entries:
                            break
                        file_path = current_path / filename
                        try:
                            stat = file_path.stat()
                        except Exception:
                            continue
                        ext = file_path.suffix.lower()
                        extension_counter[ext or "<none>"] += 1
                        entries.append(
                            {
                                "root_label": root["label"],
                                "path": str(file_path),
                                "item_type": "file",
                                "size_bytes": int(stat.st_size),
                                "ext": ext,
                                "depth": rel_depth + 1,
                            }
                        )
                        scanned_files += 1
                    if len(entries) >= max_entries:
                        break
                if len(entries) >= max_entries:
                    break
            self.store.store_scan_entries(run_id, entries)
            top_ext = [{"ext": ext, "count": count} for ext, count in extension_counter.most_common(12)]
            notes = {
                "roots": roots,
                "top_extensions": top_ext,
                "entry_cap_reached": len(entries) >= max_entries,
            }
            self.store.finish_scan_run(run_id, "done", scanned_dirs, scanned_files, notes)
            with self._lock:
                self._status.update(
                    {
                        "running": False,
                        "finished_at": now_iso(),
                        "message": f"Cartographie terminée ({scanned_files} fichiers, {scanned_dirs} dossiers)",
                        "progress_percent": 100,
                        "scanned_dirs": scanned_dirs,
                        "scanned_files": scanned_files,
                    }
                )
        except Exception as exc:
            self.store.finish_scan_run(run_id, "error", scanned_dirs, scanned_files, {"error": str(exc)})
            with self._lock:
                self._status.update(
                    {
                        "running": False,
                        "finished_at": now_iso(),
                        "message": f"Erreur mapper: {exc}",
                        "progress_percent": 0,
                        "scanned_dirs": scanned_dirs,
                        "scanned_files": scanned_files,
                    }
                )
