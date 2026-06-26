"""
Voice to Text — Transcription en temps réel avec streaming terminal
Dépendances: pip install SpeechRecognition pyaudio
"""

import speech_recognition as sr
import sys
import time
import threading

# ══════════════════════════════════════════════
#  CONFIG  — modifie ici selon ton setup
# ══════════════════════════════════════════════
LANGUAGE       = "fr-FR"   # fr-FR | en-US | es-ES | de-DE ...
MIC_INDEX      = None      # None = auto | forcer un index ex: 17
ENERGY_START   = 200       # Seuil de départ (baisser = plus sensible)
PAUSE_DURATION = 0.9       # Secondes de silence = fin de phrase
PHRASE_LIMIT   = 15        # Durée max d'une capture (secondes)
# ══════════════════════════════════════════════

GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RED    = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Bannière ──────────────────────────────────
def print_banner():
    print(f"\n{BOLD}{CYAN}{'─'*55}{RESET}")
    print(f"{BOLD}{CYAN}  🎤  VOICE TO TEXT  —  Transcription en temps réel{RESET}")
    print(f"{BOLD}{CYAN}{'─'*55}{RESET}")
    print(f"{GRAY}  Langue : {LANGUAGE}  |  Seuil départ : {ENERGY_START}{RESET}")
    print(f"{GRAY}  Ctrl+C pour quitter{RESET}")
    print(f"{BOLD}{CYAN}{'─'*55}{RESET}\n")


# ── Liste des micros ──────────────────────────
def list_microphones():
    print(f"{CYAN}Micros détectés :{RESET}")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        try:
            safe = name.encode("utf-8", errors="replace").decode("utf-8")
        except Exception:
            safe = repr(name)
        print(f"  {GRAY}[{i}]{RESET} {safe}")
    print()


# ── Sélection automatique du micro ───────────
def pick_microphone() -> int:
    if MIC_INDEX is not None:
        mics = sr.Microphone.list_microphone_names()
        name = mics[MIC_INDEX] if MIC_INDEX < len(mics) else "?"
        print(f"{GREEN}✓ Micro forcé [{MIC_INDEX}] : {name}{RESET}")
        return MIC_INDEX

    mics = sr.Microphone.list_microphone_names()
    if not mics:
        print(f"{RED}✗  Aucun micro détecté !{RESET}")
        sys.exit(1)

    bad  = {"loopback", "virtual", "stereo mix", "what u hear",
            "output", "speaker", "hdmi", "spdif"}
    good = {"microphone", "micro", "mic", "headset", "realtek",
            "usb", "input", "capture", "array", "webcam"}

    best = None
    for i, name in enumerate(mics):
        n = name.lower()
        if any(k in n for k in bad):
            continue
        if any(k in n for k in good):
            best = i
            break

    idx = best if best is not None else 0
    try:
        safe = mics[idx].encode("utf-8", errors="replace").decode("utf-8")
    except Exception:
        safe = repr(mics[idx])
    print(f"{GREEN}✓ Micro sélectionné [{idx}] : {safe}{RESET}")
    return idx


# ── Calibration robuste (sans bug Realtek) ────
def calibrate(recognizer: sr.Recognizer, mic_index: int):
    """
    Calibration via PyAudio direct pour éviter le bug
    AttributeError: 'NoneType'.close() sur certains drivers Realtek/Windows.
    """
    import pyaudio, struct, math

    CHUNK = 1024
    RATE  = 16000
    SECS  = 2

    print(f"{YELLOW}⏳  Calibration ({SECS}s) — reste silencieux...{RESET}")

    pa     = pyaudio.PyAudio()
    stream = None
    rms_values = []

    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=mic_index,
            frames_per_buffer=CHUNK,
        )
        for _ in range(int(RATE / CHUNK * SECS)):
            try:
                data   = stream.read(CHUNK, exception_on_overflow=False)
                shorts = struct.unpack(f"{len(data)//2}h", data)
                rms    = math.sqrt(sum(s*s for s in shorts) / len(shorts))
                rms_values.append(rms)
            except Exception:
                pass
    except Exception as e:
        print(f"{YELLOW}  ⚠ Calibration partielle ({e}) — seuil par défaut utilisé.{RESET}")
    finally:
        if stream:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        try:
            pa.terminate()
        except Exception:
            pass

    # Calcul du seuil : 2× le bruit ambiant, planché à 50
    if rms_values:
        avg = sum(rms_values) / len(rms_values)
        threshold = max(50, min(avg * 2.0, 3000))
    else:
        threshold = ENERGY_START

    recognizer.energy_threshold = threshold
    print(f"{GREEN}✓   Seuil calibré : {int(threshold)}{RESET}")
    print(f"{GREEN}✓   Micro prêt — Parle maintenant !{RESET}\n")
    print(f"{GRAY}{'─'*55}{RESET}")


# ── Spinner d'écoute ──────────────────────────
def spinner_thread(stop_event):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{YELLOW}{frames[i % len(frames)]}  En écoute...{RESET}  ")
        sys.stdout.flush()
        i += 1
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


# ── Affichage streaming du texte ──────────────
def stream_text(text: str):
    timestamp = time.strftime("%H:%M:%S")
    sys.stdout.write(f"\n{GRAY}[{timestamp}]{RESET} {GREEN}{BOLD}")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.018)
    sys.stdout.write(f"{RESET}\n")
    sys.stdout.flush()


# ── Boucle principale ─────────────────────────
def main():
    print_banner()
    list_microphones()

    mic_index  = pick_microphone()
    recognizer = sr.Recognizer()

    recognizer.energy_threshold        = ENERGY_START
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_ratio    = 1.2   # plus sensible (défaut 1.5)
    recognizer.pause_threshold         = PAUSE_DURATION
    recognizer.non_speaking_duration   = 0.3

    calibrate(recognizer, mic_index)

    phrase_count     = 0
    inaudible_streak = 0

    while True:
        stop_event = threading.Event()
        spin = threading.Thread(target=spinner_thread, args=(stop_event,), daemon=True)
        spin.start()

        try:
            with sr.Microphone(device_index=mic_index) as source:
                audio = recognizer.listen(source, phrase_time_limit=PHRASE_LIMIT)

            stop_event.set()
            spin.join()

            sys.stdout.write(f"\r{CYAN}⚙  Traitement...{RESET}  ")
            sys.stdout.flush()

            text = recognizer.recognize_google(audio, language=LANGUAGE)

            if text.strip():
                phrase_count    += 1
                inaudible_streak = 0
                stream_text(text)

        except sr.UnknownValueError:
            stop_event.set()
            spin.join()
            inaudible_streak += 1
            sys.stdout.write(f"\r{GRAY}〜  (inaudible){RESET}\n")
            sys.stdout.flush()

            # Auto-correction : après 3 inaudibles → baisser le seuil de 25%
            if inaudible_streak >= 3:
                new_t = max(50, recognizer.energy_threshold * 0.75)
                recognizer.energy_threshold = new_t
                sys.stdout.write(
                    f"{GRAY}   [auto] Seuil abaissé → {int(new_t)}{RESET}\n"
                )
                sys.stdout.flush()
                inaudible_streak = 0

        except sr.RequestError as e:
            stop_event.set()
            spin.join()
            print(f"\n{RED}✗  Erreur API Google : {e}{RESET}")
            print(f"{GRAY}   Vérifie ta connexion internet.{RESET}\n")
            time.sleep(2)

        except KeyboardInterrupt:
            stop_event.set()
            spin.join()
            print(f"\n\n{CYAN}{'─'*55}{RESET}")
            print(f"{BOLD}  Session terminée — {phrase_count} phrase(s) transcrite(s){RESET}")
            print(f"{CYAN}{'─'*55}{RESET}\n")
            sys.exit(0)


# ── Point d'entrée ────────────────────────────
if __name__ == "__main__":
    for pkg, name in [("speech_recognition", "SpeechRecognition"), ("pyaudio", "pyaudio")]:
        try:
            __import__(pkg)
        except ImportError:
            print(f"{RED}✗  {name} manquant → pip install {name}{RESET}")
            sys.exit(1)

    main()
