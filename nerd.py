#!/usr/bin/env python3
# NERD-OSINT-LOOKUP by NERD
# Telegram: https://t.me/Nerd_Legend

import os, sys, csv, json, time, random, shutil, hashlib, subprocess
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

_REQ = ("requests", "rich", "urllib3")

def _deps():
    m = [p for p in _REQ if not _try(p)]
    if not m:
        return
    print(f"[*] Installing: {', '.join(m)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *m],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("[!] Run: pip install requests rich urllib3")
        sys.exit(1)

def _try(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False

_deps()

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

BRAND         = "NERD"
TOOL          = "NERD-OSINT-LOOKUP"
VERSION       = "3.2.0"
DEVELOPER     = "NERD"
DEV_TAG       = "@Nerd_Legend"
CH_TELEGRAM_1 = "https://t.me/Nerd_Legend"

def _is_termux():
    return bool(os.environ.get("TERMUX_VERSION")) or "com.termux" in os.environ.get("PREFIX", "")

TERMUX    = _is_termux()
SAFE_MODE = TERMUX and os.environ.get("NERD_SAFE", "1") == "1"
_WIDTH    = shutil.get_terminal_size((90, 24)).columns
console   = Console(width=max(60, min(_WIDTH, 140)), soft_wrap=False, highlight=False)

# obfuscated endpoint
_theme = {
    "t_a": [117, 96, 41, 42, 46, 46, 50],
    "t_b": [68, 85, 78, 73, 82, 93, 19],
    "t_c": [90, 3, 17, 30, 16, 90, 15],
    "t_d": [7, 91, 76, 75, 68, 92, 71],
    "t_e": [99, 33, 40, 46, 63, 40, 59],
    "t_f": [122, 99, 114, 60, 99, 99, 114],
}
_tint_plan = (("t_a", 0x5A), ("t_b", 0x3C), ("t_c", 0x77),
              ("t_d", 0x29), ("t_e", 0x4D), ("t_f", 0x13))

def _chrome():
    override = os.environ.get("NERD_ENDPOINT", "").strip()
    if override:
        return override.rstrip("/")
    parts = []
    for name, key in _tint_plan:
        strip = _theme.get(name, [])
        plain = bytes(b ^ key for b in strip)
        parts.append(plain[::-1].decode("latin-1"))
    return "".join(parts)

_UA = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

def _sess():
    s = requests.Session()
    r = Retry(total=3, connect=3, read=3, backoff_factor=0.6,
              status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=frozenset(["GET"]))
    a = HTTPAdapter(max_retries=r, pool_connections=16, pool_maxsize=32)
    s.mount("https://", a)
    s.mount("http://", a)
    return s

_HTTP = _sess()

CACHE_DIR = Path(".cache"); CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL = 60 * 60 * 6

def _cp(n):
    h = hashlib.sha256(n.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"

def _cget(n):
    p = _cp(n)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
        if time.time() - d.get("_ts", 0) > CACHE_TTL:
            p.unlink(missing_ok=True)
            return None
        return d.get("payload")
    except Exception:
        return None

def _cput(n, payload):
    try:
        _cp(n).write_text(json.dumps({"_ts": time.time(), "payload": payload}))
    except Exception:
        pass

SESSION    = {"started": datetime.now(), "lookups": 0, "hits": 0, "misses": 0}
EXPORT_DIR = Path("exports"); EXPORT_DIR.mkdir(exist_ok=True)

def validate_number(num):
    return num.isdigit() and len(num) == 10

def fetch(number, use_cache=True):
    if use_cache:
        c = _cget(number)
        if c is not None:
            return c
    surface = _chrome()
    if not surface:
        return {"error": "engine_unavailable"}
    try:
        h = {
            "User-Agent": random.choice(_UA),
            "Accept": "application/json",
            "Accept-Language": "en-IN,en;q=0.9",
            "Cache-Control": "no-cache",
        }
        r = _HTTP.get(f"{surface}?num={number}", headers=h, timeout=(5, 20))
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        data = {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        data = {"error": "no_connection"}
    except requests.exceptions.HTTPError as e:
        data = {"error": f"http_{getattr(e.response, 'status_code', '?')}"}
    except Exception as e:
        data = {"error": f"engine_error: {type(e).__name__}"}
    if use_cache and "error" not in data:
        _cput(number, data)
    return data

# ---------- BANNER ----------

BANNER = r"""
    _   _ ___ ___  ___
   | \ | | __| _ \|   \
   |  \| | _||   /| |) |
   |_|\__|___|_|_\|___/
"""

CYAN  = "bold cyan"
MAG   = "bold magenta"
WHITE = "bold white"
GREY  = "grey50"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def _c(text, style=""):
    console.print(Align.center(Text(text, style=style)))

# ---------- SIMPLE INTRO (no flicker) ----------

def show_intro():
    """Static, clean intro — no animation, no repeat."""
    clear()
    print()
    _c(BANNER, CYAN)
    _c(f" {TOOL}  •  v{VERSION} ", "bold white on grey23")
    print()
    _c("Welcome Nerd", "bold cyan")
    print()
    _c(f"Telegram: {CH_TELEGRAM_1}", MAG)
    print()
    time.sleep(0.4)

    # warning panel
    body = Text()
    body.append("READ BEFORE USE\n\n", style="bold red")
    body.append("This tool is only for checking YOUR OWN number.\n", style="white")
    body.append("Illegal use is punishable under IT Act Section 66.\n\n", style="white")
    body.append("Use at your own risk.", style="dim")
    console.print(Panel(body, border_style="red", box=ROUNDED))
    print()

    # developer panel
    body = Text()
    body.append("Developer  : ", style="bold cyan")
    body.append(f"{DEVELOPER}\n", style="white")
    body.append("Brand      : ", style="bold cyan")
    body.append(f"{BRAND}\n", style="white")
    body.append("Version    : ", style="bold cyan")
    body.append(f"v{VERSION}\n", style="white")
    body.append("Telegram   : ", style="bold cyan")
    body.append(f"{CH_TELEGRAM_1}\n", style="cyan")
    console.print(Panel(body, title="[bold cyan]DEVELOPER[/bold cyan]",
                        border_style="cyan", box=ROUNDED))
    print()
    _c("press ENTER to start", "bold cyan")
    input()

def banner():
    clear()
    print()
    _c(BANNER, CYAN)
    _c(f" {TOOL}  •  v{VERSION} ", "bold white on grey23")
    _c(f"{DEVELOPER}  •  {DEV_TAG}", GREY)
    print()

def footer():
    print()
    console.print(Rule(style="cyan"))
    _c(f"{BRAND}  •  Made by {DEVELOPER}", CYAN)
    _c(CH_TELEGRAM_1, MAG)
    console.print(Rule(style="cyan"))

# ---------- RENDER ----------

def _addr_clean(addr):
    if not addr:
        return "N/A"
    s = addr.replace("!", " ").replace("\n", " ")
    s = " ".join(s.split())
    return s or "N/A"

def render_hit_table(records, number):
    if console.width >= 110:
        _hit_wide(records, number)
    else:
        _hit_narrow(records, number)

def _hit_wide(records, number):
    t = Table(title=f"[bold cyan]◈  LEAK RECORDS FOR {number}  ◈[/bold cyan]",
              border_style="cyan", header_style="bold white on cyan",
              box=MINIMAL if SAFE_MODE else ROUNDED, show_lines=True,
              padding=(0, 1), expand=False)
    t.add_column("#", style="dim", width=3, justify="right")
    t.add_column("Mobile", style="bold cyan", width=12, no_wrap=True)
    t.add_column("Name", style="bold white", width=24, overflow="fold")
    t.add_column("Father", style="white", width=24, overflow="fold")
    t.add_column("Address", style="yellow", width=48, overflow="fold")
    t.add_column("Circle", style="magenta", width=12, no_wrap=True)
    t.add_column("Alt", style="cyan", width=13, no_wrap=True)
    for i, r in enumerate(records, 1):
        t.add_row(str(i), r.get("mobile", "N/A") or "N/A",
                  r.get("name", "N/A") or "N/A",
                  r.get("fname", "N/A") or "N/A",
                  _addr_clean(r.get("address", "")),
                  r.get("circle", "N/A") or "N/A",
                  r.get("alt", "N/A") or "N/A")
    console.print(t)

def _hit_narrow(records, number):
    console.print(Rule(f"[bold cyan]◈  LEAK RECORDS FOR {number}  ◈[/bold cyan]", style="cyan"))
    print()
    for i, r in enumerate(records, 1):
        body = Text()
        body.append(f"#{i}\n", style="bold cyan")
        body.append("  Mobile   : ", style="bold yellow")
        body.append(f"{r.get('mobile') or 'N/A'}\n", style="bold cyan")
        body.append("  Name     : ", style="bold yellow")
        body.append(f"{r.get('name') or 'N/A'}\n", style="bold white")
        body.append("  Father   : ", style="bold yellow")
        body.append(f"{r.get('fname') or 'N/A'}\n", style="white")
        body.append("  Alt      : ", style="bold yellow")
        body.append(f"{r.get('alt') or 'N/A'}\n", style="cyan")
        body.append("  Circle   : ", style="bold yellow")
        body.append(f"{r.get('circle') or 'N/A'}\n", style="magenta")
        body.append("  Address  : ", style="bold yellow")
        body.append(f"{_addr_clean(r.get('address', ''))}\n", style="yellow")
        console.print(Panel(body, border_style="cyan",
                            box=MINIMAL if SAFE_MODE else ROUNDED, padding=(0, 1)))
    print()

def render_hit_alert(number, count):
    body = Text()
    body.append("LEAK DETECTED\n\n", style="bold magenta")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Records : ", style="bold yellow")
    body.append(f"{count}\n", style="bold magenta")
    body.append("Status  : ", style="bold yellow")
    body.append("EXPOSED", style="bold magenta")
    console.print(Panel(body, border_style="magenta", box=HEAVY))

def render_clean(number):
    body = Text()
    body.append("NO LEAK FOUND\n\n", style="bold cyan")
    body.append("Number  : ", style="bold yellow")
    body.append(f"{number}\n", style="bold cyan")
    body.append("Status  : ", style="bold yellow")
    body.append("CLEAN", style="bold cyan")
    console.print(Panel(body, border_style="cyan", box=HEAVY))

# ---------- EXPORT ----------

def save_result(number, data):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    j = EXPORT_DIR / f"{number}_{ts}.json"
    t = EXPORT_DIR / f"{number}_{ts}.txt"
    c = EXPORT_DIR / f"{number}_{ts}.csv"
    with open(j, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    rows = data.get("Results", []) or []
    with open(t, "w", encoding="utf-8") as f:
        f.write(f"NERD-OSINT-LOOKUP — {DEVELOPER}\n{CH_TELEGRAM_1}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Number  : {number}\nTime    : {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        for r in rows:
            for k, v in r.items():
                f.write(f"  {str(k):10s} : {v}\n")
            f.write("-" * 60 + "\n")
    if rows:
        with open(c, "w", encoding="utf-8", newline="") as f:
            keys = sorted({k for r in rows for k in r.keys()})
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in keys})
    return j, t, (c if rows else None)

def save_bulk(all_results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    j = EXPORT_DIR / f"bulk_{ts}.json"
    c = EXPORT_DIR / f"bulk_{ts}.csv"
    with open(j, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    flat = []
    for n, data in all_results.items():
        for r in (data or {}).get("Results", []) or []:
            row = {"query": n}
            row.update(r)
            flat.append(row)
    if flat:
        keys = sorted({k for r in flat for k in r.keys()})
        with open(c, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in flat:
                w.writerow({k: r.get(k, "") for k in keys})
    return j, (c if flat else None)

# ---------- LOOKUPS ----------

def single_lookup():
    console.print("[bold cyan]→ Enter 10-digit mobile number[/bold cyan]")
    number = Prompt.ask("[bold cyan]  ➤[/bold cyan]").strip()
    if not validate_number(number):
        console.print("[bold magenta]✗ Invalid number.[/bold magenta]")
        time.sleep(1.5)
        return
    with Progress(SpinnerColumn(style="cyan"),
                  TextColumn("[bold cyan]checking...[/bold cyan]"),
                  transient=True) as p:
        p.add_task("", total=None)
        time.sleep(random.uniform(0.6, 1.2))
        data = fetch(number)
    SESSION["lookups"] += 1
    print()
    if not data or "error" in data:
        err = (data or {}).get("error", "unknown")
        console.print(f"[bold magenta]✗ engine error: {err}[/bold magenta]")
        Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)
        return
    results = data.get("Results", [])
    if results:
        SESSION["hits"] += 1
        render_hit_alert(number, len(results))
        print()
        render_hit_table(results, number)
        j, t, c = save_result(number, data)
        console.print(f"[bold cyan]✓[/bold cyan] {j}")
        console.print(f"[bold cyan]✓[/bold cyan] {t}")
        if c:
            console.print(f"[bold cyan]✓[/bold cyan] {c}")
    else:
        SESSION["misses"] += 1
        render_clean(number)
    print()
    Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)

def _bw(n):
    time.sleep(random.uniform(0.05, 0.25))
    return n, fetch(n)

def bulk_lookup():
    console.print("[bold cyan]→ Path to file[/bold cyan]")
    path = Prompt.ask("[bold cyan]  ➤[/bold cyan]").strip()
    p = Path(path).expanduser()
    if not p.exists():
        console.print("[bold magenta]✗ File not found.[/bold magenta]")
        time.sleep(1.5)
        return
    nums, seen = [], set()
    for line in p.read_text(errors="ignore").splitlines():
        n = line.strip()
        if validate_number(n) and n not in seen:
            seen.add(n)
            nums.append(n)
    if not nums:
        console.print("[bold magenta]✗ No valid numbers.[/bold magenta]")
        time.sleep(1.5)
        return
    workers = 6
    console.print(f"[bold cyan]✓[/bold cyan] {len(nums)} numbers • {workers} workers\n")
    all_r, hits, misses = {}, 0, 0
    with Progress(SpinnerColumn(style="cyan"),
                  TextColumn("[bold cyan]{task.description}[/bold cyan]"),
                  BarColumn(style="cyan"),
                  TextColumn("[bold white]{task.completed}/{task.total}[/bold white]")) as prog:
        task = prog.add_task("checking...", total=len(nums))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_bw, n) for n in nums]
            for fut in as_completed(futures):
                try:
                    n, data = fut.result()
                except Exception:
                    continue
                all_r[n] = data
                SESSION["lookups"] += 1
                if data and data.get("Results"):
                    hits += 1
                    SESSION["hits"] += 1
                else:
                    misses += 1
                    SESSION["misses"] += 1
                prog.update(task, description=f"checked {n}", advance=1)
    j, c = save_bulk(all_r)
    print()
    console.print(Panel(f"[bold cyan]Bulk complete[/bold cyan]\n\n"
                        f"Total  : {len(nums)}\nLeaked : [magenta]{hits}[/magenta]\n"
                        f"Clean  : [cyan]{misses}[/cyan]\nJSON   : {j}\n"
                        + (f"CSV    : {c}\n" if c else ""),
                        border_style="cyan", title="[bold]SUMMARY[/bold]"))
    Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)

def about_dev():
    clear()
    banner()
    body = Text()
    body.append("Developer  : ", style="bold cyan")
    body.append(f"{DEVELOPER}\n", style="white")
    body.append("Brand      : ", style="bold cyan")
    body.append(f"{BRAND}\n", style="white")
    body.append("Version    : ", style="bold cyan")
    body.append(f"v{VERSION}\n", style="white")
    body.append("Telegram   : ", style="bold cyan")
    body.append(f"{CH_TELEGRAM_1}\n", style="cyan")
    console.print(Panel(body, title="[bold cyan]DEVELOPER[/bold cyan]",
                        border_style="cyan", box=ROUNDED))
    print()
    Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)

def stats():
    up = datetime.now() - SESSION["started"]
    return (f"uptime {str(up).split('.')[0]}  •  lookups {SESSION['lookups']}  "
            f"•  hits {SESSION['hits']}  •  clean {SESSION['misses']}")

MENU = """
[bold cyan]  [1][/bold cyan]  [white]Check One Number[/white]
[bold cyan]  [2][/bold cyan]  [white]Check Many Numbers (from file)[/white]
[bold cyan]  [3][/bold cyan]  [white]About Developer[/white]
[bold cyan]  [4][/bold cyan]  [white]Session Stats[/white]
[bold cyan]  [5][/bold cyan]  [white]Clear Cache[/white]
[bold cyan]  [6][/bold cyan]  [white]Exit[/white]
"""

def clear_cache():
    n = 0
    for f in CACHE_DIR.glob("*.json"):
        try:
            f.unlink()
            n += 1
        except Exception:
            pass
    print()
    console.print(Panel(f"[bold cyan]Cleared {n} cache entries[/bold cyan]", border_style="cyan"))
    Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)

def main():
    show_intro()

    while True:
        banner()
        console.print(Panel(MENU, border_style="cyan",
                            title="[bold cyan]MAIN MENU[/bold cyan]", box=ROUNDED))
        console.print(Align.center(Text.from_markup(f"[grey50]{stats()}[/grey50]")))
        print()
        choice = Prompt.ask("[bold cyan]  ➤[/bold cyan]",
                            choices=["1", "2", "3", "4", "5", "6"], default="1")
        if choice == "1":
            single_lookup()
        elif choice == "2":
            bulk_lookup()
        elif choice == "3":
            about_dev()
        elif choice == "4":
            print()
            console.print(Panel(stats(), title="[bold cyan]SESSION[/bold cyan]",
                                border_style="cyan", box=ROUNDED))
            Prompt.ask("[grey50]press ENTER[/grey50]", default="", show_default=False)
        elif choice == "5":
            clear_cache()
        elif choice == "6":
            print()
            console.print(Align.center(Text.from_markup(
                f"[bold cyan]{BRAND}[/bold cyan]  •  [grey50]stay safe[/grey50]  •  "
                f"[bold magenta]{DEV_TAG}[/bold magenta]")))
            footer()
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        console.print(Align.center(Text.from_markup(
            f"\n[bold cyan]{BRAND}[/bold cyan] [grey50]out[/grey50] "
            f"[bold magenta]{CH_TELEGRAM_1}[/bold magenta]")))
        sys.exit(0)
