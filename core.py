import socket
import threading
import csv
import time
import datetime
from queue import Queue
from colorama import Fore, Style

class PortScanner:
    def __init__(self, services_file="services.csv", threads=100):
        self.services = self.load_services(services_file)
        self.threads = threads
        self.queue = Queue()
        self.results = []
        self.print_lock = threading.Lock()
        self.log_file = None  # optional logging

    def write_log(self, message):
        if self.log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")

    def load_services(self, csv_file):
        services = {}
        try:
            with open(csv_file, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    services[int(row["port"])] = row["service"]
        except FileNotFoundError:
            print(Fore.RED + "[-] services.csv not found." + Style.RESET_ALL)
        return services

    def is_host_alive(self, ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 80))
            sock.close()
            return result == 0
        except:
            return False

    def worker(self, ip):
        while not self.queue.empty():
            port = self.queue.get()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))

                if result == 0:
                    service = self.services.get(port, "Unknown")

                    with self.print_lock:
                        print(
                            Fore.GREEN + "[OPEN]" + Style.RESET_ALL +
                            f" {ip}:{port} " +
                            Fore.CYAN + f"({service})" + Style.RESET_ALL
                        )

                    self.results.append({
                        "ip": ip,
                        "port": port,
                        "service": service
                    })

                    # logging happens AFTER service is defined
                    log_message = f"{ip}:{port} OPEN ({service})"
                    self.write_log(log_message)

                sock.close()
                time.sleep(0.01)

            except Exception as e:
                pass

            self.queue.task_done()

    def scan_ports(self, ip, start_port, end_port):
        for port in range(start_port, end_port + 1):
            self.queue.put(port)

        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, args=(ip,))
            t.daemon = True
            t.start()

        self.queue.join()

    def save_results(self, filename):
        import json
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)

        print(Fore.YELLOW + f"\n[+] Results saved to {filename}" + Style.RESET_ALL)
