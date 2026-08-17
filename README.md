# LULLABYTE

A fun little PyQt5 HTTP flood simulator made for learning about cybersecurity.

> **Heads up:** This tool is strictly for authorized security testing, learning, and research. Please don't use it against anything you don't own or have permission to test, that's not cool and it's illegal.

---

## What's This All About?

LULLABYTE was built as a hands on learning tool for cybersecurity students and anyone curious about how network traffic works. It's a great way to get your feet wet with:

- Understanding how HTTP flood attacks work and how traffic gets distributed
- Seeing how proxy rotation helps avoid basic rate-limiting
- Learning how GUI apps talk to background network threads
- Playing with thread management and concurrency in Python (PyQt5 `QThread`)

---

## What Can It Do?

| Feature | What It Does |
|---|---|
| **Three attack modes** | *Stealth* (sequential requests), *Rage* (threaded bursts), and *Overkill* (multiplied concurrent threads) — each one shows a different level of HTTP flood intensity |
| **Auto proxy rotation** | Grabs live public proxy lists from multiple sources and rotates through them, just like real distributed traffic |
| **Real-time logging** | Timestamped logs stream to the GUI console via Qt signals — a nice way to see thread-to-UI communication in action |
| **Progress tracking** | A live progress bar that updates as requests go out |
| **User-Agent spoofing** | Randomizes the `User-Agent` header from a pool of common browser strings |
| **Cross-platform installer** | `install_lullabyte.sh` figures out your OS (Fedora, Debian, Arch, macOS) and installs everything for you |

---

## Threats & Attack Patterns

Understanding these is key to building good defenses:

| Attack Pattern | How It Works | How To Defend |
|---|---|---|
| **HTTP GET Flood** | Fires a ton of GET requests at a server to overwhelm it | Rate limiting, CAPTCHAs, WAF rules |
| **Distributed requests via proxies** | Routes traffic through rotating proxies to hide the origin | Deep packet inspection, behavioral analysis, geo-filtering |
| **Thread amplification (Overkill mode)** | Spawns multiple threads per iteration to multiply request volume | Connection limits per IP, concurrency throttling |
| **User-Agent randomization** | Rotates browser fingerprints to dodge basic signature filtering | Anomaly detection on request patterns, TLS fingerprinting |

---

## Requirements

- Python 3.7+
- PyQt5
- requests

## Installation

```bash
# using the installer (Linux/macOS)
chmod +x install_lullabyte.sh
./install_lullabyte.sh

# or just do it manually
pip install PyQt5 requests
python3 lullabyte.py
```

## How To Use It

```
1. Fire up the app
2. Type in the target URL (needs to start with http:// or https://)
3. Set how many requests you want to send
4. Pick an attack mode
5. Toggle proxy rotation if you want
6. Hit LAUNCH LULLABYTE to start or ABORT to stop
```

---

## For Instructors & Students

This is a compact (~300 lines) single-file app that works great as a practical exercise:

- **Reverse engineering** — Look at how the attack thread spawns and manages connections
- **Network forensics** — Grab the traffic with Wireshark and study the request patterns from each mode
- **Defensive tooling** — Write a Snort/Suricata rule to detect UA rotation or proxy abuse
- **Concurrency bugs** — Check out the thread safety of shared state in `AttackThread`
- **GUI architecture** — Study PyQt5 signal/slot patterns for thread-safe UI updates

---

## License

MIT License — see [LICENSE](LICENSE) for the full details.
