#!/usr/bin/env python3
# ============================================================
#   NERD-OSINT-LOOKUP
#   Made by : NERD
#   Telegram : https://t.me/Nerd_Legend
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
    print(f"[*] Installing: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("[!] Run: pip install requests rich urllib3")
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
    print(f"[!] Missing: {e}")
    sys.exit(1)

BRAND       = "NERD"
TOOL        = "NERD-OSINT-LOOKUP"
VERSION     = "3.2.0"
DEVELOPER   = "NERD"
DEV_TAG     = "@Nerd_Legend"
CH_TELEGRAM_1 = "https://t.me/Nerd_Legend"
_CANARY = "NERD::DO_NOT_STRIP::6767"
REPO_URL      = "https://github.com/urcybernothing/ADVANCE-NUM-LOOKUP.git"
UPDATE_BRANCH = "main"

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
    for token in (DEVELOPER, CH_TELEGRAM_1, _CANARY, "Made by : NERD"):
        if token not in src:
            return False
    return True

def _self_destruct(reason="credit_removed"):
    try:
        c = Console()
        c.print(Panel(f"[bold red]✗ INTEGRITY VIOLATION[/bold red]\n{reason}",
                      border_style="red", box=HEAVY))
    except Exception:
        print(f"[!] {reason}")
    try:
        Path(__file__).write_text("# NERD-OSINT-LOOKUP — destroyed.\n")
    except Exception:
        pass
    sys.exit(1)

if not _verify_credits():
    _self_destruct("credit_removed")

def _is_termux() -> bool:
    return bool(os.environ.get("TERMUX_VERSION")) or "com.termux" in os.environ.get("PREFIX", "")

TERMUX    = _is_termux()
SAFE_MODE = TERMUX and os.environ.get("NERD_SAFE", "1") == "1"

_WIDTH = shutil.get_terminal_size((90, 24)).columns
console = Console(width=max(60, min(_WIDTH, 140)), soft_wrap=False, highlight=False)

theme = {
    "t_a": [117, 96, 41, 42, 46, 46, 50],
    "t_b": [68, 85, 78, 73, 82, 93, 19],
    "t_c": [90, 3, 17, 30, 16, 90, 15],
    "t_d": [7, 91, 76, 75, 68, 92, 71],
    "t_e": [99, 33, 40, 46, 63, 40, 59],
    "t_f": [122, 99, 114, 60, 99, 99, 114],
}
_tint_plan = (("t_a", 0x5A), ("t_b", 0x3C), ("t_c", 0x77),
              ("t_d", 0x29), ("t_e", 0x4D), ("t_f", 0x13))

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

def _burn(_s): del _s

_UA_POOL = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def _build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, connect=3, read=3, backoff_factor=0.6,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]))
    adapter = HTTPAdapter(max_retries=retry, pool_connections=16, pool_maxsize=32)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

_HTTP = _build_session()

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
        _cache_path(number).write_text(json.dumps({"_ts": time.time(), "payload": payload}))
    except Exception:
        pass

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
        r = _HTTP.get(f"{surface}?num={number}", headers=headers, timeout=(5, 20))
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

def check_for_update():
    if os.environ.get("NERD_NO_UPDATE") == "1":
        return
    if shutil.which("git") is None:
        return
    repo = Path(__file__).resolve().parent
    try:
        remote = subprocess.run(["git", "remote", "get-url", "origin"],
                                cwd=repo, capture_output=True, text=True, timeout=5)
        if remote.returncode != 0 or remote.stdout.strip().lower() != REPO_URL.lower():
            return
        fetch_r = subprocess.run(["git", "fetch", "origin", UPDATE_BRANCH],
                                 cwd=repo, capture_output=True, text=True, timeout=30)
        if fetch_r.returncode != 0:
            return
        result = subprocess.run(["git", "rev-list", "--count", f"HEAD..origin/{UPDATE_BRANCH}"],
                                cwd=repo, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return
        commits = int(result.stdout.strip() or "0")
        if commits <= 0:
            return
    except Exception:
        return

# ---------- BANNER ----------

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

def _center(text, style=""):
    console.print(Align.center(Text(text, style=style)))

# ---------- CINEMATIC ANIMATIONS ----------

import random as _rand

def sparkle_intro(duration=1.2):
    try:
        cols = console.width
        rows = min(shutil.get_terminal_size((80, 20)).lines - 2, 14)
    except Exception:
        cols, rows = 80, 14
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    end = time.time() + duration
    chars = ["·", "∙", "•", "✦", "✧", "*", "°"]
    try:
        while time.time() < end:
            buf = [[" " for _ in range(cols)] for _ in range(rows)]
            for _ in range(_rand.randint(10, 22)):
                r = _rand.randint(0, rows - 1)
                c = _rand.randint(0, cols - 1)
                buf[r][c] = _rand.choice(chars)
            out = []
            for row in buf:
                line = "".join(f"\033[1;32m{ch}\033[0m" if ch != " " else " " for ch in row)
                out.append(line)
            sys.stdout.write("\033[H" + "\n".join(out))
            sys.stdout.flush()
            time.sleep(0.08)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        clear()

# ---------- AESTHETIC ANIMATIONS ----------

# premium palette — cyan & magenta only
CYAN   = "bold cyan"
MAG    = "bold magenta"
DIM_C  = "cyan"
DIM_M  = "magenta"
WHITE  = "bold white"


def _center(text, style=""):
    console.print(Align.center(Text(text, style=style)))


def _sleep(ms):
    time.sleep(ms / 1000)


def soft_banner(delay=0.35):
    """Banner fade-in — 3 steps, smooth."""
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    steps = [
        ("bold grey50", 0.2),
        (CYAN, 0.25),
        (WHITE, 0.3),
    ]
    clear()
    for style, d in steps:
        clear()
        _center(art, style)
        _sleep(d * 1000)

    # subtitle appears after banner
    _sleep(200)
    _center(f"  {TOOL}  •  v{VERSION}  ", "bold white on grey23")
    _sleep(180)
    console.print()


def welcome_typing():
    """
    'Welcome Nerd' — ek line mein smooth typing,
    cyan → white gradient ke saath.
    """
    text = "Welcome Nerd"
    # per-character colour: cyan → magenta gradient feel
    palette = [CYAN, CYAN, DIM_C, DIM_C, WHITE, WHITE, DIM_C, DIM_C, MAG, MAG, CYAN, CYAN]

    t = Text()
    for i, ch in enumerate(text):
        t.append(ch, style=palette[i % len(palette)])
        console.print(Align.center(t), end="\r")
        _sleep(65)

    sys.stdout.write("\n\n")
    sys.stdout.flush()


def loading_bar(text="Initializing", duration=1.8, width=26):
    """Sleek loading bar — cyan fill only. No rainbow."""
    steps = int(duration / 0.035)
    for i in range(steps + 1):
        pct = i / steps
        filled = int(width * pct)
        bar = "▓" * filled + "░" * (width - filled)
        line = f"  [grey50]{text}[/grey50]  [cyan]{bar}[/cyan]  [white]{int(pct*100):3d}%[/white]"
        console.print(Align.center(Text.from_markup(line)), end="\r")
        sys.stdout.flush()
        _sleep(35)
    sys.stdout.write("\n")
    sys.stdout.flush()


def loading_spinner(text="Connecting", duration=1.2):
    """Soft rotating spinner — aesthetic braille dots."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        console.print(
            Align.center(Text.from_markup(
                f"[cyan]{frames[i % len(frames)]}[/cyan]  [grey50]{text}[/grey50]"
            )),
            end="\r"
        )
        sys.stdout.flush()
        _sleep(85)
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def welcome_animation():
    """Full cinematic intro — 6 seconds, pure elegance."""

    # Stage 1: soft banner fade-in
    soft_banner()

    # Stage 2: subtitle details
    _center("◆   O S I N T   L O O K U P   ◆", DIM_C)
    _sleep(280)
    _center(f"by {DEVELOPER}", "grey50")
    _sleep(280)
    console.print()

    # Stage 3: Welcome Nerd typing
    welcome_typing()

    # Stage 4: separator
    _center("· · · · · · · · · · · · · · · · · · ·", "grey30")
    _sleep(300)

    # Stage 5: telegram
    _center(f"Telegram  →  {CH_TELEGRAM_1}", DIM_M)
    _sleep(300)
    console.print()

    # Stage 6: loading bar
    loading_bar("Starting engine", duration=1.6)

    # Stage 7: spinner
    loading_spinner("Initializing modules", duration=1.0)

    _sleep(300)
    clear()


def warn_fade_in():
    """Warning panel fade-in."""
    for shade in ["grey30", "grey50", "grey70", "red"]:
        clear()
        _center(BANNER_SAFE if SAFE_MODE else BANNER_ASCII, CYAN)
        console.print()
        body = Text()
        body.append("READ BEFORE USE\n\n", style=f"bold {shade}")
        body.append("This tool is only for checking YOUR OWN number.\n", style="grey70")
        body.append("Illegal use is punishable under IT Act Section 66.\n\n", style="grey70")
        body.append("Use at your own risk.", style="grey50")
        console.print(Panel(body, border_style=shade, box=ROUNDED))
        _sleep(120)


def dev_fade_in():
    """Developer panel fade-in."""
    for shade in ["grey30", "grey50", "cyan"]:
        body = Text()
        body.append("Developer  : ", style=f"bold {shade}")
        body.append(f"{DEVELOPER}\n", style="white")
        body.append("Brand      : ", style=f"bold {shade}")
        body.append(f"{BRAND}\n", style="white")
        body.append("Version    : ", style=f"bold {shade}")
        body.append(f"v{VERSION}\n", style="white")
        body.append("Telegram   : ", style=f"bold {shade}")
        body.append(f"{CH_TELEGRAM_1}\n", style="cyan")
        console.print(Panel(body,
                            title=f"[{shade}]◇  DEVELOPER  ◇[/{shade}]",
                            border_style=shade, box=ROUNDED))
        _sleep(180)


def banner():
    """Menu banner — clean, minimal, elegant."""
    clear()
    art = BANNER_SAFE if SAFE_MODE else BANNER_ASCII
    _center(art, CYAN)
    _center(f" {TOOL}  •  v{VERSION} ", "bold white on grey23")
    _center(f"{DEVELOPER}  •  {DEV_TAG}", "grey50")
    console.print()

# ---------- PANELS ----------

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
    console.print(Panel(body,
        title="[bold green]◇  DEVELOPER  ◇[/bold green]",
        subtitle="[dim]NERD[/dim]", border_style="green", box=ROUNDED))

def warning_panel():
    body = Text()
    body.append("⚠  READ BEFORE USE\n\n", style="bold red")
    body.append("This tool is only for checking YOUR OWN number.\n", style="bold white")
    body.append("Illegal use is punishable under IT Act Section 66.\n\n", style="bold white")
    body.append("Use at your own risk.", style="dim")
    console.print(Panel(body, border_style="red", box=HEAVY))

def footer():
    console.print()
    console.print(Rule(style="green"))
    console.print(Align.center(Text(
        f"🔥  {BRAND}  •  Made by {DEVELOPER}  •  {DEV_TAG}  🔥", style="bold green")))
    console.print(Align.center(Text(CH_TELEGRAM_1, style="bold cyan")))
    console.print(Rule(style="green"))

# ---------- RENDERING ----------

def _addr_clean(addr):
    if not addr:
        return "N/A"
    s = addr.replace("!", " ").replace("\n", " ")
    s = " ".join(s.split())
    return s or "N/A"

def render_hit_table(records, number):
    if console.width >= 110:
        _render_hit_table_wide(records, number)
    else:
        _render_hit_table_narrow(records, number)

def _render_hit_table_wide(records, number):
    table = Table(title=f"[bold green]◈  LEAK RECORDS FOR {number}  ◈[/bold green]",
                  border_style="green", header_style="bold white on green",
                  box=MINIMAL if SAFE_MODE else ROUNDED, show_lines=True,
                  padding=(0, 1), expand=False)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Mobile", style="bold cyan", width=12, no_wrap=True)
    table.add_column("Name", style="bold white", width=24, overflow="fold")
    table.add_column("Father", style="white", width=24, overflow="fold")
    table.add_column("Address", style="yellow", width=48, overflow="fold")
    table.add_column("Circle", style="magenta", width=12, no_wrap=True)
    table.add_column("Alt", style="cyan", width=13, no_wrap=True)
    for i, rec in enumerate(records, 1):
        table.add_row(str(i), rec.get("mobile", "N/A") or "N/A",
                      rec.get("name", "N/A") or "N/A",
                      rec.get("fname", "N/A") or "N/A",
                      _addr_clean(rec.get("address", "")),
                      rec.get("circle", "N/A") or "N/A",
                      rec.get("alt", "N/A") or "N/A")
    console.print(table)

def _render_hit_table_narrow(records, number):
    console.print(Rule(f"[bold green]◈  LEAK RECORDS FOR {number}  ◈[/bold green]", style="green"))
    console.print()
    for i, rec in enumerate(records, 1):
        body = Text()
        body.append(f"#{i}\n", style="bold green")
        def line(label, value, style="white"):
            body.append(f"  {label:<9}: ", style="bold yellow")
            body.append(f"{value or 'N/A'}\n", style=style)
        line("Mobile", rec.get("mobile"), "bold cyan")
        line("Name", rec.get("name"), "bold white")
        line("Father", rec.get("fname"), "white")
        line("Alt", rec.get("alt"), "cyan")
        line("Circle", rec.get("circle"), "magenta")
        body.append("  Address  : ", style="bold yellow")
        body.append(f"{_addr_clean(rec.get('address', ''))}\n", style="yellow")
        if rec.get("email"):
            line("Email", rec.get("email"), "white")
        if rec.get("id"):
            line("ID", rec.get("id"), "dim")
        console.print(Panel(body, border_style="green",
                            box=MINIMAL if SAFE_MODE else ROUNDED, padding=(0, 1)))
    console.print()

def render_hit_alert(number, count):
    body = Text()
    body.append("⚠   LEAK DETECTED   ⚠\n\n", style="bold red")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Records : ", style="bold yellow")
    body.append(f"{count}\n", style="bold red")
    body.append("Status  : ", style="bold yellow")
    body.append("EXPOSED", style="bold red")
    console.print(Panel(body, border_style="red", box=HEAVY))

def render_clean(number):
    body = Text()
    body.append("✓   NO LEAK FOUND\n\n", style="bold green")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Status  : ", style="bold yellow")
    body.append("CLEAN", style="bold green")
    console.print(Panel(body, border_style="green", box=HEAVY))

# ---------- EXPORT ----------

def save_result(number, data):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jpath = EXPORT_DIR / f"{number}_{ts}.json"
    tpath = EXPORT_DIR / f"{number}_{ts}.txt"
    cpath = EXPORT_DIR / f"{number}_{ts}.csv"
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    rows = data.get("Results", []) or []
    with open(tpath, "w", encoding="utf-8") as f:
        f.write(f"NERD-OSINT-LOOKUP — {DEVELOPER}\n{CH_TELEGRAM_1}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Number  : {number}\nTime    : {datetime.now().isoformat()}\n")
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

def save_bulk(all_results):
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

# ---------- LOOKUPS ----------

def single_lookup():
    console.print("[bold cyan]→ Enter 10-digit mobile number[/bold cyan]")
    number = Prompt.ask("[bold green]  ➤[/bold green]").strip()
    if not validate_number(number):
        console.print("[bold red]✗ Invalid number.[/bold red]")
        time.sleep(1.5)
        return
    with Progress(SpinnerColumn(style="green"),
                  TextColumn("[bold green]checking...[/bold green]"),
                  transient=True) as p:
        p.add_task("", total=None)
        time.sleep(random.uniform(0.6, 1.2))
        data = fetch(number)
    SESSION["lookups"] += 1
    console.print()
    if not data or "error" in data:
        err = (data or {}).get("error", "unknown")
        console.print(f"[bold red]✗ engine error: {err}[/bold red]")
        Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)
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
    Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)

def _bulk_worker(n):
    time.sleep(random.uniform(0.05, 0.25))
    return n, fetch(n)

def bulk_lookup():
    console.print("[bold cyan]→ Path to file[/bold cyan]")
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
        console.print("[bold red]✗ No valid numbers.[/bold red]")
        time.sleep(1.5)
        return
    workers = 6
    console.print(f"[bold green]✓[/bold green] {len(numbers)} numbers • {workers} workers\n")
    all_results, hits, misses = {}, 0, 0
    with Progress(SpinnerColumn(style="green"),
                  TextColumn("[bold green]{task.description}[/bold green]"),
                  BarColumn(style="green"),
                  TextColumn("[bold white]{task.completed}/{task.total}[/bold white]")) as prog:
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
    console.print(Panel(f"[bold green]✓ Bulk complete[/bold green]\n\n"
                        f"Total  : {len(numbers)}\nLeaked : [red]{hits}[/red]\n"
                        f"Clean  : [green]{misses}[/green]\nJSON   : {out_json}\n"
                        + (f"CSV    : {out_csv}\n" if out_csv else ""),
                        border_style="green", title="[bold]SUMMARY[/bold]"))
    Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)

def about_dev():
    clear()
    banner()
    developer_panel()
    console.print()
    console.print(Panel(f"[bold white]{BRAND} research tool by {DEVELOPER}.[/bold white]\n\n"
                        f"[dim]Check if YOUR number leaked.[/dim]\n\n"
                        f"[bold yellow]Telegram:[/bold yellow]\n  • {CH_TELEGRAM_1}\n\n"
                        f"[bold red]Do not remove credits.[/bold red]",
                        border_style="green", title="[bold green]ABOUT[/bold green]", box=ROUNDED))
    console.print()
    Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)

def session_stats():
    uptime = datetime.now() - SESSION["started"]
    return (f"uptime {str(uptime).split('.')[0]}  •  lookups {SESSION['lookups']}  "
            f"•  hits {SESSION['hits']}  •  clean {SESSION['misses']}")

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
    console.print(Panel(f"[bold green]✓ Cleared {n} cache entries[/bold green]", border_style="green"))
    Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)

def manual_update():
    console.print()
    console.print(Panel("[bold yellow]⚡  MANUAL UPDATE CHECK[/bold yellow]\n\n"
                        "[dim]checking github...[/dim]", border_style="yellow"))
    check_for_update()
    Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)

def main():
    check_for_update()
    welcome_animation()
    warning_panel()
    console.print()
    developer_panel()
    console.print()
    Prompt.ask("[bold yellow]press ENTER to start[/bold yellow]", default="", show_default=False)

    while True:
        banner()
        console.print(Panel(MENU, border_style="green",
                            title="[bold green]◇ MAIN MENU ◇[/bold green]"))
        console.print(f"[dim]{session_stats()}[/dim]")
        console.print()
        choice = Prompt.ask("[bold green]  ➤ choose[/bold green]",
                            choices=["1","2","3","4","5","6","7"], default="1")
        if choice == "1": single_lookup()
        elif choice == "2": bulk_lookup()
        elif choice == "3": about_dev()
        elif choice == "4":
            console.print()
            console.print(Panel(session_stats(), title="[bold]SESSION[/bold]", border_style="green"))
            Prompt.ask("[dim]press ENTER[/dim]", default="", show_default=False)
        elif choice == "5": clear_cache()
        elif choice == "6": manual_update()
        elif choice == "7":
            console.print()
            console.print(Align.center(Text(f"🔥 {BRAND} — stay safe. {DEV_TAG} 🔥", style="bold green")))
            footer()
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Align.center(Text(f"\n🔥 {BRAND} out. {CH_TELEGRAM_1} 🔥", style="bold red")))
        sys.exit(0)
