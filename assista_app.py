import argparse
import os
import sys
import threading

import webview

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from nexus_core.auth import UserSession
from nexus_core.history_db import normalize_display_text
from assista.assista_logic import AssistaBrain
from assista.assista_ui import ASSISTA_HTML

RESTORE_HTML = normalize_display_text("""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:transparent;font-family:Segoe UI,sans-serif}
button{width:64px;height:64px;border-radius:18px;border:1px solid rgba(56,180,255,.45);background:rgba(4,10,16,.92);color:#38b4ff;font-weight:800;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,.38)}
button:hover{background:#38b4ff;color:#040a10}
</style></head><body><button title="Afficher ASSISTA" onclick="pywebview.api.restore_main()">ASSISTA</button></body></html>""")


class AssistaAPI:
    def __init__(self, app: "AssistaApp") -> None:
        self._app = app

    # ── Session ───────────────────────────────────────────────────────────
    def init_session(self):
        return self._app.brain.bootstrap()

    # ── Prompt ───────────────────────────────────────────────────────────
    def submit_prompt(self, prompt: str):
        return self._app.brain.submit(prompt)

    # ── Plan ─────────────────────────────────────────────────────────────
    def approve_plan(self, plan_id: str):
        return self._app.brain.approve_plan(plan_id)

    def reject_plan(self, plan_id: str):
        return self._app.brain.reject_plan(plan_id)

    # ── Contrôles ────────────────────────────────────────────────────────
    def set_autopilot(self, enabled: bool):
        return self._app.brain.set_autopilot(enabled)

    # ── Voix ─────────────────────────────────────────────────────────────
    def start_voice(self):
        return self._app.brain.start_voice()

    def stop_voice(self):
        return self._app.brain.stop_voice()

    def set_auto_speak(self, enabled: bool):
        return self._app.brain.set_auto_speak(enabled)

    def speak_last_response(self):
        return self._app.brain.speak_last_response()

    def stop_speaking(self):
        return self._app.brain.stop_speaking()

    # ── État ─────────────────────────────────────────────────────────────
    def get_state(self):
        return self._app.brain.get_state()

    def start_pc_mapper(self, force: bool = True):
        return self._app.brain.start_pc_mapper(full=force)

    def start_quick_scan(self):
        return self._app.brain.start_quick_scan()

    def get_db_stats(self):
        return self._app.brain.get_db_stats()

    def run_security_audit(self):
        return self._app.brain.run_security_audit()

    def get_ops_state(self):
        return self._app.brain.get_ops_state()

    # ── Config ───────────────────────────────────────────────────────────
    def get_config(self):
        return self._app.brain.get_config()

    def save_config(self, api_key: str, model: str, base_url: str):
        return self._app.brain.save_config(api_key, model, base_url)

    # ── Shell log ─────────────────────────────────────────────────────────
    def get_shell_log(self, n: int = 50):
        return self._app.brain.get_shell_log(n)

    # ── Mémoire ───────────────────────────────────────────────────────────
    def forget_memory(self):
        return self._app.brain.forget_memory()

    def get_memory(self):
        return self._app.brain.get_memory()

    # ── Analyse chemin local ──────────────────────────────────────────────
    def analyze_local_path(self, path: str):
        return self._app.brain.analyze_local_path(path)

    def teach_assista_model(self, user_phrase: str, kind: str, target: str = "", command: str = "", explanation: str = ""):
        return self._app.brain.teach_assista_model(user_phrase, kind, target, command, explanation)

    def set_teacher_mode(self, enabled: bool):
        return self._app.brain.set_teacher_mode(enabled)

    # ── Streaming JS polling ──────────────────────────────────────────────
    def poll_js(self):
        return self._app.brain.poll_js()

    def enter_hands_free(self):
        return self._app.enter_hands_free()

    def exit_hands_free(self):
        return self._app.exit_hands_free()

    def restore_main(self):
        return self._app.restore_main()


class AssistaApp:
    def __init__(self, session: UserSession) -> None:
        self.session = session
        self.brain   = AssistaBrain(session.display_name)
        self.api     = AssistaAPI(self)
        self.window  = webview.create_window(
            "ASSISTA",
            html=ASSISTA_HTML,
            width=1440,
            height=940,
            js_api=self.api,
            background_color="#040a10",
        )
        self.restore_window = webview.create_window(
            "ASSISTA - retour",
            html=RESTORE_HTML,
            width=84,
            height=84,
            x=20,
            y=20,
            frameless=True,
            on_top=True,
            hidden=True,
            js_api=self.api,
            background_color="#000000",
        )

    def _safe_call(self, fn) -> None:
        try:
            fn()
        except Exception:
            pass

    def enter_hands_free(self):
        self.brain.set_hands_free(True)
        self.brain.set_auto_speak(True)
        self.brain.start_voice()

        def _apply():
            self._safe_call(self.window.hide)
            self._safe_call(self.restore_window.show)

        threading.Timer(0.15, _apply).start()
        return self.brain.get_state()

    def exit_hands_free(self):
        self.brain.set_hands_free(False)
        return self.restore_main()

    def restore_main(self):
        self.brain.set_hands_free(False)

        def _apply():
            self._safe_call(self.window.show)
            self._safe_call(self.window.restore)
            self._safe_call(self.restore_window.hide)

        threading.Timer(0.05, _apply).start()
        return self.brain.get_state()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username",     default="invited")
    parser.add_argument("--display-name", default="Invite")
    parser.add_argument("--role",         default="simple")
    return parser.parse_args()


def main():
    args    = parse_args()
    session = UserSession(0, args.username, args.display_name, args.role, "")
    AssistaApp(session)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
