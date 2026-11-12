# Phase 2 — WSL2 Security Boundaries and Network Architecture

**Project:** Homelab Cybersecurity Lab  
**Date:** 12 November 2026  
**Environment:** Windows 11 + WSL2 + Ubuntu 26.04.1 LTS + Docker Desktop 4.76.0  
**Status:** Architecture and connectivity investigation completed; no firewall modifications made.

---

## 1. Objective

The objective of Phase 2 was to understand the networking and security boundaries between Windows, Ubuntu on WSL2, Docker Desktop and the external network.

Before deploying cybersecurity services, it is important to understand:

- Which environments are running.
- How they communicate.
- Which IP addresses and network interfaces they use.
- How DNS resolution works.
- Which firewall controls are active.
- Which network ports have inbound exceptions.
- Whether Windows can reach services running inside Ubuntu.

The approach followed was:

**Observe → Understand → Modify → Verify**

No firewall rules or network configurations were modified during this phase.

## 2. Environment overview

| Component | Observed configuration |
|---|---|
| Windows | Windows 11, build 26200.9711 |
| WSL | Version 2.7.8.0 |
| WSL kernel | 6.18.33.1-1 |
| Ubuntu | Ubuntu 26.04.1 LTS |
| Kali Linux | Installed, stopped during inspection |
| Docker Desktop | Version 4.76.0 |
| Docker Engine | 29.5.2 |
| Docker Compose | 5.1.4 |

WSL2 provides a virtualised Linux environment using a Linux kernel. Ubuntu and Kali are separate distributions running under WSL2.

Docker Desktop uses its own WSL integration and internal distribution. The default WSL distribution was found to be `docker-desktop`, so Ubuntu was explicitly selected when running Linux commands.

## 3. Network architecture

### Observed addresses

| Interface or device | Address |
|---|---|
| Windows Wi-Fi | 192.168.0.101 |
| Windows WSL virtual adapter | 172.31.208.1 |
| Ubuntu WSL interface | 172.31.221.32 |
| Ubuntu default gateway | 172.31.208.1 |
| Wi-Fi router | 192.168.0.1 |

Ubuntu's network was `172.31.208.0/20`.

The Ubuntu interface and Windows WSL virtual adapter belong to the same virtual subnet. This is consistent with WSL virtual networking.

The precise active WSL networking mode was not conclusively established from the IP addresses alone.

### Important concepts

- An IP address identifies a network interface.
- A subnet defines an IP address range.
- A gateway provides a route to other networks.
- A virtual network allows virtualised environments to communicate.
- NAT, or Network Address Translation, allows systems to communicate across network boundaries by translating addresses.

## 4. DNS and connectivity

Ubuntu's automatically generated `/etc/resolv.conf` contained:

`nameserver 10.255.255.254`

Windows Wi-Fi was configured to use:

`192.168.0.1`

### DNS test

Command:

`getent hosts github.com`

Result:

`4.186.157.192 github.com`

Conclusion: Ubuntu successfully resolved the domain name.

### HTTPS connectivity test

Command:

`curl -I --max-time 10 https://github.com`

Result:

`HTTP/2 200`

Conclusion: Ubuntu successfully established an HTTPS connection to GitHub and received a successful response.

These checks establish working DNS resolution and outbound HTTPS connectivity at the time of testing. They do not prove that every destination or network port is reachable.

## 5. Windows Defender Firewall

Windows Defender Firewall was enabled for all three profiles.

Effective policy from the ActiveStore:

| Profile | Enabled | Default inbound | Default outbound |
|---|---|---|---|
| Domain | True | Block | Allow |
| Private | True | Block | Allow |
| Public | True | Block | Allow |

The active Wi-Fi connection was classified as Public.

This means inbound traffic is blocked by default unless a rule permits it, while outbound traffic is allowed by default unless restricted.

The Public profile is appropriate for treating untrusted networks cautiously.

## 6. Hyper-V Firewall

WSL was registered as a Hyper-V Firewall virtual-machine creator.

Observed effective settings:

| Setting | Value |
|---|---|
| Enabled | True |
| Default inbound action | Block |
| Default outbound action | Allow |
| Loopback enabled | True |
| Allow host policy merge | True |

The WSLCore rules included inbound exceptions for:

- ICMPv4
- ICMPv6
- mDNS over IPv4
- mDNS over IPv6

These are specific network traffic exceptions. They do not mean all inbound traffic is permitted.

## 7. MySQL-related inbound exceptions

Two persistent local Hyper-V Firewall rules were identified.

| Display name | Protocol | Local port | Direction | Action |
|---|---|---|---|---|
| Port 3306 | TCP | 3306 | Inbound | Allow |
| Port 33060 | TCP | 33060 | Inbound | Allow |

These are conventional MySQL-related ports.

### Investigation results

- MySQL Workbench and other MySQL 8.0.42 tools were installed.
- No matching MySQL/MariaDB Windows service was found.
- No matching running Windows process was found.
- No Windows TCP listener was detected on ports 3306 or 33060.
- No Ubuntu TCP listener was detected on these ports.
- No running Docker containers were publishing ports.

The rules were present in the PersistentStore and identified as locally defined rules. Their description, group and owner fields were empty.

### Assessment

No active listener was identified in the environments checked at the time of inspection.

The origin and purpose of the firewall rules remain unknown. They should be treated as unexplained inbound exceptions until their purpose is established.

No rules were disabled or deleted during this phase.

## 8. Windows-to-Ubuntu connectivity test

A temporary HTTP server was started inside Ubuntu:

`python3 -m http.server 8000 --bind 0.0.0.0`

From Windows PowerShell, the following request was made:

`curl.exe -I --max-time 5 http://172.31.221.32:8000`

Result:

`HTTP/1.0 200 OK`

Conclusion: Windows successfully reached a temporary HTTP service running inside Ubuntu through Ubuntu's WSL virtual IP.

The test demonstrated Windows-to-Ubuntu connectivity. It did not establish that the service was reachable from the local Wi-Fi network or the public Internet.

The temporary server was intended to be stopped with Ctrl+C after testing.

## 9. Linux security controls observed

During the earlier baseline assessment:

- UFW was not installed.
- AppArmor's module was loaded, but its filesystem was not mounted and its service was inactive because the system condition was unmet.
- Windows Defender Firewall and Hyper-V Firewall were enabled.

This means we should not assume that conventional Ubuntu firewall or AppArmor enforcement is currently protecting this WSL environment.

WSL2 security must be considered together with Windows security controls and the virtual networking configuration.

## 10. Security observations and limitations

1. Windows Defender Firewall is enabled for all profiles.
2. Hyper-V Firewall is enabled for WSL with inbound traffic blocked by default.
3. Ubuntu has working DNS resolution and outbound HTTPS connectivity.
4. Windows can reach a temporary HTTP service inside Ubuntu.
5. Two inbound MySQL-related Hyper-V Firewall exceptions exist without a currently identified listener.
6. No active MySQL service was identified in the environments checked.
7. Docker Desktop is installed, but no containers were running during the inspection.
8. The precise WSL networking mode and all possible Windows-to-WSL and LAN-to-WSL traffic paths have not been exhaustively verified.
9. WSL2 is not equivalent to a dedicated isolated physical server.

## 11. Recommended design principles for the homelab

- Keep inbound access restricted by default.
- Expose only the ports required by a specific service.
- Avoid binding services to all network interfaces unless required.
- Document every intentional port exposure.
- Treat Docker access as highly privileged.
- Avoid unnecessary services and containers.
- Preserve Windows Firewall and Hyper-V Firewall protections.
- Investigate unexplained firewall rules before modifying them.
- Account for the limited physical storage and memory available on the laptop.
- Verify service reachability after every network-related configuration change.

## 12. Command reference

| Task | PowerShell | Ubuntu |
|---|---|---|
| Inspect IP configuration | `Get-NetIPConfiguration` | `ip address` |
| Inspect routes | `Get-NetRoute` | `ip route` |
| Inspect listeners | `Get-NetTCPConnection` | `ss -lntp` |
| Inspect processes | `Get-Process` | `ps aux` |
| Inspect services | `Get-Service` | `systemctl` |
| Inspect DNS | `Get-DnsClientServerAddress` | `cat /etc/resolv.conf` |
| Test HTTPS | `curl.exe -I https://github.com` | `curl -I https://github.com` |
| List containers | `docker ps` | `docker ps` |

PowerShell commands manage or inspect Windows. Linux commands inspect or manage Ubuntu. Docker commands communicate with the Docker engine when its integration is available.

## 13. Phase 2 completion

The architecture and connectivity investigation is complete.

No firewall rules, WSL networking settings or security configurations were modified during this phase.

**Next phase:** Design and implement the homelab security architecture, with particular attention to network exposure, service isolation, resource limits and the role of each security component.
