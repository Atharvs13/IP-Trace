# 🔍 IP-Trace

**AthrvSec Recon Engine** – A multithreaded TCP IP & Port Scanner built in Python for fast network reconnaissance.

> ⚠️ This tool is intended for **authorized security testing and educational purposes only**. Only scan networks and systems you own or have explicit permission to test.

---

## Features

* 🚀 Multithreaded TCP port scanning
* 🌐 Scan a single IP or an entire CIDR subnet
* 📡 Host discovery before port scanning
* ⚡ Customizable port ranges
* 🧵 Adjustable thread count
* 📄 Export scan results to JSON
* 🎨 Colored terminal output
* 🖥️ Cross-platform (Windows, Linux, macOS)

---

## Project Structure

```text
IP-Trace/
├── core.py
├── main.py
├── requirements.txt
├── README.md
└── output/
```

---

## Requirements

* Python 3.9+
* colorama

Install dependencies:

```bash
pip install -r requirements.txt
```

or

```bash
pip install colorama
```

---

## Usage

Scan the default TCP ports (1–1024):

```bash
python main.py -t 192.168.1.10
```

Scan an entire subnet:

```bash
python main.py -t 192.168.1.0/24
```

Scan custom ports:

```bash
python main.py -t 192.168.1.10 -p 20-1000
```

Increase scanning speed:

```bash
python main.py -t 192.168.1.10 --threads 500
```

Save results:

```bash
python main.py -t 192.168.1.10 -o results.json
```

---

## Command Line Options

| Option         | Description                     |
| -------------- | ------------------------------- |
| `-t, --target` | Target IP address or CIDR range |
| `-p, --ports`  | Port range (Default: `1-1024`)  |
| `--threads`    | Number of scanning threads      |
| `-o, --output` | Save scan results as JSON       |

---

## Example

```bash
python main.py -t 192.168.1.0/24 -p 1-1000 --threads 300 -o results.json
```

---

## Sample Output

```text
===========================================================================
AthrvSec Recon Engine
Developed by Sassy
GitHub: Atharvs13
===========================================================================

[*] Scanning: 192.168.1.0/24
[*] Ports: 1-1024

[+] Host Alive: 192.168.1.1
    22/tcp   OPEN
    80/tcp   OPEN
    443/tcp  OPEN
```

---

## Roadmap

* [ ] UDP scanning
* [ ] Service/version detection
* [ ] Banner grabbing
* [ ] OS fingerprinting
* [ ] Progress bar
* [ ] HTML/PDF reports
* [ ] XML and CSV export
* [x] IPv6 support

---

## Disclaimer

This software is provided for educational purposes and authorized security assessments only. The author is not responsible for any misuse or damage resulting from the use of this tool.

---

## Author

**AthrvSec**

Developed by **Sassy**

GitHub: https://github.com/Atharvs13

---

## License

This project is licensed under the MIT License.
