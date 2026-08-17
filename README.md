# LULLABYTE

A PyQt5-based HTTP flood simulation tool built **for educational and cybersecurity research purposes**.

> **Disclaimer:** This tool is intended exclusively for authorized security testing, penetration testing education, and academic research. Unauthorized use against systems you do not own or have explicit written permission to test is illegal and unethical. The authors assume no liability for misuse.

---

## Why This Exists

LULLABYTE is designed as a **teaching aid for cybersecurity students** and professionals studying network traffic patterns, denial-of-service mechanics, and defensive countermeasures. By examining the source code, students can learn:

- How HTTP flood attacks generate and distribute request traffic
- The role of proxy rotation in evading basic rate-limiting
- How GUI applications interact with background networking threads
- Thread management and concurrency patterns in Python (PyQt5 `QThread`)

---

## Features

| Feature | Description |
|---|---|
| **Multi-mode attack simulation** | Three distinct modes — *Stealth* (sequential requests), *Rage* (threaded bursts), and *Overkill* (multiplied concurrent threads) — demonstrate escalating levels of HTTP flood intensity |
| **Auto-fetched proxy rotation** | Pulls live public HTTP proxy lists from multiple sources and randomly rotates through them per request, simulating real-world distributed traffic patterns |
| **Real-time logging** | Timestamped request logs streamed to a live GUI console via Qt signals, illustrating proper thread-to-UI communication |
| **Progress tracking** | A progress bar updates in real time as simulated requests complete |
| **User-Agent spoofing** | Randomizes the `User-Agent` header from a pool of common browser strings |
| **Cross-platform installer** | `install_lullabyte.sh` detects your OS (Fedora, Debian, Arch, macOS) and installs all dependencies automatically |

---

## Threats & Attack Patterns Demonstrated

Understanding these patterns is critical for building effective defenses:

| Attack Pattern | How It Works | Defensive Countermeasure |
|---|---|---|
| **HTTP GET Flood** | Sends a high volume of GET requests to overwhelm the target server's ability to respond | Rate limiting, CAPTCHAs, WAF rules |
| **Distributed requests via proxies** | Routes traffic through rotating public proxies to mask origin and bypass IP-based blocks | Deep packet inspection, behavioral analysis, geo-filtering |
| **Thread amplification (Overkill mode)** | Spawns multiple threads per iteration to multiply request volume exponentially | Connection limits per IP, concurrency throttling |
| **User-Agent randomization** | Rotates browser fingerprints to evade basic signature-based filtering | Anomaly detection on request patterns, TLS fingerprinting |

---

## Requirements

- Python 3.7+
- PyQt5
- requests

## Installation

```bash
# Using the installer (Linux/macOS)
chmod +x install_lullabyte.sh
./install_lullabyte.sh

# Or manually
pip install PyQt5 requests
python3 lullabyte.py
```

## Usage

```
1. Launch the application
2. Enter the target URL (must start with http:// or https://)
3. Set the number of requests
4. Select an attack mode
5. Toggle proxy rotation as needed
6. Click LAUNCH LULLABYTE to begin / ABORT to stop
```

---

## For Instructors & Students

This codebase is a compact (~300 lines) single-file application that can serve as a practical exercise in:

- **Reverse engineering** — Analyze how the attack thread spawns and manages connections
- **Network forensics** — Capture the traffic with Wireshark and study request patterns from each mode
- **Defensive tooling** — Write a Snort/Suricata rule that detects the UA rotation or proxy abuse patterns
- **Concurrency bugs** — Examine the thread safety of shared state in `AttackThread`
- **GUI architecture** — Study PyQt5 signal/slot patterns for thread-safe UI updates

---

## License

MIT License — see [LICENSE](LICENSE) for details.
