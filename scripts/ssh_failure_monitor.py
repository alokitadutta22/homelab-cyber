
import subprocess
import re
from collections import Counter

THRESHOLD = 3

def get_ssh_logs():
    result = subprocess.run(
        [
            "journalctl",
            "-u", "ssh.service",
            "--since", "today",
            "--no-pager"
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


def detect_failed_logins(logs):
    failed_ips = []

    pattern = r"Failed password for (?:invalid user )?\S+ from (\S+)"

    for line in logs.splitlines():
        match = re.search(pattern, line)

        if match:
            failed_ips.append(match.group(1))

    return Counter(failed_ips)


def main():
    logs = get_ssh_logs()
    ip_counts = detect_failed_logins(logs)

    print("\nSSH Failed Login Monitor")
    print("-----------------------")

    if not ip_counts:
        print("No failed SSH password attempts found today.")
        return

    for ip, count in sorted(ip_counts.items()):
        print(f"{ip}: {count} failed attempts")

        if count >= THRESHOLD:
            print(f"WARNING: {ip} crossed the threshold!")


if __name__ == "__main__":
    main()
