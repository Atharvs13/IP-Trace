<<<<<<< HEAD
# athrvsec-recon
=======
# AthrvSec Recon

Professional TCP/IP & Port Scanner designed for network reconnaissance and quick service identification.

Features
- Multithreaded TCP port scanner with safe thread limits
- Service detection using a packaged `services.csv`
- Basic banner grabbing for HTTP/SSH-like services
- Optional logging to file and clean JSON output
- Modular design: scanner moved into `core/scanner.py`

Installation
1. Clone the repository and change into the `athrvsec-recon` directory:

```bash
git clone <repo-url>
cd athrvsec-recon
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix / macOS
source venv/bin/activate

pip install -r requirements.txt
```

Usage

Scan a CIDR range (default ports 1-1024):

```bash
python main.py -t 192.168.1.0/24 -p 1-1024 --threads 100 -o results.json --log logs/scan.log
```

Scan a single host and save results:

```bash
python main.py -t 8.8.8.8 -p 53 -o google-dns.json
```

Notes
- The tool respects a `--max-threads` option to avoid resource abuse. Do not raise threads beyond what your environment can handle.
- `data/services.csv` is used to map common ports to service names.

Disclaimer
This tool is intended for authorized security testing and network administration only. Do not use it to scan systems without explicit permission. The authors are not responsible for misuse.
>>>>>>> eaf31de (Initial Commit - AthrvSec Recon Tool)
