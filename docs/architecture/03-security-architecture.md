# Phase 3 — Security Architecture

**Project:** Homelab Cybersecurity Lab  
**Platform:** Windows 11 + Oracle VirtualBox + WSL2  
**Status:** Architecture designed; implementation pending  
**Date:** 15 November 2026

---

## 1. Objective

The objective of this phase is to design a segmented cybersecurity homelab that supports three major learning areas:

1. Network Security
2. Security Monitoring and SOC / Blue Team Operations
3. Vulnerability Management

The lab will use separate virtual machines for attacker and target activities, with controlled network communication and lightweight security monitoring.

The design prioritises isolation, repeatability, resource efficiency and practical learning.

## 2. Existing Environment

| Component | Current configuration | Status |
|---|---|---|
| Host OS | Windows 11 | Existing |
| Hypervisor | Oracle VirtualBox 7.2.22 | Existing |
| Attacker VM | Kali Linux 2026.2 | Existing |
| Kali RAM | 2 GB | Existing |
| Kali CPUs | 2 | Existing |
| Supporting environment | Ubuntu on WSL2 | Existing |
| Docker | Docker Desktop | Existing |
| Host-only adapter | 192.168.56.1/24 | Existing |
| Host-only DHCP | Configured | Existing |
| Ubuntu Server VM | Not yet created | Planned |
| Central monitoring VM | Not initially required | Deferred |

The existing Kali VM will be reused. A second hypervisor installation or duplicate Kali VM is unnecessary.

## 3. Machine Roles

### 3.1 Windows 11 Host

Responsibilities:

- Run Oracle VirtualBox.
- Allocate CPU, memory and storage to virtual machines.
- Manage VM configuration and snapshots.
- Provide controlled administrative access.

The Windows host is not an intentionally vulnerable target.

### 3.2 Kali Linux — Attacker

Responsibilities:

- Network reconnaissance.
- Host discovery.
- Port and service enumeration.
- Vulnerability identification.
- Controlled penetration-testing exercises.

The existing Kali VM will be retained.

### 3.3 Ubuntu Server — Target

Responsibilities:

- Run Linux services such as SSH and a web server.
- Provide user accounts and permission configurations.
- Generate authentication, system and application logs.
- Support vulnerability assessment and controlled attack exercises.

The Ubuntu Server will first be configured with a secure baseline.

Selected vulnerabilities and misconfigurations will subsequently be introduced individually in a controlled environment.

This enables comparison between secure and insecure configurations.

### 3.4 Lightweight Monitoring — Defender

The initial monitoring approach will use endpoint-level telemetry rather than a dedicated SOC virtual machine.

Planned monitoring sources include:

- systemd journal logs
- authentication and SSH events
- application and service logs
- selected audit events

The initial exercises will involve collecting, reviewing and correlating these events to identify suspicious activity.

Centralised SIEM deployment can be considered in a later stage.

## 4. Network Architecture

### 4.1 Internal Network

**Name:** `homelab-internal`  
**Subnet:** `10.10.10.0/24`

Purpose:

- Isolate attacker-target communication.
- Prevent direct exposure to the home LAN.
- Provide a controlled environment for security exercises.

Planned addressing:

| Machine | IPv4 address |
|---|---|
| Kali Linux | 10.10.10.10/24 |
| Ubuntu Server | 10.10.10.20/24 |

These are proposed static addresses, not currently assigned addresses.

The Internal Network will not have a default gateway or direct internet route.

### 4.2 Host-only Network

Existing configuration:

- Windows host adapter: `192.168.56.1`
- Network: `192.168.56.0/24`
- VirtualBox DHCP server: enabled
- DHCP allocation range: `192.168.56.101–192.168.56.254`

Purpose:

- Controlled host-to-VM administration.
- Possible future management connectivity.

The host-only network will not be required for the initial attacker-target exercises.

### 4.3 NAT

Purpose:

- Temporary outbound internet access for software installation and updates.

NAT will be enabled only when necessary.

During isolated testing, unnecessary NAT connectivity will be disconnected to reduce unintended network paths.

Bridged networking will not be used for the vulnerable target.

## 5. Communication Policy

| Source | Destination | Intended policy |
|---|---|---|
| Kali | Ubuntu | Permit selected testing traffic |
| Ubuntu | Kali | Permit required responses |
| Windows | Internal Network | No direct connection |
| Public Internet | Ubuntu | No direct exposure |
| Ubuntu | Public Internet | Disabled during isolated exercises |
| Monitoring | Ubuntu telemetry | Collect local endpoint events |

These are architectural intentions. They are not yet implemented firewall rules.

## 6. Monitoring Strategy

The initial implementation will use lightweight endpoint-level monitoring.

The target server will act as the primary source of security events.

The first exercises will focus on:

- Failed SSH authentication attempts.
- Successful and unusual login activity.
- Changes to selected system files.
- Service startup and shutdown events.
- Application errors and suspicious activity.

A limitation of this approach is that endpoint logs do not provide complete network packet visibility.

Network traffic monitoring and centralised log correlation may be added later.

## 7. Vulnerability Management Strategy

The Ubuntu Server will follow a controlled vulnerability lifecycle:

1. Establish a secure baseline.
2. Identify installed services and exposed ports.
3. Perform vulnerability assessments.
4. Introduce selected weaknesses individually.
5. Observe their security impact.
6. Collect relevant evidence and logs.
7. Apply remediation.
8. Repeat the assessment to validate the fix.

All deliberately vulnerable configurations will remain within the isolated lab environment.

## 8. Security Principles

The architecture follows these principles:

- Network segmentation: separate lab traffic from the physical network.
- Least privilege: avoid unnecessary administrative permissions.
- Minimal exposure: enable only required services and ports.
- Controlled vulnerability introduction: avoid uncontrolled weaknesses.
- Observability: preserve logs for investigation.
- Repeatability: use documented IP addresses and configurations.
- Resource efficiency: avoid unnecessary virtual machines and services.

## 9. Resource Strategy

The laptop has 16 GB RAM and approximately 70 GB of free C: drive space at the time of assessment.

The initial design will reuse the existing Kali VM and add one Ubuntu Server VM.

A dedicated monitoring VM is deferred to avoid unnecessary resource consumption.

Final CPU, RAM and virtual disk allocations will be decided after checking the selected Ubuntu Server image and its requirements.

## 10. Implementation Status

| Component | Status |
|---|---|
| Windows host assessment | Completed |
| VirtualBox installation assessment | Completed |
| Existing Kali VM assessment | Completed |
| Host-only network assessment | Completed |
| Internal Network design | Designed |
| Static IP plan | Designed |
| Ubuntu Server VM | Pending |
| Lightweight monitoring | Planned |
| Vulnerability exercises | Planned |
| Firewall implementation | Pending |

## 11. Next Steps

1. Finalise the detailed network design.
2. Document network addressing and communication rules.
3. Decide Ubuntu Server version and installation requirements.
4. Inspect existing Kali VM settings before changing adapters.
5. Create and configure Ubuntu Server.
6. Verify network segmentation.
7. Implement lightweight monitoring.
8. Begin controlled vulnerability assessment exercises.

**Phase 3 architecture design is complete at the conceptual level. Implementation has not yet started.**
