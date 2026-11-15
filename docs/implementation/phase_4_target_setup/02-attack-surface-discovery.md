# Phase 4 — Attack Surface Discovery

**Project:** Homelab Cybersecurity Lab  
**Date:** 15 November 2026  
**Status:** Initial assessment completed

## 1. Objective

Identify the services running on the Ubuntu target, discover network-accessible ports, inspect SSH configuration and understand the target's attack surface.

**Testing environment:**

| Machine | Role | Internal IP |
|---|---|---|
| Kali Linux | Security testing machine | `10.10.10.10` |
| Ubuntu Server | Target machine | `10.10.10.20` |

## 2. Network Configuration

Both VMs have two network adapters configured in VirtualBox.

| Network | Purpose | Kali | Ubuntu |
|---|---|---|---|
| NAT | Temporary internet access for updates and downloads | DHCP-assigned | DHCP-assigned |
| Internal Network (`homelab-internal`) | Private communication between the two VMs | `10.10.10.10/24` | `10.10.10.20/24` |

**Why two adapters?**

- **NAT:** Allows the VMs to access the internet without directly exposing them as machines on the home network. Useful for installing updates and tools.
- **Internal Network:** Provides a separate private network for Kali and Ubuntu to communicate during security exercises.
- **Static IPs:** Manually assigned addresses ensure that both VMs keep predictable internal addresses after restarting.

**How the static IPs were configured:**

- Ubuntu: Netplan file `/etc/netplan/99-homelab-internal.yaml`, interface `enp0s8`, address `10.10.10.20/24`.
- Kali: NetworkManager connection named `homelab-internal`, interface `eth1`, address `10.10.10.10/24`.

`/24` represents the subnet mask `255.255.255.0`. Both addresses belong to subnet `10.10.10.0/24`.

**Important:** The NAT addresses are DHCP-assigned and may change. The internal static addresses are saved in the VM configurations. NAT remains connected for convenience; it should be disconnected when an exercise requires tighter isolation.

## 3. Attack Surface Discovery Results

### A. Local listening sockets — Ubuntu

Command:

```bash
sudo ss -tulpen
```

| Service | Port | Observation |
|---|---|---|
| SSH | TCP 22 | Listening on all IPv4 and IPv6 interfaces |
| systemd-resolved | TCP/UDP 53 | Local DNS resolver |
| systemd-networkd | UDP 68 | DHCP-related listener on NAT interface |
| chronyd | UDP 323 | Local time synchronisation |

### B. Network scanning — Kali

Initial scan:

```bash
sudo nmap -sS 10.10.10.20
```

Full TCP scan:

```bash
sudo nmap -sS -p- 10.10.10.20
```

**Result:** Only TCP port `22` was open. The remaining 65,534 TCP ports were closed.

### C. SSH service identification

```bash
sudo nmap -sV -p 22 10.10.10.20
```

**Identified service:** OpenSSH `10.2p1`, Ubuntu package revision `2ubuntu3.8`.

### D. SSH configuration review — Ubuntu

```bash
sudo sshd -T
```

Selected effective settings:

| Setting | Value |
|---|---|
| `port` | 22 |
| `maxauthtries` | 6 |
| `permitrootlogin` | prohibit-password |
| `pubkeyauthentication` | yes |
| `passwordauthentication` | yes |
| `permitemptypasswords` | no |

**Observation:** Password and public-key authentication are both enabled. Password authentication requires further security review.

### E. SSH cryptographic algorithms — Kali

```bash
sudo nmap --script ssh2-enum-algos -p 22 10.10.10.20
```

The server advertised modern key exchange and encryption algorithms, along with some older SHA-1-based MAC options. Their presence warrants review but does not automatically establish a vulnerability.

### F. SSH logs — Ubuntu

```bash
sudo journalctl -u ssh.service --no-pager -n 30
```

Observed events included successful password authentication, session creation and closure, and a rejected negotiation attempt from Kali involving the obsolete `diffie-hellman-group1-sha1` algorithm.

## 4. Important Linux Commands — Quick Reference

These are useful commands for this phase and common Linux/security interviews.

| Command | Purpose |
|---|---|
| `pwd` | Show current directory |
| `ls -la` | List files, including hidden files |
| `cd folder` | Change directory |
| `whoami` | Show current username |
| `id` | Show user ID and group membership |
| `sudo command` | Run a command with elevated privileges |
| `ip -brief address` | Show network interfaces and IP addresses |
| `ip route` | Show routing table and default gateway |
| `ping -c 4 IP` | Test network reachability |
| `ss -tulpen` | Show listening TCP/UDP sockets and processes |
| `ps aux` | List running processes |
| `systemctl status service` | Inspect a system service |
| `systemctl list-units --type=service --state=running` | List running services |
| `journalctl -u service` | Read logs for a service |
| `grep -i "text" file` | Search text without case sensitivity |
| `cat file` | Display file contents |
| `less file` | Read a file page by page |
| `df -h` | Check filesystem disk space |
| `free -h` | Check memory usage |
| `uname -r` | Display Linux kernel version |
| `hostnamectl` | Display system and hostname information |

**Interview tip:** Know what a command investigates, what its output tells you, and whether it changes the system. For example, `ss` observes network sockets; it does not open or close ports.

## 5. Key Interview Concepts

- **Attack surface:** All the points through which a system could potentially be accessed or attacked.
- **Port:** A numbered communication endpoint used by network services.
- **Listening socket:** A service waiting for incoming network connections.
- **Static IP:** A manually configured address that remains predictable across restarts.
- **DHCP:** Automatically assigns network configuration, including IP addresses.
- **NAT:** Allows a private VM to access external networks through address translation.
- **TCP SYN scan:** Checks TCP port states using connection-establishment packets without completing the normal handshake.
- **Service version detection:** Attempts to identify the software and version running on an open port.
- **SSH:** Secure remote administration protocol, normally using TCP port 22.

## 6. Final Findings and Limitations

- Ubuntu was reachable from Kali over the internal network.
- Only TCP port 22 was discovered open in the full TCP scan.
- OpenSSH 10.2p1 was identified.
- Password authentication was enabled.
- SSH algorithms and authentication logs were inspected.
- No configuration changes were made during this phase.

**Limitations:** This was an initial TCP attack-surface assessment. UDP reachability, a complete SSH security audit and vulnerability exploitability were not established.

**Next Phase:** Logging and Monitoring — establish a repeatable process to collect, inspect and investigate security events on Ubuntu.
