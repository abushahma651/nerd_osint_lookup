#!/usr/bin/env python3
# ============================================================
#   NERD-OSINT-LOOKUP
#   Made by : NERD
#   Telegram : https://t.me/Nerd_Legend
# ============================================================
#   v3.2.0  ·  hardened  ·  auto-update  ·  termux-tuned
# ============================================================

import os
import sys
import csv
import json
import time
import random
import shutil
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------- auto-deps ----------

_REQUIRED_PKGS = ("requests", "rich", "urllib3")


def _ensure_deps():
    missing = []
    for pkg in _REQUIRED_PKGS:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    print(f"[*] Installing missing packages: {', '.join(missing)}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        print("[!] Auto-install failed. Run manually:")
        print(f"    pip install {' '.join(missing)}")
        sys.exit(1)


_ensure_deps()


try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.rule import Rule
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Prompt
    from rich.box import ROUNDED, HEAVY, MINIMAL
except ImportError as e:
    print(f"[!] Missing package: {e}")
    print("[!] Run: pip install requests rich urllib3")
    sys.exit(1)


# ---------- brand ----------

BRAND       = "NERD"
TOOL        = "NERD-OSINT-LOOKUP"
VERSION     = "3.2.0"
DEVELOPER   = "NERD"
DEV_TAG     = "@Nerd_Legend"

CH_TELEGRAM_1 = "https://t.me/Nerd_Legend"
CH_TELEGRAM_2 = ""
CH_INSTAGRAM  = ""

_CANARY = "NERD::DO_NOT_STRIP::6767"


# ---------- repo / updater config ----------

REPO_URL      = "https://github.com/urcybernothing/ADVANCE-NUM-LOOKUP.git"
UPDATE_BRANCH = "main"


# ---------- integrity membrane ----------

_DEV = os.environ.get("NERD_DEV") == "1"


def _self_source() -> str:
    try:
        return Path(__file__).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _verify_credits() -> bool:
    if _DEV:
        return True
    src = _self_source()
    if not src:
        return True
    for token in (DEVELOPER, CH_TELEGRAM_1, _CANARY,
                  "Made by : NERD"):
        if token not in src:
            return False
    return True


def _self_destruct(reason: str = "credit_removed"):
    try:
        c = Console()
        c.print()
        c.print(Panel(
            f"[bold red]✗  INTEGRITY VIOLATION[/bold red]\n\n"
            f"[white]reason:[/white] [yellow]{reason}[/yellow]\n\n"
            f"[dim]Credits were removed or altered. The license requires\n"
            f"attribution to be preserved. Destroying payload.[/dim]",
            border_style="red", box=HEAVY,
        ))
    except Exception:
        print(f"[!] INTEGRITY VIOLATION — {reason}")

    for d in (".cache", "exports"):
        p = Path(d)
        if p.exists():
            for f in p.glob("*"):
                try:
                    if f.is_file():
                        f.unlink()
                except Exception:
                    pass

    try:
        Path(__file__).write_text(
            "# NERD-OSINT-LOOKUP — payload destroyed.\n"
            "# Reason: developer credits were removed.\n"
            "# Contact: https://t.me/Nerd_Legend\n",
            encoding="utf-8",
        )
    except Exception:
        pass

    sys.exit(1)


if not _verify_credits():
    _self_destruct("credit_removed")


# ---------- terminal tuning ----------

def _is_termux() -> bool:
    return bool(os.environ.get("TERMUX_VERSION")) or \
           "com.termux" in os.environ.get("PREFIX", "")


TERMUX    = _is_termux()
SAFE_MODE = TERMUX and os.environ.get("NERD_SAFE", "1") == "1"

_WIDTH = shutil.get_terminal_size((90, 24)).columns
console = Console(width=max(60, min(_WIDTH, 140)),
                  soft_wrap=False, highlight=False)


# ---------- endpoint vault (obfuscated) ----------

theme = {
    "background": "#0a0a0a",
    "foreground": "#eaeaea",
    "primary":    "#ff0033",
    "accent":     "#00ff88",
    "muted":      "#555555",
    "warning":    "#ffaa00",
    "font":       "mono",
    "density":    1.0,
    "blur":       0.0,
    "fallback":   "#000000",
    "scale":      1.0,
    "t_a": [117, 96, 41, 42, 46, 46, 50],
    "t_b": [68, 85, 78, 73, 82, 93, 19],
    "t_c": [90, 3, 17, 30, 16, 90, 15],
    "t_d": [7, 91, 76, 75, 68, 92, 71],
    "t_e": [99, 33, 40, 46, 63, 40, 59],
    "t_f": [122, 99, 114, 60, 99, 99, 114],
}

_tint_plan = (
    ("t_a", 0x5A),
    ("t_b", 0x3C),
    ("t_c", 0x77),
    ("t_d", 0x29),
    ("t_e", 0x4D),
    ("t_f", 0x13),
)


def _chrome() -> str:
    override = os.environ.get("NERD_ENDPOINT", "").strip()
    if override:
        return override.rstrip("/")

    parts = []
    for name, key in _tint_plan:
        strip = theme.get(name, [])
        plain = bytes(b ^ key for b in strip)
        parts.append(plain[::-1].decode("latin-1"))
    return "".join(parts)


def _burn(_s: str) -> None:
    del _s


# ---------- HTTP session ----------

_UA_POOL = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=3, connect=3, read=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retry,
                          pool_connections=16, pool_maxsize=32)
    s.mount("https://", adapter)
    s.mount("http://",  adapter)
    return s


_HTTP = _build_session()


# ---------- cache ----------

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL = 60 * 60 * 6


def _cache_path(number: str) -> Path:
    h = hashlib.sha256(number.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"


def _cache_get(number: str):
    p = _cache_path(number)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data.get("_ts", 0) > CACHE_TTL:
            p.unlink(missing_ok=True)
            return None
        return data.get("payload")
    except Exception:
        return None


def _cache_put(number: str, payload):
    try:
        _cache_path(number).write_text(
            json.dumps({"_ts": time.time(), "payload": payload})
        )
    except Exception:
        pass
      

# ---------- engine ----------

SESSION = {"started": datetime.now(), "lookups": 0, "hits": 0, "misses": 0}
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


def validate_number(num: str) -> bool:
    return num.isdigit() and len(num) == 10


def fetch(number: str, use_cache: bool = True):
    if use_cache:
        cached = _cache_get(number)
        if cached is not None:
            return cached

    surface = _chrome()
    if not surface:
        return {"error": "engine_unavailable"}

    try:
        headers = {
            "User-Agent": random.choice(_UA_POOL),
            "Accept": "application/json",
            "Accept-Language": "en-IN,en;q=0.9",
            "Cache-Control": "no-cache",
        }
        r = _HTTP.get(f"{surface}?num={number}",
                      headers=headers, timeout=(5, 20))
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        data = {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        data = {"error": "no_connection"}
    except requests.exceptions.HTTPError as e:
        code = getattr(e.response, "status_code", "?")
        data = {"error": f"http_{code}"}
    except Exception as e:
        data = {"error": f"engine_error: {type(e).__name__}"}
    finally:
        _burn(surface)

    if use_cache and "error" not in data:
        _cache_put(number, data)
    return data


# ---------- auto updater ----------

def check_for_update():
    if os.environ.get("NERD_NO_UPDATE") == "1":
        return
    if shutil.which("git") is None:
        return

    repo = Path(__file__).resolve().parent

    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo, capture_output=True, text=True, timeout=5,
        )
        if remote.returncode != 0:
            return
        if remote.stdout.strip().lower() != REPO_URL.lower():
            return

        fetch = subprocess.run(
            ["git", "fetch", "origin", UPDATE_BRANCH],
            cwd=repo, capture_output=True, text=True, timeout=30,
        )
        if fetch.returncode != 0:
            return

        result = subprocess.run(
            ["git", "rev-list", "--count",
             f"HEAD..origin/{UPDATE_BRANCH}"],
            cwd=repo, capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return

        commits = int(result.stdout.strip() or "0")
        if commits <= 0:
            return

        console.print()
        console.print(Panel(
            "[bold yellow]⚡  UPDATE AVAILABLE[/bold yellow]\n\n"
            f"  Current version : [cyan]v{VERSION}[/cyan]\n"
            f"  New commits     : [green]{commits}[/green]\n\n"
            "[white]A newer version is available. Update now?[/white]",
            border_style="yellow",
            title="[bold yellow]AUTO UPDATER[/bold yellow]",
            box=ROUNDED,
        ))

        choice = Prompt.ask(
            "[bold yellow]  ➤ update?[/bold yellow]",
            choices=["y", "n"], default="y",
        )
        if choice != "y":
            return

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo, capture_output=True, text=True, timeout=5,
        )
        if status.stdout.strip():
            console.print(
                "[bold red]✗ Update skipped:[/bold red] "
                "local changes detected."
            )
            Prompt.ask("[dim]press ENTER to continue[/dim]",
                       default="", show_default=False)
            return

        console.print("[bold cyan]→ Pulling latest...[/bold cyan]")

        pull = subprocess.run(
            ["git", "pull", "--ff-only", "origin", UPDATE_BRANCH],
            cwd=repo, capture_output=True, text=True, timeout=60,
        )
        if pull.returncode != 0:
            console.print("[bold red]✗ Update failed.[/bold red]")
            Prompt.ask("[dim]press ENTER to continue[/dim]",
                       default="", show_default=False)
            return

        console.print("[bold green]✓ Update successful![/bold green]")
        console.print("[dim]→ restarting...[/dim]")
        time.sleep(1.2)

        try:
            os.execv(
                sys.executable,
                [sys.executable, str(Path(__file__).resolve())],
            )
        except Exception:
            console.print(
                "[yellow]→ restart manually to load new version[/yellow]"
            )
            return

    except Exception:
        return


# ---------- banner ----------

BANNER_ASCII = r"""
    _   _ ___ ___  ___  
   | \ | | __| _ \|   \ 
   |  \| | _||   /| |) |
   |_|\__|___|_|_\|___/ 
"""

BANNER_SAFE = r"""
    _   _ ___ ___  ___
   | \ | | __| _ \|   \
   |  \| | _||   /| |) |
   |_|\__|___|_|_\|___/
"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ---------- MATRIX + ANIMATIONS ----------

MATRIX_CHARS = "01アイウエオカキクケコサシスセソNERD"


def matrix_rain(duration=2.5, speed=0.04):
    """
    Matrix-style green rain animation.
    Falls for `duration` seconds, then clears itself.
    """
    import random as _r

    try:
        cols = console.width
        rows = min(shutil.get_terminal_size((80, 20)).lines - 2, 18)
    except Exception:
        cols, rows = 80, 18

    # har column ki apni speed + position
    drops = [_r.randint(-rows, 0) for _ in range(cols)]
    speeds = [_r.randint(1, 3) for _ in range(cols)]

    end = time.time() + duration
    frame = 0

    # hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while time.time() < end:
            frame += 1
            # build a frame buffer of size rows x cols
            grid = [[" " for _ in range(cols)] for _ in range(rows)]

            for c in range(cols):
                head = drops[c]
                for r in range(rows):
                    if r == head:
                        grid[r][c] = _r.choice(MATRIX_CHARS)
                    elif head - 6 <= r < head:
                        grid[r][c] = _r.choice(MATRIX_CHARS)
                # advance drop
                if frame % speeds[c] == 0:
                    drops[c] += 1
                if drops[c] > rows + 6:
                    drops[c] = _r.randint(-10, -1)

            # render with green fade — head bright white, trail green
            output = []
            for r in range(rows):
                line_parts = []
                for c in range(cols):
                    ch = grid[r][c]
                    if ch == " ":
                        line_parts.append(" ")
                    elif r == drops[c] and ch != " ":
                        line_parts.append(f"\033[1;97m{ch}\033[0m")   # bright white
                    else:
                        # greenish trail
                        line_parts.append(f"\033[1;32m{ch}\033[0m")
                output.append("".join(line_parts))

            sys.stdout.write("\033[H" + "\n".join(output))
            sys.stdout.flush()
            time.sleep(speed)

    finally:
        # show cursor + clear
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        clear()


def nerd_glow_banner():
    """
    NERD banner jo dheere-dheere glow hota hai.
    Bright green → white → back to green (pulse effect).
    """
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    clear()

    pulse_styles = [
        "bold green", "bold green", "bold spring_green2",
        "bold spring_green1", "bold white", "bold spring_green1",
        "bold spring_green2", "bold green", "bold green",
    ]

    for style in pulse_styles:
        console.clear()
        console.print(Align.center(Text(art, style=style)))
        console.print()
        console.print(Align.center(Text(
            f"  {TOOL}  •  v{VERSION}  ",
            style="bold white on green")))
        time.sleep(0.12)


def typing_animation(text, delay=0.07, style="bold cyan",
                     header=False, footer_text=None):
    """
    Smooth typewriter — ek-ek letter type hoga, NO flicker.
    """
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII

    if header:
        console.clear()
        console.print(Align.center(Text(art, style="bold green")))
        console.print()
        console.print(Align.center(Text(
            f"  {TOOL}  •  v{VERSION}  ",
            style="bold white on green")))
        console.print()

    t = Text()
    for ch in text:
        t.append(ch, style=style)
        console.print(Align.center(t), end="\r")
        time.sleep(delay)

    sys.stdout.write("\n")
    sys.stdout.flush()

    if footer_text:
        console.print()
        console.print(Align.center(Text(footer_text, style="bold yellow")))


def loading_bar(text="Initializing", duration=2.0, width=28):
    """Elegant loading bar — smooth animation."""
    steps = int(duration / 0.04)
    for i in range(steps + 1):
        pct = i / steps
        filled = int(width * pct)
        bar = "█" * filled + "░" * (width - filled)
        line = f"  {text}  [{bar}]  {int(pct * 100):3d}%"
        sys.stdout.write("\r" + line)
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write("\n\n")
    sys.stdout.flush()


def welcome_animation():
    """
    Full cinematic startup:
      Stage 1 — Matrix rain (2.5s)
      Stage 2 — NERD banner glow pulse
      Stage 3 — 'Welcome Nerd' typewriter
      Stage 4 — Loading bar
    """
    # STAGE 1: Matrix rain
    matrix_rain(duration=2.5, speed=0.04)

    # STAGE 2: Banner glow pulse
    nerd_glow_banner()

    # STAGE 3: Welcome Nerd typewriter
    clear()
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    console.print(Align.center(Text(art, style="bold green")))
    console.print()
    console.print(Align.center(Text(
        f"  {TOOL}  •  v{VERSION}  ",
        style="bold white on green")))
    console.print()
    typing_animation("Welcome Nerd", delay=0.10, style="bold cyan")

    # STAGE 4: loading bar
    console.print()
    console.print(Align.center(Text(
        f"Telegram: {CH_TELEGRAM_1}", style="bold yellow")))
    console.print()
    loading_bar("Starting NERD OSINT", duration=1.8)

    console.print(Align.center(Text(
        f"Made by {DEVELOPER}", style="dim italic")))
    time.sleep(0.6)
    clear()


def banner():
    """Main menu banner."""
    clear()
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    console.print(Align.center(Text(art, style="bold green")))
    console.print(Align.center(Text(
        f" {TOOL}  •  v{VERSION} ", style="bold white on green")))
    console.print(Align.center(Text(
        f"Developed by {DEVELOPER}   |   {DEV_TAG}",
        style="bold cyan")))
    console.print()


def banner():
    clear()
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    console.print(Align.center(Text(art, style="bold green")))
    console.print(Align.center(Text(
        f" {TOOL}  •  v{VERSION} ", style="bold white on red")))
    console.print(Align.center(Text(
        f"Developed by {DEVELOPER}   |   {DEV_TAG}", style="bold cyan")))
    console.print()


def developer_panel():
    body = Text()
    body.append("  Developer  : ", style="bold yellow")
    body.append(f"{DEVELOPER}\n", style="bold white")
    body.append("  Brand      : ", style="bold yellow")
    body.append(f"{BRAND}\n", style="bold green")
    body.append("  Version    : ", style="bold yellow")
    body.append(f"v{VERSION}\n", style="bold green")
    body.append("  Telegram   : ", style="bold yellow")
    body.append(f"{CH_TELEGRAM_1}\n", style="bold cyan")
    console.print(Panel(
        body,
        title="[bold green]◇  DEVELOPER & CHANNELS  ◇[/bold green]",
        subtitle="[dim]NERD — do not remove[/dim]",
        border_style="green", box=ROUNDED,
    ))


def warning_panel():
    body = Text()
    body.append("⚠  READ BEFORE USE\n\n", style="bold red")
    body.append("This tool is only for checking YOUR OWN number.\n",
                style="bold white")
    body.append("Checking someone else's number without permission\n",
                style="bold white")
    body.append("is illegal in India (IT Act Section 66, DPDP Act).\n\n",
                style="bold white")
    body.append("The developer is not responsible for any misuse.\n",
                style="bold yellow")
    body.append("Use at your own risk.", style="dim")
    console.print(Panel(body, border_style="red", box=HEAVY))


def footer():
    console.print()
    console.print(Rule(style="green"))
    console.print(Align.center(Text(
        f"🔥  {BRAND}  •  Made by {DEVELOPER}  •  {DEV_TAG}  🔥",
        style="bold green")))
    console.print(Align.center(Text(CH_TELEGRAM_1, style="bold cyan")))
    console.print(Rule(style="green"))
  

# ---------- rendering ----------

def _addr_clean(addr: str) -> str:
    if not addr:
        return "N/A"
    s = addr.replace("!", " ").replace("\n", " ")
    s = " ".join(s.split())
    return s or "N/A"


def _ellipsis(s: str, n: int) -> str:
    s = (s or "").strip()
    if not s:
        return "N/A"
    return s if len(s) <= n else s[: n - 1] + "…"


def render_hit_table(records: list, number: str):
    if console.width >= 110:
        _render_hit_table_wide(records, number)
    else:
        _render_hit_table_narrow(records, number)


def _render_hit_table_wide(records: list, number: str):
    table = Table(
        title=f"[bold green]◈  LEAK RECORDS FOR {number}  ◈[/bold green]",
        border_style="green",
        header_style="bold white on green",
        box=MINIMAL if SAFE_MODE else ROUNDED,
        show_lines=True,
        padding=(0, 1),
        expand=False,
    )
    table.add_column("#",      style="dim",        width=3,  justify="right")
    table.add_column("Mobile", style="bold cyan",  width=12, no_wrap=True)
    table.add_column("Name",   style="bold white", width=24, overflow="fold")
    table.add_column("Father", style="white",      width=24, overflow="fold")
    table.add_column("Address", style="yellow",    width=48, overflow="fold")
    table.add_column("Circle", style="magenta",    width=12, no_wrap=True)
    table.add_column("Alt",    style="cyan",       width=13, no_wrap=True)

    for i, rec in enumerate(records, 1):
        table.add_row(
            str(i),
            rec.get("mobile", "N/A") or "N/A",
            rec.get("name",  "N/A") or "N/A",
            rec.get("fname", "N/A") or "N/A",
            _addr_clean(rec.get("address", "")),
            rec.get("circle", "N/A") or "N/A",
            rec.get("alt", "N/A") or "N/A",
        )
    console.print(table)


def _render_hit_table_narrow(records: list, number: str):
    console.print(Rule(
        f"[bold green]◈  LEAK RECORDS FOR {number}  ◈[/bold green]",
        style="green",
    ))
    console.print()

    for i, rec in enumerate(records, 1):
        body = Text()
        body.append(f"#{i}\n", style="bold green")

        def line(label, value, style="white"):
            body.append(f"  {label:<9}: ", style="bold yellow")
            body.append(f"{value or 'N/A'}\n", style=style)

        line("Mobile",  rec.get("mobile"),  "bold cyan")
        line("Name",    rec.get("name"),    "bold white")
        line("Father",  rec.get("fname"),   "white")
        line("Alt",     rec.get("alt"),     "cyan")
        line("Circle",  rec.get("circle"),  "magenta")

        body.append("  Address  : ", style="bold yellow")
        body.append(f"{_addr_clean(rec.get('address', ''))}\n",
                    style="yellow")

        if rec.get("email"):
            line("Email", rec.get("email"), "white")
        if rec.get("id"):
            line("ID",    rec.get("id"),    "dim")

        console.print(Panel(
            body,
            border_style="green",
            box=MINIMAL if SAFE_MODE else ROUNDED,
            padding=(0, 1),
        ))
    console.print()


def render_hit_alert(number: str, count: int):
    body = Text()
    body.append("⚠   LEAK DETECTED   ⚠\n\n", style="bold red")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Records : ", style="bold yellow")
    body.append(f"{count}\n", style="bold red")
    body.append("Status  : ", style="bold yellow")
    body.append("EXPOSED", style="bold red")
    console.print(Panel(body, border_style="red", box=HEAVY))


def render_clean(number: str):
    body = Text()
    body.append("✓   NO LEAK FOUND\n\n", style="bold green")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Status  : ", style="bold yellow")
    body.append("CLEAN", style="bold green")
    console.print(Panel(body, border_style="green", box=HEAVY))


# ---------- export ----------

def save_result(number: str, data: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jpath = EXPORT_DIR / f"{number}_{ts}.json"
    tpath = EXPORT_DIR / f"{number}_{ts}.txt"
    cpath = EXPORT_DIR / f"{number}_{ts}.csv"

    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    rows = data.get("Results", []) or []
    with open(tpath, "w", encoding="utf-8") as f:
        f.write(f"NERD-OSINT-LOOKUP — {DEVELOPER}\n")
        f.write(f"{CH_TELEGRAM_1}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Number  : {number}\n")
        f.write(f"Time    : {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        for r in rows:
            for k, v in r.items():
                f.write(f"  {str(k):10s} : {v}\n")
            f.write("-" * 60 + "\n")

    if rows:
        with open(cpath, "w", encoding="utf-8", newline="") as f:
            keys = sorted({k for r in rows for k in r.keys()})
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in keys})

    return jpath, tpath, (cpath if rows else None)


def save_bulk(all_results: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = EXPORT_DIR / f"bulk_{ts}.json"
    out_csv  = EXPORT_DIR / f"bulk_{ts}.csv"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    flat = []
    for n, data in all_results.items():
        for r in (data or {}).get("Results", []) or []:
            row = {"query": n}
            row.update(r)
            flat.append(row)

    if flat:
        keys = sorted({k for r in flat for k in r.keys()})
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in flat:
                w.writerow({k: r.get(k, "") for k in keys})

    return out_json, (out_csv if flat else None)

  

# ---------- lookups ----------

def single_lookup():
    console.print("[bold cyan]→ Enter 10-digit mobile number[/bold cyan]")
    number = Prompt.ask("[bold green]  ➤[/bold green]").strip()

    if not validate_number(number):
        console.print("[bold red]✗ Invalid number. 10 digits only.[/bold red]")
        time.sleep(1.5)
        return

    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]checking databases...[/bold green]"),
        transient=True,
    ) as p:
        p.add_task("", total=None)
        time.sleep(random.uniform(0.6, 1.2))
        data = fetch(number)

    SESSION["lookups"] += 1
    console.print()

    if not data or "error" in data:
        err = (data or {}).get("error", "unknown")
        console.print(f"[bold red]✗ engine error: {err}[/bold red]")
        Prompt.ask("[dim]press ENTER to go back[/dim]",
                   default="", show_default=False)
        return

    results = data.get("Results", [])
    if results:
        SESSION["hits"] += 1
        render_hit_alert(number, len(results))
        console.print()
        render_hit_table(results, number)
        jp, tp, cp = save_result(number, data)
        console.print(f"[bold green]✓[/bold green] {jp}")
        console.print(f"[bold green]✓[/bold green] {tp}")
        if cp:
            console.print(f"[bold green]✓[/bold green] {cp}")
    else:
        SESSION["misses"] += 1
        render_clean(number)

    console.print()
    Prompt.ask("[dim]press ENTER to go back[/dim]",
               default="", show_default=False)


def _bulk_worker(n: str):
    time.sleep(random.uniform(0.05, 0.25))
    return n, fetch(n)


def bulk_lookup():
    console.print(
        "[bold cyan]→ Path to file (one number per line)[/bold cyan]")
    path = Prompt.ask("[bold green]  ➤[/bold green]").strip()

    p = Path(path).expanduser()
    if not p.exists():
        console.print("[bold red]✗ File not found.[/bold red]")
        time.sleep(1.5)
        return

    numbers, seen = [], set()
    for line in p.read_text(errors="ignore").splitlines():
        n = line.strip()
        if validate_number(n) and n not in seen:
            seen.add(n)
            numbers.append(n)

    if not numbers:
        console.print("[bold red]✗ No valid numbers in file.[/bold red]")
        time.sleep(1.5)
        return

    workers = 6
    console.print(f"[bold green]✓[/bold green] {len(numbers)} numbers "
                  f"• {workers} workers\n")

    all_results, hits, misses = {}, 0, 0

    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold green]{task.description}[/bold green]"),
        BarColumn(style="green"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
    ) as prog:
        task = prog.add_task("checking...", total=len(numbers))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_bulk_worker, n) for n in numbers]
            for fut in as_completed(futures):
                try:
                    n, data = fut.result()
                except Exception:
                    continue
                all_results[n] = data
                SESSION["lookups"] += 1
                if data and data.get("Results"):
                    hits += 1
                    SESSION["hits"] += 1
                else:
                    misses += 1
                    SESSION["misses"] += 1
                prog.update(task, description=f"checked {n}", advance=1)

    out_json, out_csv = save_bulk(all_results)

    console.print()
    console.print(Panel(
        f"[bold green]✓ Bulk check complete[/bold green]\n\n"
        f"Total  : {len(numbers)}\n"
        f"Leaked : [red]{hits}[/red]\n"
        f"Clean  : [green]{misses}[/green]\n"
        f"JSON   : {out_json}\n"
        + (f"CSV    : {out_csv}\n" if out_csv else ""),
        border_style="green", title="[bold]SUMMARY[/bold]",
    ))
    Prompt.ask("[dim]press ENTER to go back[/dim]",
               default="", show_default=False)


def about_dev():
    clear()
    banner()
    developer_panel()
    console.print()
    console.print(Panel(
        f"[bold white]{BRAND} is a research tool made by "
        f"{DEVELOPER}.[/bold white]\n\n"
        f"[dim]Goal: help people find out if their own number\n"
        f"was leaked in public data breaches.[/dim]\n\n"
        f"[bold yellow]Join our channel for updates:[/bold yellow]\n"
        f"  • {CH_TELEGRAM_1}\n\n"
        f"[bold red]Please do not remove the developer credits.\n"
        f"Removing them breaks the license and stops all support."
        f"[/bold red]",
        border_style="green", title="[bold green]ABOUT[/bold green]",
        box=ROUNDED,
    ))
    console.print()
    Prompt.ask("[dim]press ENTER to go back[/dim]",
               default="", show_default=False)


def session_stats():
    uptime = datetime.now() - SESSION["started"]
    return (
        f"uptime {str(uptime).split('.')[0]}  "
        f"•  lookups {SESSION['lookups']}  "
        f"•  hits {SESSION['hits']}  "
        f"•  clean {SESSION['misses']}"
    )


MENU = """
[bold green]  [1][/bold green]  [white]Check One Number[/white]
[bold green]  [2][/bold green]  [white]Check Many Numbers (from file)[/white]
[bold green]  [3][/bold green]  [white]About Developer[/white]
[bold green]  [4][/bold green]  [white]Session Stats[/white]
[bold green]  [5][/bold green]  [white]Clear Cache[/white]
[bold green]  [6][/bold green]  [white]Check for Updates[/white]
[bold green]  [7][/bold green]  [white]Exit[/white]
"""


def clear_cache():
    n = 0
    for f in CACHE_DIR.glob("*.json"):
        try:
            f.unlink()
            n += 1
        except Exception:
            pass
    console.print()
    console.print(Panel(
        f"[bold green]✓ Cleared {n} cache entries[/bold green]",
        border_style="green"))
    Prompt.ask("[dim]press ENTER to go back[/dim]",
               default="", show_default=False)


def manual_update():
    console.print()
    console.print(Panel(
        "[bold yellow]⚡  MANUAL UPDATE CHECK[/bold yellow]\n\n"
        "[dim]checking github for new commits...[/dim]",
        border_style="yellow"))
    check_for_update()
    Prompt.ask("[dim]press ENTER to go back[/dim]",
               default="", show_default=False)


def main():
    # startup sequence
    check_for_update()

    welcome_animation()
    warning_panel()
    console.print()
    developer_panel()
    console.print()
    Prompt.ask("[bold yellow]press ENTER to start[/bold yellow]",
               default="", show_default=False)

    while True:
        banner()
        console.print(Panel(
            MENU,
            border_style="green",
            title="[bold green]◇ MAIN MENU ◇[/bold green]",
        ))
        console.print(f"[dim]{session_stats()}[/dim]")
        console.print()

        choice = Prompt.ask(
            "[bold green]  ➤ choose option[/bold green]",
            choices=["1", "2", "3", "4", "5", "6", "7"],
            default="1",
        )

        if choice == "1":
            single_lookup()
        elif choice == "2":
            bulk_lookup()
        elif choice == "3":
            about_dev()
        elif choice == "4":
            console.print()
            console.print(Panel(session_stats(),
                                title="[bold]SESSION[/bold]",
                                border_style="green"))
            Prompt.ask("[dim]press ENTER to go back[/dim]",
                       default="", show_default=False)
        elif choice == "5":
            clear_cache()
        elif choice == "6":
            manual_update()
        elif choice == "7":
            console.print()
            console.print(Align.center(Text(
                f"🔥 {BRAND} — stay safe. {DEV_TAG} 🔥",
                style="bold green")))
            footer()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Align.center(Text(
            f"\n🔥 {BRAND} out. {CH_TELEGRAM_1} 🔥",
            style="bold red")))
        sys.exit(0)

  
      
      
