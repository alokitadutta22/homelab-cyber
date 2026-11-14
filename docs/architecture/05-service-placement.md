# Phase 3 — Service Placement and Resource Allocation

**Project:** Homelab Cybersecurity Lab  
**Environment:** Windows 11 + VirtualBox 7.2.22  
**Status:** Service placement designed; implementation pending

---

## 1. Purpose

This document explains which applications, services and security tools will run on each machine in the cybersecurity lab.

The goal is to give every machine a clear responsibility while keeping resource usage manageable.

The lab will initially use two virtual machines:

1. Kali Linux — attacker and security testing machine.
2. Ubuntu Server — target machine and primary source of security logs.

A separate monitoring virtual machine will not be created initially. Instead, Ubuntu will collect its own system and application logs. Centralised monitoring can be introduced later if the laptop has sufficient resources.

## 2. Existing Hardware and Software

| Component | Existing configuration |
|---|---|
| Host operating system | Windows 11 |
| Processor | Intel Core i7-1355U |
| Memory | 16 GB RAM |
| Graphics | Integrated graphics |
| Hypervisor | Oracle VirtualBox 7.2.22 |
| Existing attacker VM | Kali Linux 2026.2 |
| Existing Kali RAM | 2 GB |
| Existing Kali CPUs | 2 |
| Available disk space | Approximately 70 GB at last check |

These values describe the environment observed during the architecture assessment. Available disk space can change as files and virtual machines are added.

## 3. Machine 1 — Windows 11 Host

**Role:** Physical host and hypervisor platform.

Windows is the main operating system on which VirtualBox runs.

### Responsibilities

- Run VirtualBox and manage virtual machines.
- Provide the physical network connection.
- Maintain host-level security through Windows Defender Firewall.
- Store virtual machine files and snapshots.
- Provide controlled management access when required.

### Security considerations

- Keep Windows and VirtualBox updated.
- Avoid unnecessary shared folders between Windows and lab VMs.
- Avoid bidirectional clipboard and drag-and-drop when stronger isolation is required.
- Monitor available disk space before creating additional virtual disks.

Windows will not be used as the vulnerable target machine.

## 4. Machine 2 — Kali Linux

**Role:** Attacker and security testing machine.

An existing Kali Linux 2026.2 VirtualBox VM will be reused.

### Existing allocation

| Resource | Current allocation |
|---|---|
| RAM | 2 GB |
| CPU | 2 virtual CPUs |
| Network | NAT |
| Virtual disk | Dynamic VDI, approximately 18.3 GB currently occupied |

### Responsibilities

Kali will be used to perform controlled security assessments against Ubuntu Server.

Planned activities include:

- Network discovery.
- Port and service enumeration.
- Vulnerability scanning.
- Controlled exploitation exercises.
- Verification of security configurations.

### Planned network

Kali will eventually connect to the Internal Network:

`10.10.10.10/24`

NAT may be used temporarily for software updates. It will be disconnected when unnecessary during isolated exercises.

The existing VM will be reused instead of creating another Kali installation.

## 5. Machine 3 — Ubuntu Server

**Role:** Target machine and primary security monitoring endpoint.

A new Ubuntu Server virtual machine will be created.

It will host the services that Kali will assess.

### Planned responsibilities

- Run SSH for remote administration.
- Host a web service for controlled testing.
- Generate authentication and system logs.
- Run selected services with deliberately introduced vulnerabilities during controlled exercises.
- Collect security events for monitoring and investigation.

### Planned network

`10.10.10.20/24`

Ubuntu will initially have no default gateway on the isolated Internal Network.

A temporary NAT connection may be used for updates and software installation.

### Monitoring responsibilities

Ubuntu will collect its own security-related events, including:

- Systemd journal logs.
- SSH authentication events.
- User login and privilege-related events.
- Application and web-server logs.
- Selected audit events, where appropriate.

These records will help us investigate what happened during an exercise.

Endpoint logs provide visibility into activity recorded by the machine itself. They do not provide complete visibility into every network packet exchanged between machines.

## 6. Monitoring Architecture

**Initial approach: Lightweight endpoint monitoring**

A separate SOC virtual machine would consume additional RAM, CPU and disk space.

With a 16 GB laptop, the initial design will avoid that overhead.

Instead:

1. Ubuntu records system and authentication events.
2. Application services generate their own logs.
3. We inspect and analyse the collected logs.
4. We compare the events with the actions performed from Kali.

A centralised SIEM (Security Information and Event Management) platform may be introduced later.

A SIEM collects and correlates security events from multiple sources to help identify suspicious activity.

It is not part of the initial deployment.

## 7. Vulnerability Management Strategy

The Ubuntu target will begin with a reasonably secure baseline.

We will then introduce selected weaknesses individually for testing.

Examples may include:

- Weak authentication configurations.
- Misconfigured file permissions.
- Unnecessary exposed services.
- Outdated software in controlled conditions.
- Insecure application configurations.

Each exercise will follow this sequence:

1. Establish the normal, secure configuration.
2. Introduce one controlled weakness.
3. Identify the weakness using Kali.
4. Record the evidence.
5. Apply the corrective measure.
6. Verify that the issue has been resolved.

The target will remain isolated during these exercises.

## 8. Resource Allocation Strategy

The laptop has 16 GB of physical RAM. Windows also needs memory for its own applications and background processes.

Therefore, we will avoid allocating all available memory to VirtualBox.

The following are provisional starting allocations, not final settings:

| Machine | Proposed RAM | Proposed CPUs |
|---|---:|---:|
| Kali Linux | 2 GB | 2 |
| Ubuntu Server | 2 GB | 2 |
| Windows host | Remaining memory | Shared physical CPU resources |

The exact Ubuntu allocation will be confirmed after selecting the Ubuntu Server image and checking its requirements.

We will initially run only the two lab VMs when possible.

If a monitoring platform or additional service requires more resources, we will measure actual usage before increasing allocations.

## 9. Storage Strategy

The existing Kali VDI uses dynamic allocation.

This means its virtual disk can grow as data is written, up to its configured maximum capacity.

Ubuntu's virtual disk will also use dynamic allocation unless implementation requirements suggest otherwise.

We will:

- Monitor available Windows disk space.
- Avoid unnecessarily large virtual disks.
- Remove unused installation files where safe.
- Take snapshots before major changes.
- Keep important documentation and configuration files in the project repository.

Snapshots are useful recovery points, but they are not independent backups.

## 10. Planned Service Placement

| Service or tool | Machine | Purpose |
|---|---|---|
| Nmap | Kali | Network and port discovery |
| Vulnerability scanner | Kali | Identify known weaknesses |
| SSH server | Ubuntu | Remote administration and authentication logging |
| Web server | Ubuntu | Target application and service testing |
| Systemd journal | Ubuntu | Collect system events |
| Authentication logs | Ubuntu | Track login activity |
| Application logs | Ubuntu | Record service activity |
| Windows Defender Firewall | Windows | Host-level network protection |
| VirtualBox | Windows | Run and isolate virtual machines |

The exact vulnerability scanner and web server will be selected during implementation.

## 11. Implementation Status

| Component | Status |
|---|---|
| Windows host assessment | Completed |
| Kali VM discovery | Completed |
| Kali resource allocation | Existing |
| Ubuntu Server VM | Not created |
| Internal Network | Planned |
| Ubuntu services | Not deployed |
| Endpoint monitoring | Planned |
| Centralised SIEM | Deferred |
| Controlled vulnerability exercises | Planned |

## 12. Next Steps

1. Finalise the Ubuntu Server image and resource allocation.
2. Create the Ubuntu Server VM.
3. Configure the Internal Network.
4. Assign static IP addresses.
5. Install and secure the initial services.
6. Configure endpoint logging.
7. Validate communication and isolation before security testing.

---

**Milestone:** Service placement and resource strategy designed. No new virtual machines or services have been deployed as part of this design work.
