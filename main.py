#!/usr/bin/env python3
"""athrvsec-recon main entrypoint

Usage examples:
  python main.py -t 192.168.1.0/24 -p 1-1024 --threads 100 -o results.json --log logs/scan.log
"""
import argparse
import ipaddress
import datetime
import os
from colorama import init, Fore, Style

from core.scanner import PortScanner


def show_banner():
    init(autoreset=True)
    print(Fore.MAGENTA + "=" * 75)
    print(Fore.CYAN + r"""
                         AthrvSec Recon Engine
                         Professional TCP/IP & Port Scanner
                         https://github.com/atharvs13/athrvsec-recon.git
    """)
    print(Fore.RED + "           Multithreaded TCP IP & Port Scanner")
    print(Fore.GREEN + f"        Started: {datetime.datetime.now()}")
    print(Fore.MAGENTA + "=" * 75)
    print(Style.RESET_ALL)


def parse_ports(ports_str):
    try:
        if "-" in ports_str:
            start, end = ports_str.split("-", 1)
            return int(start), int(end)
        p = int(ports_str)
        return p, p
    except Exception:
        raise argparse.ArgumentTypeError("Invalid port range. Use e.g. 1-1024 or 80")


def main():
    show_banner()

    parser = argparse.ArgumentParser(description="AthrvSec Recon Engine - TCP/IP & Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target IP or CIDR (e.g. 192.168.1.0/24 or 8.8.8.8)")
    parser.add_argument("-p", "--ports", default="1-1024", help="Port range (default 1-1024)")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads (default 100)")
    parser.add_argument("--max-threads", type=int, default=200, help="Maximum allowed threads (default 200)")
    parser.add_argument("--log", help="Write scan log to file (optional)")
    parser.add_argument("-o", "--output", help="Save results to JSON file (optional)")

    args = parser.parse_args()

    try:
        start_port, end_port = parse_ports(args.ports)
    except Exception as e:
        print(Fore.RED + f"[-] {e}")
        return

    # Resolve targets (network or single IP)
    try:
        network = ipaddress.ip_network(args.target, strict=False)
        hosts = list(network.hosts())
        if not hosts:
            hosts = [network.network_address]
    except ValueError:
        try:
            hosts = [ipaddress.ip_address(args.target)]
        except ValueError:
            print(Fore.RED + "[-] Invalid target IP or CIDR")
            return

    scanner = PortScanner(threads=args.threads, max_threads=args.max_threads)
    if args.log:
        scanner.set_log_file(args.log)
    else:
        # default log file path (optional)
        logdir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logdir):
            os.makedirs(logdir, exist_ok=True)
        default_log = os.path.join(logdir, f"scan-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log")
        scanner.set_log_file(default_log)

    print(Fore.BLUE + f"\n[*] Ports: {start_port}-{end_port}\n")

    for ip in hosts:
        ip_str = str(ip)
        try:
            alive = scanner.is_host_alive(ip_str)
        except Exception:
            alive = False

        if alive:
            print(Fore.GREEN + f"\n[+] Host Alive: {ip_str}")
            try:
                scanner.scan_ports(ip_str, start_port, end_port)
            except Exception as e:
                print(Fore.RED + f"[-] Error scanning {ip_str}: {e}")
        else:
            print(Fore.RED + f"[-] Host Down: {ip_str}")

    if args.output:
        try:
            scanner.save_results(args.output)
        except Exception as e:
            print(Fore.RED + f"[-] Failed to save results: {e}")


if __name__ == "__main__":
    main()
