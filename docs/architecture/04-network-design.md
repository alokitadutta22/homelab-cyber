# Phase 3 — Network Design

**Project:** Homelab Cybersecurity Lab  
**Environment:** Windows 11 + VirtualBox 7.2.22  
**Status:** Network design proposed; implementation pending

---

## 1. Purpose

This document explains how the virtual machines in the cybersecurity lab will communicate.

The main goal is to create a controlled network where Kali Linux can test an Ubuntu Server machine without exposing the target machine directly to the home network or the internet.

The network will use three connection types:

1. Internal Network — communication between lab virtual machines.
2. Host-only Network — optional communication between the Windows host and lab virtual machines.
3. NAT — temporary internet access for updates and software installation.

These networks serve different purposes and should not be treated as interchangeable.

## 2. Network Overview

The planned architecture is:

```text
                 WINDOWS 11 HOST
                        |
                ORACLE VIRTUALBOX
                        |
          +-------------+-------------+
          |             |             |
       Internal      Host-only       NAT
       Network       Network       Connection
          |             |             |
      10.10.10.0/24 192.168.56.0/24  Internet
          |
     +----+----------------+
     |                     |
  KALI LINUX          UBUNTU SERVER
  Attacker            Target
  10.10.10.10         10.10.10.20
```

The diagram represents the planned design, not the current configuration.

## 3. Network 1 — Internal Network

**Purpose:** Isolated communication between Kali Linux and Ubuntu Server.

| Property | Planned value |
|---|---|
| VirtualBox network type | Internal Network |
| Network name | `homelab-internal` |
| Subnet | `10.10.10.0/24` |
| Kali Linux IP | `10.10.10.10` |
| Ubuntu Server IP | `10.10.10.20` |
| Address assignment | Static |
| Default gateway | None |
| DNS server | None initially |

An Internal Network is a private virtual network that allows connected VirtualBox virtual machines to communicate with one another.

The Windows host does not automatically become a member of this network.

### Why use static IP addresses?

A static IP address is manually assigned rather than automatically provided by DHCP.

Using fixed addresses makes the lab easier to understand and troubleshoot.

For example:

- Kali will always use `10.10.10.10`.
- Ubuntu Server will always use `10.10.10.20`.

The `/24` portion means that both machines belong to the same local IP network, `10.10.10.0/24`.

### Why no default gateway?

A default gateway is the network device a machine uses when it needs to communicate outside its local network.

The isolated network does not need a gateway for Kali and Ubuntu to communicate with each other.

Leaving the gateway unconfigured also avoids creating an unnecessary route from the lab network to another network.

## 4. Network 2 — Host-only Network

**Purpose:** Optional management access between Windows and a virtual machine.

An existing VirtualBox Host-only adapter was discovered on the Windows host.

| Property | Existing value |
|---|---|
| Network | `192.168.56.0/24` |
| Windows host IP | `192.168.56.1` |
| DHCP server address | `192.168.56.100` |
| DHCP lease range | `192.168.56.101–192.168.56.254` |
| DHCP server | Enabled |

A Host-only Network allows the Windows host and connected virtual machines to communicate without automatically providing internet access.

The existing adapter is available, but no lab VM has been confirmed as connected to it.

### Planned use

Host-only networking may be used later for controlled management access, such as connecting from Windows to a VM.

It is not required for the initial Kali-to-Ubuntu exercises.

Static addresses for any VM connected to this network will be decided separately. They must not conflict with the existing DHCP lease range.

## 5. Network 3 — NAT

**Purpose:** Temporary internet access.

NAT stands for Network Address Translation.

VirtualBox NAT allows a virtual machine to access external networks through the host's network connection.

The existing Kali VM currently uses an individual NAT connection.

### Planned use

NAT will be used when a virtual machine needs to:

- Download operating system updates.
- Install required packages.
- Download security tools.
- Retrieve necessary software.

After the required downloads and updates are complete, unnecessary NAT connections will be disconnected before isolated testing.

A named VirtualBox NAT Network is not currently configured. Individual VM NAT and a named NAT Network are different VirtualBox features.

## 6. IP Address Allocation

The following addresses are proposed for the Internal Network.

| Machine | Role | IP address |
|---|---|---|
| Kali Linux | Attacker / testing machine | `10.10.10.10/24` |
| Ubuntu Server | Target / workload machine | `10.10.10.20/24` |

Both machines will use:

- Subnet mask: `255.255.255.0`
- Default gateway: None on the Internal Network
- DNS: None initially on the Internal Network

These addresses have not yet been assigned.

## 7. Communication Policy

The lab will follow these initial communication rules:

| Source | Destination | Policy |
|---|---|---|
| Kali Linux | Ubuntu Server | Allow selected testing traffic |
| Ubuntu Server | Kali Linux | Allow required responses |
| Windows host | Internal Network | No direct connection by default |
| Internet | Ubuntu Server | No direct exposure |
| Ubuntu Server | Internet | Disable during isolated exercises |
| Windows host | Host-only-connected VM | Allow only when management access is required |

The exact ports and protocols will be documented when the target services are selected.

Allowing selected testing traffic does not mean opening every port.

## 8. Isolation and Safety

The following precautions will be followed:

1. Do not use Bridged networking for the vulnerable target.
2. Do not expose the Ubuntu target directly to the home Wi-Fi network.
3. Disconnect unnecessary NAT adapters during isolated exercises.
4. Avoid unnecessary network adapters on either VM.
5. Use snapshots before introducing vulnerabilities or changing important configurations.
6. Verify network connectivity before beginning each exercise.

A snapshot is a saved state of a virtual machine that can help restore it to an earlier condition. It is not a replacement for a separate backup.

## 9. Network Verification Plan

After implementation, the following checks will be performed.

### IP address verification

Confirm that each VM has the expected static IP address.

### Local connectivity

From Kali, test communication with Ubuntu:

```bash
ping 10.10.10.20
```

A successful response indicates that the machines can communicate using ICMP. A failed ping alone does not prove that the network is broken, because firewalls may block ICMP.

### Service connectivity

After a service is deployed on Ubuntu, test only its intended port from Kali.

For example, if SSH is configured:

```bash
nc -vz 10.10.10.20 22
```

### Isolation verification

Confirm that:

- The Windows host cannot directly access the Internal Network by default.
- The target is not reachable through the home Wi-Fi network.
- The target has no unnecessary internet route during isolated exercises.
- No unintended network adapter or forwarding path has been introduced.

These checks will be performed after configuration. They have not yet been performed.

## 10. Current Implementation Status

| Component | Status |
|---|---|
| VirtualBox installed | Existing |
| Kali Linux VM | Existing |
| Kali currently using NAT | Existing |
| Host-only adapter | Existing |
| Host-only DHCP server | Existing |
| Internal Network `homelab-internal` | Planned |
| Ubuntu Server VM | Planned |
| Static IP configuration | Planned |
| Network isolation testing | Pending |

## 11. Next Steps

1. Finalise which services will run on Kali and Ubuntu.
2. Decide the Ubuntu Server VM resource allocation.
3. Create the Internal Network.
4. Configure static IP addresses.
5. Verify connectivity and isolation.
6. Document the results before beginning security testing.

---

**Milestone:** Network architecture designed. No VirtualBox network settings have been changed as part of this design work.
