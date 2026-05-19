import argparse
import ipaddress
from core import PortScanner
from colorama import init, Fore, Style

init(autoreset=True)

import platform
import datetime

def show_banner():
    print(Fore.MAGENTA + "=" * 75)

    print(Fore.CYAN + r"""
                         AthrvSec Recon Engine
                         Developed by Sassy
                         GitHub: Atharvs13
                         
""")

    print(Fore.YELLOW + "           AthrvSec Network Recon Tool")
    print(Fore.GREEN + "           Multithreaded TCP IP & Port Scanner")
    print(Fore.BLUE +  "           Developed by: Sassy")
    print(Fore.BLUE +  "           GitHub: Atharvs13")
    print(Fore.BLUE +  f"           System: {platform.system()} {platform.release()}")
    print(Fore.BLUE +  f"           Started: {datetime.datetime.now()}")

    print(Fore.MAGENTA + "=" * 75)
    print(Style.RESET_ALL)

def main():
    show_banner() 

    parser = argparse.ArgumentParser(description="TCP IP & Port Scanner")
    parser.add_argument("-t", "--target", required=True,
                        help="Target IP or CIDR (e.g. 192.168.1.0/24)")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Port range (default 1-1024)")
    parser.add_argument("--threads", type=int, default=100,
                        help="Number of threads (default 100)")
    parser.add_argument("-o", "--output", help="Save results to JSON file")

    args = parser.parse_args()

    try:
        network = ipaddress.ip_network(args.target, strict=False)
    except ValueError:
        print(Fore.RED + "[-] Invalid IP or CIDR range")
        return

    start_port, end_port = map(int, args.ports.split("-"))

    scanner = PortScanner(threads=args.threads)

    print(Fore.BLUE + f"\n[*] Scanning: {network}")
    print(Fore.BLUE + f"[*] Ports: {start_port}-{end_port}\n")

    for ip in network.hosts():
        ip = str(ip)
        if scanner.is_host_alive(ip):
            print(Fore.GREEN + f"\n[+] Host Alive: {ip}")
            scanner.scan_ports(ip, start_port, end_port)
        else:
            print(Fore.RED + f"[-] Host Down: {ip}")

    if args.output:
        scanner.save_results(args.output)

if __name__ == "__main__":
    main()
