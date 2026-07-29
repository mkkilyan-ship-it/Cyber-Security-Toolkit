"""Scanner de ports TCP (connect scan) à usage pédagogique.

Destiné exclusivement à l'analyse de systèmes vous appartenant ou pour
lesquels vous disposez d'une autorisation explicite.
"""
import argparse
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_PORTS_PER_SCAN = 2048
MAX_WORKERS = 100

COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-alt", 8443: "HTTPS-alt", 27017: "MongoDB",
}


def _service_name(port):
    if port in COMMON_SERVICES:
        return COMMON_SERVICES[port]
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "inconnu"


def scan_port(host, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        return result == 0


def scan_range(host, start_port, end_port, timeout=0.5, max_workers=MAX_WORKERS):
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        raise ValueError("Plage de ports invalide (1-65535).")

    port_count = end_port - start_port + 1
    if port_count > MAX_PORTS_PER_SCAN:
        raise ValueError(f"Trop de ports demandés (max {MAX_PORTS_PER_SCAN} par analyse).")

    try:
        resolved_host = socket.gethostbyname(host)
    except socket.gaierror as exc:
        raise ValueError(f"Impossible de résoudre l'hôte '{host}': {exc}")

    start_time = time.monotonic()
    open_ports = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_port, resolved_host, port, timeout): port
            for port in range(start_port, end_port + 1)
        }
        for future in as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    open_ports.append({"port": port, "service": _service_name(port)})
            except OSError:
                continue

    open_ports.sort(key=lambda p: p["port"])
    duration = round(time.monotonic() - start_time, 2)

    return {
        "host": host,
        "resolved_host": resolved_host,
        "scanned_ports": port_count,
        "open_ports": open_ports,
        "duration_seconds": duration,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scanner de ports TCP - à utiliser uniquement sur des systèmes autorisés."
    )
    parser.add_argument("host")
    parser.add_argument("-p", "--ports", default="1-1024", help="Plage de ports, ex: 1-1024")
    parser.add_argument("-t", "--timeout", type=float, default=0.5)
    args = parser.parse_args()

    start_port, end_port = (int(p) for p in args.ports.split("-"))
    result = scan_range(args.host, start_port, end_port, timeout=args.timeout)

    print(f"Analyse de {result['host']} ({result['resolved_host']}) - "
          f"{result['scanned_ports']} ports en {result['duration_seconds']}s")
    if result["open_ports"]:
        for entry in result["open_ports"]:
            print(f"  {entry['port']}/tcp  ouvert  {entry['service']}")
    else:
        print("  Aucun port ouvert détecté.")


if __name__ == "__main__":
    main()
