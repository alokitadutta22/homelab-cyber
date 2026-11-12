# Phase 1 — Understanding and Assessing the Linux Environment

**Project:** Homelab Cybersecurity Lab  
**Date:** 12 November 2026  
**Environment:** Ubuntu 26.04.1 LTS running on WSL2  
**Status:** Initial security assessment completed

---

## 1. What was the objective of this phase?

Before installing cybersecurity tools or changing security configurations, I wanted to understand the existing Linux environment.

This process is called a **Security Baseline Assessment**.

In simple terms, a security baseline is like a health check-up for a computer. Before trying to improve its security, we first need to understand its current condition.

During this assessment, I investigated:

- Which user account was accessing the system?
- What administrative privileges did the user have?
- How was Ubuntu connected to the network?
- Which ports were listening for incoming connections?
- Which background services were running?
- Was a firewall installed?
- Was AppArmor active?
- Were software updates available?

The approach followed was:

**Observe → Understand → Modify → Verify**

We first inspected the system, interpreted the findings, applied available software updates and documented the results.

We did not blindly install security tools or change firewall configurations.

---

## 2. Understanding the environment

Before assessing security, I identified the operating environment.

| Component | Configuration |
|---|---|
| Host operating system | Windows 11 |
| Linux distribution | Ubuntu 26.04.1 LTS |
| Ubuntu codename | Resolute |
| Linux kernel | 6.18.33.1-microsoft-standard-WSL2 |
| Environment | WSL2 |
| Architecture | AMD64 |
| RAM available to Ubuntu | Approximately 7.6 GiB |
| Swap memory | 2 GiB |
| Container platform | Docker Desktop |
| Docker Engine | 29.5.2 |
| Docker Compose | 5.1.4 |

### What is WSL2?

WSL stands for Windows Subsystem for Linux.

It allows us to run a Linux environment directly on Windows without having to install a separate Linux operating system in a traditional virtual machine.

I chose this setup because I already had Ubuntu, Kali Linux and Docker Desktop installed.

It allowed me to reuse my existing laptop instead of consuming additional disk space with another virtual machine.

**Important limitation:** WSL2 is not exactly the same as running Ubuntu Server on a separate machine. Its networking and security boundaries are connected to the Windows host. This must be considered when designing the homelab.

### Commands used

```bash
uname -r
free -h
df -h /
```

- `uname -r` displays the currently running Linux kernel version.
- `free -h` displays available and used memory.
- `df -h /` displays the storage capacity and usage of the Linux root filesystem.

**Storage observation:** The Linux filesystem reported approximately 1 TB of virtual capacity. This does not mean the Windows computer has 1 TB of free physical storage. The Windows C: drive had approximately 39.4 GB free at the time of assessment.

---

## 3. Checking users and administrative privileges

The first security question was: Who has access to the Linux environment, and what can that user do?

In Linux, users have different levels of permissions. Some users can perform ordinary tasks, while authorised administrative users can make system-level changes.

### Commands used

**Command 1:**

```bash
whoami
```

This displays the username of the currently logged-in user.

Observed result:

```text
aloki
```

**Command 2:**

```bash
id
```

This displays the user's numerical identity and group memberships.

Observed result included:

```text
uid=1000(aloki)
gid=1000(aloki)
groups=1000(aloki),4(adm),24(cdrom),27(sudo),
30(dip),46(plugdev),100(users),1001(docker)
```

Important terms:

- UID: User ID, a unique numerical identifier assigned to a user.
- GID: Group ID, a numerical identifier assigned to a group.
- Groups: Collections of users that share certain permissions.

Two memberships were particularly important:

- `sudo`: Provides authorised administrative privileges.
- `docker`: Provides access to Docker functionality.

**Security observation:** Docker group membership is highly privileged. On a conventional Docker daemon setup, a user with Docker access can potentially obtain root-equivalent control over the host.

Therefore, Docker access should be treated as administrative access.

**Command 3:**

```bash
sudo -l
```

This displays the commands the current user is permitted to execute using elevated privileges.

Observed result:

```text
(ALL : ALL) ALL
```

This indicates that the user has unrestricted sudo permissions.

### Why is this important?

If an ordinary user account is compromised, the attacker's access may initially be limited.

However, if that account has administrative privileges, the attacker may be able to make system-level changes.

Understanding user permissions is therefore an important part of a security assessment.

---

## 4. Understanding network configuration

Next, I investigated how the Ubuntu environment was connected to the network.

A computer needs a network interface and an IP address to communicate with other devices.

### Command 4

```bash
ip -brief address
```

This displays network interfaces and their IP addresses in a compact format.

Observed output:

```text
lo    UNKNOWN    127.0.0.1/8
eth0  UP         172.31.221.32/20
```

Understanding the output:

- `lo`: Loopback interface, used by the computer to communicate with itself.
- `eth0`: Network interface used by Ubuntu.
- `127.0.0.1`: Localhost IP address.
- `172.31.221.32`: Private IP address assigned to the Ubuntu interface.

The `UP` state indicates that the `eth0` interface is operational.

### Command 5

```bash
ip route
```

This displays the routing table.

A routing table tells the computer where to send network traffic.

Observed output:

```text
default via 172.31.208.1 dev eth0
172.31.208.0/20 dev eth0 proto kernel scope link src 172.31.221.32
```

The important part is:

```text
default via 172.31.208.1
```

This identifies the default gateway.

A default gateway is the network destination used when there is no more specific route for the traffic.

**Security observation:** Ubuntu was using a private WSL2 virtual network. This is not equivalent to a dedicated, isolated server network.

---

## 5. Identifying listening ports

This was one of the important checks in the assessment.

A port is a communication endpoint used by a service on a computer.

For example:

| Port | Common purpose |
|---|---|
| 22 | SSH remote access |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |

An open or listening port can indicate that a service is waiting for network connections.

Unnecessary exposed services can increase a system's attack surface.

### Command 6

```bash
sudo ss -tulpn
```

This command displays listening TCP and UDP sockets and their associated processes, where available.

Understanding the options:

- `-t`: TCP connections.
- `-u`: UDP connections.
- `-l`: Listening sockets.
- `-p`: Associated processes.
- `-n`: Numerical addresses and port numbers.

### What did we find?

The output showed:

| Port | Protocol | Service or endpoint |
|---|---|---|
| 53 | UDP/TCP | systemd-resolved DNS listeners |
| 53 | UDP | WSL DNS endpoint |
| 323 | UDP | chronyd time synchronisation |

We did not observe SSH (22), HTTP (80) or HTTPS (443) listeners in the supplied Ubuntu socket listing.

### Why does this matter?

Suppose a machine is running an unnecessary remote-access service.

An attacker may scan the machine, discover the listening port and investigate the service behind it.

This is why identifying exposed services is an important part of network security.

**Scope limitation:** This command showed the sockets in the Ubuntu environment. It did not establish which ports were listening on the Windows host.

---

## 6. Investigating running and enabled services

Linux runs several background programs called services.

These services perform tasks such as logging, time synchronisation, networking and scheduled maintenance.

I inspected both running services and services configured to start automatically.

### Command 7

```bash
systemctl list-units --type=service --state=running
```

This lists services that are currently running.

Some services observed:

| Service | Purpose |
|---|---|
| chrony | Maintains accurate system time |
| cron | Executes scheduled tasks |
| dbus | Allows system components to communicate |
| rsyslog | Handles system logs |
| systemd-journald | Collects system journal logs |
| systemd-resolved | Handles DNS resolution |
| systemd-logind | Manages user login sessions |
| unattended-upgrades | Handles automatic package updates |

### Command 8

```bash
systemctl list-unit-files --type=service --state=enabled --no-pager
```

This lists service definitions configured to start automatically when their conditions are met.

The system reported 32 enabled service unit files.

Examples included AppArmor, chrony, cron, snapd, rsyslog and unattended-upgrades.

### Running versus enabled

These terms are not interchangeable.

| Running | Enabled |
|---|---|
| The service is active now. | The service is configured for automatic startup. |
| Describes its current state. | Describes its startup configuration. |

A service can be enabled but not running.

We observed this with AppArmor.

**Security observation:** Not every enabled service is unnecessary. Services should be understood before deciding whether they need to be disabled.

---

## 7. Checking firewall availability

A firewall controls network traffic according to defined security rules.

For example, a firewall can allow SSH connections while blocking unwanted incoming connections.

I checked whether UFW was installed.

UFW stands for **Uncomplicated Firewall**. It is a Linux utility that simplifies firewall management.

### Command 9

```bash
sudo ufw status verbose
```

Observed result:

```text
sudo: 'ufw': command not found
```

This means UFW was not installed in the Ubuntu environment.

### Does this mean there is no firewall?

No.

The absence of UFW does not prove that the system has no firewall protection.

Windows Firewall, WSL networking and Linux packet-filtering mechanisms are separate considerations.

We deliberately did not install or enable UFW during the baseline assessment because we first need to understand how firewall rules interact with WSL2 networking.

---

## 8. Checking AppArmor

AppArmor is a Linux security mechanism that restricts what applications are allowed to do.

It uses security profiles to limit an application's access to files, resources and system capabilities.

For example, a security profile can restrict an application from accessing files outside its permitted directory.

This helps reduce the damage an application could cause if it were compromised.

### Commands used

**Command 10**

```bash
systemctl is-active apparmor
```

Checks whether the AppArmor service is active.

Observed result:

```text
inactive
```

**Command 11**

```bash
sudo aa-status
```

Displays the current AppArmor status and loaded profiles.

Observed result:

```text
apparmor module is loaded.
apparmor filesystem is not mounted.
```

**Command 12**

```bash
systemctl status apparmor --no-pager
```

Provides detailed information about the AppArmor service.

The important output was:

```text
Active: inactive (dead)
Condition: start condition unmet
ConditionSecurity=apparmor was not met
```

### What does this mean?

The AppArmor kernel module was loaded, but its security filesystem was not mounted.

Systemd skipped starting the AppArmor service because its required security condition was not met.

Therefore, we did not establish that AppArmor was actively enforcing security profiles in this Ubuntu environment.

**Security observation:** We recorded this as an environment limitation associated with our WSL2 setup. We did not attempt to force-start AppArmor.

---

## 9. Checking and applying software updates

Keeping software updated is an important part of system security.

Updates can include security fixes, bug fixes and improvements.

I first checked whether any installed packages had newer versions available.

### Command 13

```bash
sudo apt update
```

This refreshes the local package information from configured Ubuntu repositories.

It does not install updates.

The repositories responded successfully, and Ubuntu reported that 29 packages could be upgraded.

### Command 14

```bash
apt list --upgradable
```

This lists packages for which newer versions are available.

### Simulating the upgrade

Before installing anything, I wanted to understand what changes Ubuntu intended to make.

**Command 15**

```bash
sudo apt-get -s upgrade
```

The `-s` option runs the operation in simulation mode.

It calculates the proposed changes without actually installing the upgrades.

The simulation reported:

| Category | Result |
|---|---:|
| Packages to upgrade | 25 |
| New packages to install | 0 |
| Packages to remove | 0 |
| Packages deferred due to phasing | 4 |

### What is phased updating?

Ubuntu sometimes distributes updates gradually instead of releasing them to every system simultaneously.

This process is called phased updating.

It helps Ubuntu detect potential problems before a wider rollout.

We did not force the four deferred packages to upgrade.

### Applying the updates

**Command 16**

```bash
sudo apt upgrade
```

This installed the 25 available package upgrades.

### Verifying the package state

**Command 17**

```bash
apt list --upgradable
```

After the upgrade, only the four phased packages remained.

**Command 18**

```bash
sudo apt-get check
```

This checks the package system for dependency problems.

The command completed successfully.

### Why did we do this?

Running outdated software can leave known vulnerabilities unpatched.

Applying available updates helps keep the system maintained and reduces exposure to vulnerabilities that have already been fixed by software vendors.

---

## 10. Verifying the kernel version

Finally, I confirmed which Linux kernel was running.

### Command 19

```bash
uname -r
```

Observed output:

```text
6.18.33.1-microsoft-standard-WSL2
```

The `microsoft-standard-WSL2` suffix identifies this as the WSL2 kernel.

This confirms that our Ubuntu environment is running through WSL2 rather than booting an independent Linux kernel.

---

## 11. What did the assessment reveal?

After completing the checks, these were the main findings:

| Area | Finding |
|---|---|
| User privileges | Primary user has unrestricted sudo privileges |
| Docker access | User belongs to the Docker group |
| Network | Ubuntu uses a private WSL2 virtual network |
| Listening ports | DNS and time-synchronisation listeners observed |
| SSH listener | Not observed in the supplied Ubuntu output |
| HTTP/HTTPS listeners | Not observed in the supplied Ubuntu output |
| Running services | 14 services observed |
| Enabled service files | 32 listed |
| UFW | Not installed |
| AppArmor | Not actively enforcing profiles |
| Package updates | 25 upgrades successfully applied |
| Remaining updates | 4 packages deferred by phasing |
| Package consistency | apt-get check completed successfully |

---

## 12. What did we change?

It is important to distinguish between inspecting a system and modifying it.

During this phase:

**We inspected:**
- User permissions and group memberships.
- Network interfaces and routing.
- Listening ports.
- Running and enabled services.
- Firewall availability.
- AppArmor status.
- Available software updates.

**We changed:**
- Applied 25 available Ubuntu package upgrades.

**We deliberately did not change:**
- User privileges or group memberships.
- Firewall rules.
- AppArmor configuration.
- Network configuration.
- Running system services.

This ensures that the baseline remains a record of the original environment, apart from the documented package maintenance.

---

## 13. Important limitations of our environment

Our setup uses WSL2, so some security configurations behave differently from a conventional standalone Linux server.

The following limitations must be considered in later phases:

1. WSL2 uses a virtualised Linux environment integrated with Windows.
2. Its networking is not equivalent to a dedicated isolated server network.
3. Windows Firewall and Linux firewall behaviour must be considered together.
4. AppArmor was not found to be actively enforcing profiles.
5. The Ubuntu socket listing does not represent every listening port on the Windows host.

These limitations will influence how we design and test the security controls.

---

## 14. Next steps

The next milestone is to understand the security boundary between Windows and WSL2.

We will investigate:

1. The installed WSL version and networking configuration.
2. Windows Firewall settings.
3. How network traffic moves between Windows and Ubuntu.
4. Which firewall and hardening controls are appropriate for this environment.

After that, we can begin implementing and testing security controls.

---

## 15. Learning and interview preparation

The Linux commands used in this phase are important for understanding system administration and cybersecurity.

Some particularly useful commands to remember:

| Command | Purpose |
|---|---|
| `whoami` | Identify current user |
| `id` | Inspect user and group memberships |
| `sudo -l` | Inspect administrative permissions |
| `ip -brief address` | Inspect network interfaces |
| `ip route` | Inspect routing table |
| `ss -tulpn` | Inspect listening ports |
| `systemctl` | Inspect and manage services |
| `ufw status` | Inspect UFW firewall status |
| `aa-status` | Inspect AppArmor |
| `apt update` | Refresh package information |
| `apt upgrade` | Install available package updates |
| `uname -r` | Identify running kernel |

The objective is not simply to memorise commands.

I should understand:
- What each command does.
- Why it was used.
- What its output means.
- What security conclusion can reasonably be drawn from that output.

**Phase 1 milestone:** Initial security baseline assessment completed and documented.

**Next milestone:** WSL2 security boundaries and hardening strategy.
