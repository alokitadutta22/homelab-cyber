# Phase 5: SSH Failure Monitoring

## Objective
Implement basic SSH authentication monitoring on the Ubuntu target VM.

## 1. Log Collection
Used systemd journal to inspect SSH authentication events.

Command:
`sudo journalctl -u ssh.service --since "today" --no-pager`

Verified successful and failed SSH login events.

## 2. Source IP Detection
Used grep, awk, sort and uniq to extract and count failed login attempts by source IP.

Test result:
- Source IP: 10.10.10.10 (Kali VM)
- Failed attempts: 3

## 3. Python Detection Script
Created `scripts/ssh_failure_monitor.py`.

The script:
- Reads SSH logs using Python subprocess.
- Uses regular expressions to extract source IP addresses.
- Uses Counter to count failed attempts per IP.
- Generates a warning when an IP reaches the configured threshold.

Configured threshold: 3 failed attempts per IP.

## 4. Verification
Executed:

`sudo python3 scripts/ssh_failure_monitor.py`

Observed:

- 10.10.10.10: 3 failed attempts
- WARNING: 10.10.10.10 crossed the threshold!

The script was also tested from its final location in the repository.

## 5. Limitations
- Checks today's journal entries when executed.
- Does not run continuously.
- Does not automatically block IP addresses.
- A threshold warning indicates repeated failures, not confirmed malicious activity.

## Outcome
Implemented and verified a basic SSH failed-login detection mechanism using systemd journal logs and Python.
