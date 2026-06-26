"""
assista_commands.py
════════════════
Moteur de commandes vocales prédéfinies pour ASSISTA.
Aucun LLM requis : correspondance par mots-clés normalisés.

Chaque règle = {
    "patterns"  : liste de phrases ou mots-clés déclencheurs (normalisés, sans accents)
    "kind"      : action ActionProposal (open_app, run_shell, open_url, speak_text, …)
    "title"     : libellé humain affiché
    "target"    : cible fixe (peut contenir {ARG} pour les commandes paramétrées)
    "command"   : commande fixe (idem)
    "summary"   : phrase ASSISTA prononce après
    "extract"   : (optionnel) fn(normalized_text) → dict d'arguments extraits
    "category"  : catégorie pour le markdown de doc
}
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Helpers d'extraction d'arguments
# ─────────────────────────────────────────────────────────────────────────────

def _after(text: str, keywords: List[str]) -> str:
    """Retourne la portion de texte après le premier mot-clé trouvé."""
    for kw in keywords:
        idx = text.find(kw)
        if idx != -1:
            return text[idx + len(kw):].strip()
    return text.strip()


def _extract_url(text: str) -> str:
    """Extrait une URL ou construit une recherche Google."""
    m = re.search(r'https?://\S+', text)
    if m:
        return m.group(0)
    query = _after(text, ["ouvre", "va sur", "ouvrir", "navigue vers", "cherche sur google", "recherche"])
    if query:
        return "https://www.google.com/search?q=" + query.replace(" ", "+")
    return ""


def _extract_volume(text: str) -> str:
    """Extrait un niveau de volume (0-100) ou retourne None."""
    m = re.search(r'\b(\d{1,3})\b', text)
    if m:
        vol = max(0, min(100, int(m.group(1))))
        return str(vol)
    if "max" in text or "maximum" in text:
        return "100"
    if "min" in text or "minimum" in text or "zero" in text:
        return "0"
    return ""


def _extract_brightness(text: str) -> str:
    m = re.search(r'\b(\d{1,3})\b', text)
    if m:
        val = max(0, min(100, int(m.group(1))))
        return str(val)
    if "max" in text or "plein" in text:
        return "100"
    if "min" in text or "zero" in text:
        return "0"
    return ""


def _extract_timer(text: str) -> str:
    """Extrait une durée (minutes/secondes) et retourne la commande shell."""
    minutes = re.search(r'(\d+)\s*(?:minute|min)', text)
    seconds = re.search(r'(\d+)\s*(?:seconde|sec)', text)
    total_sec = 0
    if minutes:
        total_sec += int(minutes.group(1)) * 60
    if seconds:
        total_sec += int(seconds.group(1))
    if total_sec == 0:
        total_sec = 60  # défaut : 1 minute
    return (
        f"Start-Sleep -Seconds {total_sec}; "
        f"[System.Media.SystemSounds]::Beep.Play(); "
        f"Add-Type -AssemblyName PresentationFramework; "
        f"[System.Windows.MessageBox]::Show('Minuterie echouee !','ASSISTA')"
    )


def _extract_search_term(text: str) -> str:
    term = _after(text, [
        "cherche", "recherche", "trouve", "google", "bing",
        "youtube", "wikipedia", "wiki",
    ])
    return term or text


# ─────────────────────────────────────────────────────────────────────────────
# TABLE DES COMMANDES PRÉDÉFINIES
# ─────────────────────────────────────────────────────────────────────────────

COMMANDS: List[Dict[str, Any]] = [

    # ══════════════════════════════════════════════════════════════
    # 1. APPLICATIONS SYSTEME
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Applications",
        "patterns": ["ouvre le bloc-notes", "ouvre notepad", "lance notepad", "ouvrir notepad"],
        "kind": "open_app", "title": "Ouvrir Bloc-Notes",
        "target": "notepad.exe", "command": "",
        "summary": "Bloc-Notes ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre la calculatrice", "lance la calculatrice", "ouvrir calculatrice"],
        "kind": "open_app", "title": "Ouvrir Calculatrice",
        "target": "calc.exe", "command": "",
        "summary": "Calculatrice ouverte.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre paint", "lance paint", "ouvrir paint"],
        "kind": "open_app", "title": "Ouvrir Paint",
        "target": "mspaint.exe", "command": "",
        "summary": "Paint ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre l'explorateur", "ouvre les fichiers", "ouvrir l explorateur", "ouvrir fichiers"],
        "kind": "open_app", "title": "Ouvrir Explorateur",
        "target": "explorer.exe", "command": "",
        "summary": "Explorateur de fichiers ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre le terminal", "ouvre cmd", "ouvrir terminal", "lance cmd", "invite de commandes"],
        "kind": "open_app", "title": "Ouvrir Terminal (CMD)",
        "target": "cmd.exe", "command": "",
        "summary": "Terminal ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre powershell", "lance powershell", "ouvrir powershell"],
        "kind": "open_app", "title": "Ouvrir PowerShell",
        "target": "powershell.exe", "command": "",
        "summary": "PowerShell ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre les parametres", "ouvre les reglages", "ouvrir parametres", "parametre windows"],
        "kind": "open_app", "title": "Ouvrir Paramètres Windows",
        "target": "ms-settings:", "command": "",
        "summary": "Paramètres Windows ouverts.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre le gestionnaire de taches", "gestionnaire de taches", "task manager"],
        "kind": "run_shell", "title": "Ouvrir Gestionnaire des tâches",
        "target": "powershell", "command": "Start-Process taskmgr.exe",
        "summary": "Gestionnaire des tâches ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre chrome", "lance chrome", "ouvrir chrome"],
        "kind": "open_app", "title": "Ouvrir Chrome",
        "target": "chrome.exe", "command": "",
        "summary": "Chrome ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre edge", "lance edge", "ouvrir edge"],
        "kind": "open_app", "title": "Ouvrir Edge",
        "target": "msedge.exe", "command": "",
        "summary": "Edge ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre word", "lance word", "ouvrir word"],
        "kind": "run_shell", "title": "Ouvrir Word",
        "target": "powershell", "command": "Start-Process winword.exe",
        "summary": "Word ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre excel", "lance excel", "ouvrir excel"],
        "kind": "run_shell", "title": "Ouvrir Excel",
        "target": "powershell", "command": "Start-Process excel.exe",
        "summary": "Excel ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre vs code", "ouvre vscode", "lance visual studio code"],
        "kind": "run_shell", "title": "Ouvrir VS Code",
        "target": "powershell", "command": "Start-Process code",
        "summary": "Visual Studio Code ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre spotify", "lance spotify"],
        "kind": "run_shell", "title": "Ouvrir Spotify",
        "target": "powershell", "command": "Start-Process spotify",
        "summary": "Spotify ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre discord", "lance discord"],
        "kind": "run_shell", "title": "Ouvrir Discord",
        "target": "powershell", "command": "Start-Process discord",
        "summary": "Discord ouvert.",
    },
    {
        "category": "Applications",
        "patterns": ["ouvre vlc", "lance vlc"],
        "kind": "run_shell", "title": "Ouvrir VLC",
        "target": "powershell", "command": "Start-Process vlc",
        "summary": "VLC ouvert.",
    },

    # ══════════════════════════════════════════════════════════════
    # 2. NAVIGATION WEB
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Web",
        "patterns": ["ouvre youtube", "va sur youtube", "youtube"],
        "kind": "open_url", "title": "Ouvrir YouTube",
        "target": "https://www.youtube.com", "command": "",
        "summary": "YouTube ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre gmail", "va sur gmail", "ouvre mes mails"],
        "kind": "open_url", "title": "Ouvrir Gmail",
        "target": "https://mail.google.com", "command": "",
        "summary": "Gmail ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre github", "va sur github"],
        "kind": "open_url", "title": "Ouvrir GitHub",
        "target": "https://github.com", "command": "",
        "summary": "GitHub ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre google", "va sur google", "ouvre le navigateur"],
        "kind": "open_url", "title": "Ouvrir Google",
        "target": "https://www.google.com", "command": "",
        "summary": "Google ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre wikipedia", "va sur wikipedia"],
        "kind": "open_url", "title": "Ouvrir Wikipedia",
        "target": "https://fr.wikipedia.org", "command": "",
        "summary": "Wikipedia ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre netflix", "va sur netflix"],
        "kind": "open_url", "title": "Ouvrir Netflix",
        "target": "https://www.netflix.com", "command": "",
        "summary": "Netflix ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["ouvre chatgpt", "va sur chatgpt"],
        "kind": "open_url", "title": "Ouvrir ChatGPT",
        "target": "https://chat.openai.com", "command": "",
        "summary": "ChatGPT ouvert.",
    },
    {
        "category": "Web",
        "patterns": ["cherche sur google", "recherche sur google", "google"],
        "kind": "open_url", "title": "Recherche Google",
        "target": "",  # rempli dynamiquement
        "command": "",
        "summary": "Recherche lancée.",
        "extract": lambda t: {"target": "https://www.google.com/search?q=" + _after(t, ["google", "cherche", "recherche"]).replace(" ", "+")},
    },
    {
        "category": "Web",
        "patterns": ["cherche sur youtube", "recherche sur youtube"],
        "kind": "open_url", "title": "Recherche YouTube",
        "target": "",
        "command": "",
        "summary": "Recherche YouTube lancée.",
        "extract": lambda t: {"target": "https://www.youtube.com/results?search_query=" + _after(t, ["youtube", "cherche", "recherche"]).replace(" ", "+")},
    },

    # ══════════════════════════════════════════════════════════════
    # 3. VOLUME ET AUDIO
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Audio",
        "patterns": ["monte le volume", "augmente le volume", "plus fort", "hausse le son"],
        "kind": "run_shell", "title": "Volume +10",
        "target": "powershell",
        "command": (
            "$wsh = New-Object -ComObject WScript.Shell; "
            "1..2 | ForEach-Object { $wsh.SendKeys([char]175) }"
        ),
        "summary": "Volume augmenté.",
    },
    {
        "category": "Audio",
        "patterns": ["baisse le volume", "diminue le volume", "moins fort", "baisse le son"],
        "kind": "run_shell", "title": "Volume -10",
        "target": "powershell",
        "command": (
            "$wsh = New-Object -ComObject WScript.Shell; "
            "1..2 | ForEach-Object { $wsh.SendKeys([char]174) }"
        ),
        "summary": "Volume diminué.",
    },
    {
        "category": "Audio",
        "patterns": ["coupe le son", "mute", "silencieux", "sourdine"],
        "kind": "run_shell", "title": "Couper le son",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)",
        "summary": "Son coupé.",
    },
    {
        "category": "Audio",
        "patterns": ["reactive le son", "unmute", "remet le son", "enleve le silencieux"],
        "kind": "run_shell", "title": "Réactiver le son",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)",
        "summary": "Son réactivé.",
    },
    {
        "category": "Audio",
        "patterns": ["volume maximum", "volume au max", "son maximum"],
        "kind": "run_shell", "title": "Volume maximum",
        "target": "powershell",
        "command": (
            "$wsh = New-Object -ComObject WScript.Shell; "
            "1..20 | ForEach-Object { $wsh.SendKeys([char]175) }"
        ),
        "summary": "Volume au maximum.",
    },
    {
        "category": "Audio",
        "patterns": ["volume minimum", "son minimum", "volume tres bas"],
        "kind": "run_shell", "title": "Volume minimum",
        "target": "powershell",
        "command": (
            "$wsh = New-Object -ComObject WScript.Shell; "
            "1..20 | ForEach-Object { $wsh.SendKeys([char]174) }"
        ),
        "summary": "Volume au minimum.",
    },

    # ══════════════════════════════════════════════════════════════
    # 4. ECRAN ET AFFICHAGE
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Écran",
        "patterns": ["prends une capture d ecran", "capture d ecran", "screenshot", "fais une capture"],
        "kind": "capture_screen", "title": "Capture d'écran",
        "target": "screen", "command": "",
        "summary": "Capture d'écran effectuée.",
    },
    {
        "category": "Écran",
        "patterns": ["analyse l ecran", "lis l ecran", "que vois-tu a l ecran", "ocr ecran"],
        "kind": "analyze_screen", "title": "Analyser l'écran (OCR)",
        "target": "screen", "command": "",
        "summary": "Analyse de l'écran effectuée.",
    },
    {
        "category": "Écran",
        "patterns": ["eteins l ecran", "eteindre l ecran", "ecran noir", "verrouille l ecran"],
        "kind": "run_shell", "title": "Éteindre l'écran",
        "target": "powershell",
        "command": "powercfg /change monitor-timeout-ac 1; Start-Process rundll32.exe -ArgumentList 'user32.dll,LockWorkStation'",
        "summary": "Écran éteint et poste verrouillé.",
    },
    {
        "category": "Écran",
        "patterns": ["verrouille le pc", "verrouille l ordinateur", "verrous l ecran", "lock"],
        "kind": "run_shell", "title": "Verrouiller le PC",
        "target": "powershell",
        "command": "Start-Process rundll32.exe -ArgumentList 'user32.dll,LockWorkStation'",
        "summary": "PC verrouillé.",
    },
    {
        "category": "Écran",
        "patterns": ["passe en mode nuit", "mode nuit", "filtre de couleur"],
        "kind": "run_shell", "title": "Activer mode nuit",
        "target": "powershell",
        "command": "Start-Process ms-settings:nightlight",
        "summary": "Paramètres du mode nuit ouverts.",
    },

    # ══════════════════════════════════════════════════════════════
    # 5. GESTION DU PC (alimentation)
    # ══════════════════════════════════════════════════════════════
    {
        "category": "PC",
        "patterns": ["eteins le pc", "eteindre le pc", "arreter le pc", "shutdown"],
        "kind": "run_shell", "title": "Éteindre le PC",
        "target": "powershell",
        "command": "Stop-Computer -Force",
        "summary": "Le PC va s'éteindre.",
    },
    {
        "category": "PC",
        "patterns": ["redemarrer le pc", "redemarrage", "restart", "reboot"],
        "kind": "run_shell", "title": "Redémarrer le PC",
        "target": "powershell",
        "command": "Restart-Computer -Force",
        "summary": "Le PC va redémarrer.",
    },
    {
        "category": "PC",
        "patterns": ["mode veille", "mettre en veille", "hibernate", "hibernation"],
        "kind": "run_shell", "title": "Mettre en veille",
        "target": "powershell",
        "command": "Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)",
        "summary": "PC mis en veille.",
    },
    {
        "category": "PC",
        "patterns": ["vide la corbeille", "supprimer la corbeille", "nettoie la corbeille"],
        "kind": "run_shell", "title": "Vider la corbeille",
        "target": "powershell",
        "command": "Clear-RecycleBin -Force",
        "summary": "Corbeille vidée.",
    },
    {
        "category": "PC",
        "patterns": ["quelle heure est-il", "quelle heure", "dis moi l heure", "heure actuelle"],
        "kind": "speak_text", "title": "Dire l'heure",
        "target": "voice", "command": "",  # généré dynamiquement
        "summary": "",
        "extract": lambda _: {"command": __import__("datetime").datetime.now().strftime("Il est %H heures %M.")},
    },
    {
        "category": "PC",
        "patterns": ["quel jour sommes-nous", "quelle date", "dis moi la date", "date du jour"],
        "kind": "speak_text", "title": "Dire la date",
        "target": "voice", "command": "",
        "summary": "",
        "extract": lambda _: {"command": __import__("datetime").datetime.now().strftime("Nous sommes le %d %B %Y.")},
    },
    {
        "category": "PC",
        "patterns": ["quel est mon pc", "nom du pc", "nom de l ordinateur"],
        "kind": "run_shell", "title": "Nom du PC",
        "target": "powershell",
        "command": "$env:COMPUTERNAME",
        "summary": "Nom de l'ordinateur affiché.",
    },
    {
        "category": "PC",
        "patterns": ["combien de ram", "memoire ram", "memoire vive"],
        "kind": "run_shell", "title": "Infos RAM",
        "target": "powershell",
        "command": "Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum | ForEach-Object { [math]::Round($_.Sum/1GB,2).ToString() + ' Go de RAM installee' }",
        "summary": "Infos RAM affichées.",
    },
    {
        "category": "PC",
        "patterns": ["espace disque", "espace libre", "combien d espace", "taille disque"],
        "kind": "run_shell", "title": "Espace disque",
        "target": "powershell",
        "command": "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Libre(Go)';E={[math]::Round($_.Free/1GB,1)}}, @{N='Total(Go)';E={[math]::Round(($_.Used+$_.Free)/1GB,1)}} | Format-Table -AutoSize | Out-String",
        "summary": "Espace disque affiché.",
    },
    {
        "category": "PC",
        "patterns": ["processus en cours", "liste des processus", "quels programmes tournent"],
        "kind": "run_shell", "title": "Processus actifs",
        "target": "powershell",
        "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet | Format-Table -AutoSize | Out-String",
        "summary": "Processus affichés.",
    },

    # ══════════════════════════════════════════════════════════════
    # 6. FICHIERS ET DOSSIERS
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Fichiers",
        "patterns": ["ouvre le bureau", "aller au bureau", "affiche le bureau"],
        "kind": "open_path", "title": "Ouvrir le Bureau",
        "target": "$env:USERPROFILE\\Desktop", "command": "",
        "summary": "Bureau ouvert.",
    },
    {
        "category": "Fichiers",
        "patterns": ["ouvre mes documents", "aller dans documents", "affiche mes documents"],
        "kind": "open_path", "title": "Ouvrir Documents",
        "target": "$env:USERPROFILE\\Documents", "command": "",
        "summary": "Dossier Documents ouvert.",
    },
    {
        "category": "Fichiers",
        "patterns": ["ouvre mes telechargements", "aller dans telechargements", "affiche les telechargements"],
        "kind": "open_path", "title": "Ouvrir Téléchargements",
        "target": "$env:USERPROFILE\\Downloads", "command": "",
        "summary": "Dossier Téléchargements ouvert.",
    },
    {
        "category": "Fichiers",
        "patterns": ["ouvre mes images", "aller dans images", "affiche mes photos"],
        "kind": "open_path", "title": "Ouvrir Images",
        "target": "$env:USERPROFILE\\Pictures", "command": "",
        "summary": "Dossier Images ouvert.",
    },
    {
        "category": "Fichiers",
        "patterns": ["ouvre ma musique", "aller dans musique"],
        "kind": "open_path", "title": "Ouvrir Musique",
        "target": "$env:USERPROFILE\\Music", "command": "",
        "summary": "Dossier Musique ouvert.",
    },
    {
        "category": "Fichiers",
        "patterns": ["liste le bureau", "qu est-ce qu il y a sur le bureau", "fichiers du bureau"],
        "kind": "list_dir", "title": "Lister le Bureau",
        "target": "bureau", "command": "",
        "summary": "Contenu du bureau listé.",
    },
    {
        "category": "Fichiers",
        "patterns": ["liste mes documents", "qu est-ce qu il y a dans documents"],
        "kind": "list_dir", "title": "Lister Documents",
        "target": "documents", "command": "",
        "summary": "Contenu du dossier Documents listé.",
    },
    {
        "category": "Fichiers",
        "patterns": ["cree un nouveau fichier", "nouveau fichier texte", "creer un fichier"],
        "kind": "run_shell", "title": "Nouveau fichier texte sur le Bureau",
        "target": "powershell",
        "command": "New-Item -Path \"$env:USERPROFILE\\Desktop\\nouveau.txt\" -ItemType File -Force | Out-Null; notepad.exe \"$env:USERPROFILE\\Desktop\\nouveau.txt\"",
        "summary": "Nouveau fichier texte créé sur le bureau.",
    },

    # ══════════════════════════════════════════════════════════════
    # 7. RÉSEAU ET WIFI
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Réseau",
        "patterns": ["quel est mon ip", "mon adresse ip", "adresse ip"],
        "kind": "run_shell", "title": "Adresse IP",
        "target": "powershell",
        "command": "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' } | Select-Object -First 1).IPAddress",
        "summary": "Adresse IP affichée.",
    },
    {
        "category": "Réseau",
        "patterns": ["teste la connexion", "test internet", "ping google", "est-ce que j ai internet"],
        "kind": "run_shell", "title": "Test connexion Internet",
        "target": "powershell",
        "command": "if (Test-Connection google.com -Count 2 -Quiet) { 'Connexion Internet : OK' } else { 'Pas de connexion Internet detectee' }",
        "summary": "Test de connexion effectué.",
    },
    {
        "category": "Réseau",
        "patterns": ["montre le wifi", "reseaux wifi", "reseaux disponibles", "liste les reseaux"],
        "kind": "run_shell", "title": "Réseaux Wi-Fi disponibles",
        "target": "powershell",
        "command": "netsh wlan show networks | Select-String 'SSID' | Out-String",
        "summary": "Réseaux Wi-Fi listés.",
    },
    {
        "category": "Réseau",
        "patterns": ["active le wifi", "activer le wifi", "allume le wifi"],
        "kind": "run_shell", "title": "Activer Wi-Fi",
        "target": "powershell",
        "command": "Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false",
        "summary": "Wi-Fi activé.",
    },
    {
        "category": "Réseau",
        "patterns": ["desactive le wifi", "desactiver le wifi", "coupe le wifi"],
        "kind": "run_shell", "title": "Désactiver Wi-Fi",
        "target": "powershell",
        "command": "Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false",
        "summary": "Wi-Fi désactivé.",
    },

    # ══════════════════════════════════════════════════════════════
    # 8. CLIPBOARD ET TEXTE
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Presse-papier",
        "patterns": ["qu est-ce qu il y a dans le presse-papier", "lis le presse-papier", "affiche le presse-papier"],
        "kind": "run_shell", "title": "Lire le presse-papier",
        "target": "powershell",
        "command": "Get-Clipboard",
        "summary": "Contenu du presse-papier affiché.",
    },
    {
        "category": "Presse-papier",
        "patterns": ["vide le presse-papier", "efface le presse-papier"],
        "kind": "run_shell", "title": "Vider le presse-papier",
        "target": "powershell",
        "command": "Set-Clipboard -Value ''",
        "summary": "Presse-papier vidé.",
    },

    # ══════════════════════════════════════════════════════════════
    # 9. MINUTERIE ET RAPPELS
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Minuterie",
        "patterns": [
            "lance une minuterie", "programme un minuteur", "set un timer",
            "minuterie de", "minuteur de", "dans une minute", "dans cinq minutes",
            "dans dix minutes", "dans trente minutes",
        ],
        "kind": "run_shell", "title": "Minuterie",
        "target": "powershell",
        "command": "",  # généré dynamiquement
        "summary": "Minuterie programmée.",
        "extract": lambda t: {"command": _extract_timer(t)},
    },

    # ══════════════════════════════════════════════════════════════
    # 10. RACCOURCIS CLAVIER SYSTÈME
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Raccourcis",
        "patterns": ["alt tab", "change de fenetre", "fenetre suivante", "passe a l application suivante"],
        "kind": "run_shell", "title": "Alt+Tab",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('%{TAB}')",
        "summary": "Changement de fenêtre effectué.",
    },
    {
        "category": "Raccourcis",
        "patterns": ["ferme la fenetre", "fermer la fenetre", "alt f4", "quitte l application"],
        "kind": "run_shell", "title": "Fermer la fenêtre active",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('%{F4}')",
        "summary": "Fenêtre fermée.",
    },
    {
        "category": "Raccourcis",
        "patterns": ["agrandis la fenetre", "fenetre en plein ecran", "maximise la fenetre"],
        "kind": "run_shell", "title": "Maximiser la fenêtre",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('^{UP}')",
        "summary": "Fenêtre agrandie.",
    },
    {
        "category": "Raccourcis",
        "patterns": ["reduis la fenetre", "minimise la fenetre", "cache la fenetre"],
        "kind": "run_shell", "title": "Minimiser la fenêtre",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('^{DOWN}')",
        "summary": "Fenêtre réduite.",
    },
    {
        "category": "Raccourcis",
        "patterns": ["annule", "ctrl z", "defaire"],
        "kind": "run_shell", "title": "Ctrl+Z (Annuler)",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('^z')",
        "summary": "Action annulée.",
    },
    {
        "category": "Raccourcis",
        "patterns": ["copie tout", "selectionne tout", "ctrl a"],
        "kind": "run_shell", "title": "Ctrl+A (Tout sélectionner)",
        "target": "powershell",
        "command": "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys('^a')",
        "summary": "Tout sélectionné.",
    },

    # ══════════════════════════════════════════════════════════════
    # 11. MISES A JOUR ET MAINTENANCE
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Maintenance",
        "patterns": ["nettoie les fichiers temporaires", "supprime les fichiers temp", "vide le cache"],
        "kind": "run_shell", "title": "Nettoyer fichiers temporaires",
        "target": "powershell",
        "command": "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Fichiers temporaires supprimes.'",
        "summary": "Fichiers temporaires nettoyés.",
    },
    {
        "category": "Maintenance",
        "patterns": ["mets a jour windows", "cherche les mises a jour", "windows update"],
        "kind": "run_shell", "title": "Windows Update",
        "target": "powershell",
        "command": "Start-Process ms-settings:windowsupdate",
        "summary": "Windows Update ouvert.",
    },
    {
        "category": "Maintenance",
        "patterns": ["repare le reseau", "reinitialise le reseau", "reset reseau"],
        "kind": "run_shell", "title": "Réinitialiser le réseau",
        "target": "powershell",
        "command": "ipconfig /release; ipconfig /flushdns; ipconfig /renew",
        "summary": "Réseau réinitialisé.",
    },

    # ══════════════════════════════════════════════════════════════
    # 12. INFORMATIONS SYSTEME
    # ══════════════════════════════════════════════════════════════
    {
        "category": "Informations",
        "patterns": ["version de windows", "quelle version de windows", "quel windows"],
        "kind": "run_shell", "title": "Version de Windows",
        "target": "powershell",
        "command": "(Get-CimInstance Win32_OperatingSystem).Caption + ' ' + (Get-CimInstance Win32_OperatingSystem).Version",
        "summary": "Version de Windows affichée.",
    },
    {
        "category": "Informations",
        "patterns": ["modele du pc", "marque du pc", "infos materiel", "caracteristiques pc"],
        "kind": "run_shell", "title": "Modèle du PC",
        "target": "powershell",
        "command": "Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model | Format-List | Out-String",
        "summary": "Infos matériel affichées.",
    },
    {
        "category": "Informations",
        "patterns": ["quelle est ma carte graphique", "gpu", "carte graphique"],
        "kind": "run_shell", "title": "Carte graphique",
        "target": "powershell",
        "command": "(Get-CimInstance Win32_VideoController).Name",
        "summary": "Carte graphique affichée.",
    },
    {
        "category": "Informations",
        "patterns": ["quel est mon processeur", "cpu", "processeur"],
        "kind": "run_shell", "title": "Processeur",
        "target": "powershell",
        "command": "(Get-CimInstance Win32_Processor).Name",
        "summary": "Processeur affiché.",
    },

    # ══════════════════════════════════════════════════════════════
    # 13. ASSISTA (meta-commandes)
    # ══════════════════════════════════════════════════════════════
    {
        "category": "ASSISTA",
        "patterns": ["que sais-tu faire", "liste tes commandes", "aide", "help", "commandes disponibles"],
        "kind": "speak_text", "title": "Aide ASSISTA",
        "target": "voice",
        "command": (
            "Je peux ouvrir des applications, contrôler le volume, "
            "capturer l'écran, gérer les fichiers, tester le réseau, "
            "lancer des minuteries, et bien plus encore. "
            "Dites par exemple : ouvre le bloc-notes, monte le volume, "
            "capture d'écran, ou quel est mon IP."
        ),
        "summary": "",
    },
    {
        "category": "ASSISTA",
        "patterns": ["comment tu t appelles", "qui es-tu", "tu es qui", "tu es quoi"],
        "kind": "speak_text", "title": "Présentation ASSISTA",
        "target": "voice",
        "command": "Je suis ASSISTA, votre assistante vocale locale. Je suis là pour vous aider à contrôler votre PC.",
        "summary": "",
    },
    {
        "category": "ASSISTA",
        "patterns": ["merci", "parfait", "super", "bien joue", "bravo"],
        "kind": "speak_text", "title": "Remerciement",
        "target": "voice",
        "command": "Avec plaisir ! Je suis là si vous avez besoin de moi.",
        "summary": "",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions de normalisation et de correspondance
# ─────────────────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Normalise : minuscules, sans accents, espaces multiples → un seul."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower())
    ascii_ = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_).strip()


def _pattern_score(normalized_input: str, pattern: str) -> float:
    """
    Retourne un score de correspondance entre 0 et 1.
    1.0 = correspondance exacte ou très proche.
    0   = aucune correspondance.
    """
    norm_pattern = _normalize(pattern)
    if norm_pattern == normalized_input:
        return 1.0
    if norm_pattern in normalized_input:
        # Le pattern est une sous-chaîne de l'input
        return len(norm_pattern) / len(normalized_input)
    # Correspondance partielle : tous les mots du pattern présents ?
    pattern_words = set(norm_pattern.split())
    input_words = set(normalized_input.split())
    common = pattern_words & input_words
    if len(common) == len(pattern_words):
        # Tous les mots-clés présents
        return 0.75
    return 0.0


def match_command(raw_text: str) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Cherche la meilleure correspondance dans COMMANDS.
    Retourne (commande_correspondante, score) ou (None, 0).
    Score ≥ 0.4 → correspondance acceptée.
    """
    normalized = _normalize(raw_text)
    best_cmd: Optional[Dict[str, Any]] = None
    best_score: float = 0.0

    for cmd in COMMANDS:
        for pattern in cmd["patterns"]:
            score = _pattern_score(normalized, pattern)
            if score > best_score:
                best_score = score
                best_cmd = cmd

    return best_cmd, best_score


def build_action_proposal(cmd: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Construit un dict ActionProposal à partir d'une commande et du texte brut.
    Applique la fonction extract() si elle existe pour les commandes paramétrées.
    """
    result = {
        "kind": cmd["kind"],
        "title": cmd["title"],
        "target": cmd.get("target", ""),
        "command": cmd.get("command", ""),
        "summary": cmd.get("summary", ""),
        "meta": {},
    }
    extract_fn = cmd.get("extract")
    if extract_fn:
        try:
            extras = extract_fn(_normalize(raw_text))
            result.update(extras)
        except Exception:
            pass
    return result


def try_command_match(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Interface principale : retourne un ActionProposal dict si une commande
    correspond, ou None si le LLM doit prendre le relais.
    """
    cmd, score = match_command(raw_text)
    if cmd and score >= 0.40:
        return build_action_proposal(cmd, raw_text)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Génération de la liste de commandes pour le markdown
# ─────────────────────────────────────────────────────────────────────────────

def export_commands_markdown() -> str:
    """Génère le markdown complet de toutes les commandes prédéfinies."""
    from collections import defaultdict
    categories: Dict[str, List] = defaultdict(list)
    for cmd in COMMANDS:
        categories[cmd["category"]].append(cmd)

    icons = {
        "Applications": "🖥️",
        "Web":          "🌐",
        "Audio":        "🔊",
        "Écran":        "📸",
        "PC":           "⚙️",
        "Fichiers":     "📁",
        "Réseau":       "📡",
        "Presse-papier":"📋",
        "Minuterie":    "⏱️",
        "Raccourcis":   "⌨️",
        "Maintenance":  "🔧",
        "Informations": "ℹ️",
        "ASSISTA":         "🎙️",
    }

    lines = [
        "# 🎙️ ASSISTA — Commandes Vocales Prédéfinies\n",
        "> Dites à ASSISTA l'une des phrases ci-dessous. "
        "Les variantes entre guillemets sont toutes acceptées.\n",
        "---\n",
    ]

    for cat, cmds in categories.items():
        icon = icons.get(cat, "•")
        lines.append(f"## {icon} {cat}\n")
        lines.append("| Phrase vocale | Action |\n")
        lines.append("|---|---|\n")
        for cmd in cmds:
            phrases = " / ".join(f'`{p}`' for p in cmd["patterns"][:3])
            lines.append(f"| {phrases} | {cmd['title']} |\n")
        lines.append("\n")

    lines += [
        "---\n",
        "## 💡 Conseils d'utilisation\n",
        "- **Réveil** : Dites `salut`, `bonjour` ou `assista` pour réveiller ASSISTA.\n",
        "- **Veille** : Dites `stop`, `merci`, `bonne nuit` ou `au revoir` pour la mettre en veille.\n",
        "- **Confirmation** : Dites `oui`, `ok` ou `go` pour approuver une action. Dites `non` ou `annule` pour refuser.\n",
        "- Les commandes fonctionnent même avec une formulation légèrement différente.\n",
        "- Si aucune commande ne correspond, ASSISTA bascule automatiquement sur le mode LLM.\n",
    ]
    return "".join(lines)