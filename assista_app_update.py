import argparse
import os
import sys

import webview

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from nexus_core.auth import UserSession
from assista.assista_logic import AssistaBrain
from assista.assista_ui import ASSISTA_HTML


class AssistaAPI:
    def __init__(self, app: "AssistaApp") -> None:
        self.app = app

    # ── Session ───────────────────────────────────────────────────────────
    def init_session(self):
        return self.app.brain.bootstrap()

    # ── Prompt ───────────────────────────────────────────────────────────
    def submit_prompt(self, prompt: str):
        return self.app.brain.submit(prompt)

    # ── Plan ─────────────────────────────────────────────────────────────
    def approve_plan(self, plan_id: str):
        return self.app.brain.approve_plan(plan_id)

    def reject_plan(self, plan_id: str):
        return self.app.brain.reject_plan(plan_id)

    # ── Contrôles ────────────────────────────────────────────────────────
    def set_autopilot(self, enabled: bool):
        return self.app.brain.set_autopilot(enabled)

    # ── Voix ─────────────────────────────────────────────────────────────
    def start_voice(self):
        return self.app.brain.start_voice()

    def stop_voice(self):
        return self.app.brain.stop_voice()

    def set_auto_speak(self, enabled: bool):
        return self.app.brain.set_auto_speak(enabled)

    def speak_last_response(self):
        return self.app.brain.speak_last_response()

    # ── État ─────────────────────────────────────────────────────────────
    def get_state(self):
        return self.app.brain.get_state()

    # ── Config ───────────────────────────────────────────────────────────
    def get_config(self):
        return self.app.brain.get_config()

    def save_config(self, api_key: str, model: str, base_url: str):
        return self.app.brain.save_config(api_key, model, base_url)

    # ── Shell log ─────────────────────────────────────────────────────────
    def get_shell_log(self, n: int = 50):
        return self.app.brain.get_shell_log(n)

    # ── Mémoire ───────────────────────────────────────────────────────────
    def forget_memory(self):
        return self.app.brain.forget_memory()

    def get_memory(self):
        return self.app.brain.get_memory()

    # ── Micros disponibles ───────────────────────────────────────────────
    def list_microphones(self):
        return self.app.brain.list_microphones()

    def set_microphone(self, index: int):
        return self.app.brain.set_microphone(int(index))

    # ── Analyse chemin local ──────────────────────────────────────────────
    def analyze_local_path(self, path: str):
        return self.app.brain.analyze_local_path(path)

    # ── Streaming JS polling ──────────────────────────────────────────────
    def poll_js(self):
        return self.app.brain.poll_js()


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