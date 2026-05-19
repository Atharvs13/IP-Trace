import socket
import threading
import csv
import time
import datetime
import os
import json
from queue import Queue, Empty
from colorama import Fore, Style


class PortScanner:
    def __init__(self, services_file=None, threads=100, max_threads=200, timeout=1.0):
        # Resolve services file relative to the package if not provided
        if services_file is None:
            services_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "services.csv"))

        self.services_file = services_file
        self.services = self.load_services(self.services_file)

        # Prevent thread abuse and validate values
        self.max_threads = int(max_threads)
        try:
            requested = int(threads)
        except Exception:
            requested = 100
        self.threads = max(1, min(requested, self.max_threads))

        self.timeout = float(timeout)
        self.queue = Queue()
        self.results = []
        self.print_lock = threading.Lock()
        self.log_file = None  # optional logging

    def set_log_file(self, filename):
        self.log_file = filename

    def write_log(self, message):
        if not self.log_file:
            return
        try:
            # Ensure log directory exists if part of path
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            with self.print_lock:
                print(Fore.RED + f"[-] Failed to write to log file: {e}" + Style.RESET_ALL)

    def load_services(self, csv_file):
        services = {}
        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        services[int(row["port"])] = row["service"]
                    except Exception:
                        continue
        except FileNotFoundError:
            with self.print_lock:
                print(Fore.RED + f"[-] Services file not found at {csv_file}. Continuing with unknown services." + Style.RESET_ALL)
        except Exception as e:
            with self.print_lock:
                print(Fore.RED + f"[-] Error loading services file: {e}" + Style.RESET_ALL)
        return services

    def is_host_alive(self, ip):
        """
        Check if host is alive by probing a set of common ports.
        """
        common_ports = [80, 443, 22, 445, 3389]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.6)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            except Exception:
                # Non-fatal network error; continue probing other ports
                continue
        return False

    def grab_banner(self, ip, port):
        """Attempts to grab a short banner from the service where possible."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((ip, port))

            # Basic HTTP probe to trigger a response
            if port in (80, 8080, 8000, 8081, 8888):
                try:
                    sock.sendall(b"HEAD / HTTP/1.0\r\nHost: localhost\r\n\r\n")
                except Exception:
                    pass

            try:
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            except Exception:
                banner = ""
            sock.close()

            if banner:
                return banner.split("\n")[0][:120]
        except Exception:
            return ""
        return ""

    def worker(self, ip):
        while True:
            try:
                port = self.queue.get_nowait()
            except Empty:
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip, port))

                if result == 0:
                    service = self.services.get(port, "Unknown")
                    banner = self.grab_banner(ip, port)

                    banner_text = f" [{banner}]" if banner else ""

                    with self.print_lock:
                        print(
                            Fore.GREEN + "[OPEN]" + Style.RESET_ALL +
                            f" {ip:<15} : {port:<5} " +
                            Fore.CYAN + f"({service})" + Style.RESET_ALL +
                            (Fore.LIGHTBLACK_EX + banner_text + Style.RESET_ALL if banner else "")
                        )

                    self.results.append({
                        "ip": ip,
                        "port": port,
                        "service": service,
                        "banner": banner
                    })

                    self.write_log(f"{ip}:{port} OPEN ({service}){banner_text}")

                sock.close()
                time.sleep(0.005)
            except Exception as e:
                # Log but do not crash worker thread
                self.write_log(f"Error scanning {ip}:{port} - {e}")
            finally:
                try:
                    self.queue.task_done()
                except Exception:
                    pass

    def validate_ports(self, start_port, end_port):
        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
            raise ValueError("Ports must be between 1 and 65535")
        if start_port > end_port:
            raise ValueError("Start port must be less than or equal to end port")

    def scan_ports(self, ip, start_port, end_port):
        self.validate_ports(start_port, end_port)

        for port in range(start_port, end_port + 1):
            self.queue.put(port)

        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, args=(ip,))
            t.daemon = True
            t.start()

        self.queue.join()

    def save_results(self, filename):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=4, ensure_ascii=False)
            with self.print_lock:
                print(Fore.YELLOW + f"\n[+] Results saved to {filename}" + Style.RESET_ALL)
        except Exception as e:
            with self.print_lock:
                print(Fore.RED + f"\n[-] Failed to save results: {e}" + Style.RESET_ALL)
