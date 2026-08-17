# lullabyte

a cute little PyQt5 HTTP flood simulator for learning about network traffic and cybersecurity.

> **please be nice.** this tool is only for authorized testing, learning, and research. don't use it against anything you don't own or have explicit permission to test. that's not cool and it's illegal.

---

## what is this?

lullabyte is a hands-on tool for anyone curious about how HTTP traffic works under pressure. whether you're a cybersecurity student, a curious dev, or just want to poke around and learn, this is for you.

you'll get to see firsthand how:
- HTTP flood requests behave at different intensities
- proxy rotation helps mix up where traffic comes from
- GUI apps talk to background threads without freezing
- Python's threading model handles concurrent network calls

---

## features

| what | how it works |
|---|---|
| **three intensity modes** | *soft* (one request at a time), *burst* (threaded), and *flood* (multiplied concurrent threads) |
| **auto proxy rotation** | grabs live proxy lists from multiple sources and rotates through them automatically |
| **live logging** | timestamped logs stream to the console in real time via Qt signals |
| **progress bar** | watch your requests go out with a live progress indicator |
| **user-agent spoofing** | randomly picks a browser fingerprint from a pool of common ones |
| **cross-platform installer** | `install_lullabyte.sh` detects your OS and sets everything up for you |

---

## attack patterns & defenses

if you're studying this from a defensive angle, here's what each pattern looks like and how to block it:

| pattern | what it does | how to defend |
|---|---|---|
| **HTTP GET flood** | fires a lot of GET requests at a server | rate limiting, CAPTCHAs, WAF rules |
| **distributed via proxies** | routes traffic through rotating proxies | deep packet inspection, behavioral analysis |
| **thread amplification** | spawns multiple threads per iteration | connection limits per IP, concurrency throttling |
| **UA randomization** | rotates browser fingerprints to dodge filters | anomaly detection, TLS fingerprinting |

---

## requirements

- python 3.7+
- PyQt5
- requests
- Pillow (for the title rendering)

## installation

```bash
# using the installer (linux/macOS)
chmod +x install_lullabyte.sh
./install_lullabyte.sh

# or just do it yourself
pip install PyQt5 requests Pillow
python3 lullabyte.py
```

## how to use

1. run the app
2. type in your target url (make sure it starts with `http://` or `https://`)
3. pick how many requests you want to send
4. choose an intensity mode
5. toggle proxy rotation if you'd like
6. hit **launch** to start, **stop** to halt

---

## for instructors & students

this is a compact (~250 lines) single-file app that works really well as a classroom exercise:

- **reverse engineering** — look at how the attack thread manages its connections
- **network forensics** — grab the traffic with Wireshark and study request patterns from each mode
- **defensive tooling** — write a Snort or Suricata rule to detect UA rotation or proxy abuse
- **concurrency bugs** — examine thread safety of shared state in `AttackThread`
- **GUI architecture** — study PyQt5 signal/slot patterns for thread-safe UI updates

---

## license

MIT License — see [LICENSE](LICENSE) for details.
