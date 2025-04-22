# Proxmox Wake-on-LAN VM Starter

A lightweight service that listens for Wake-on-LAN (WoL) magic packets and starts the corresponding Proxmox VMs based on their MAC addresses.

## How it Works

1. The service listens for WoL magic packets on UDP port 9
2. When a packet is received, it extracts the target MAC address
3. It then checks Proxmox VM configurations for a matching network interface MAC
4. If found, it starts the corresponding VM

## Installation

```bash
# Clone the repository
git clone https://github.com/tfohlmeister/proxmoxwol.git
cd proxmoxwol

# Install dependencies (Debian/Ubuntu)
apt install python3 python3-systemd

# Install the service (as root)
./install.sh
```

The service will be automatically enabled and started.

## Usage

### Sending WoL Packets

Use the included `magicpacket.py` utility to send WoL packets:

```bash
./magicpacket.py AA:BB:CC:DD:EE:FF
```

Additional options:
```bash
./magicpacket.py --help
usage: magicpacket.py [-h] [--broadcast BROADCAST] [--port PORT] mac

Send Wake-on-LAN magic packet

positional arguments:
  mac                   MAC address of target machine

optional arguments:
  -h, --help           show this help message and exit
  --broadcast BROADCAST broadcast address (default: 255.255.255.255)
  --port PORT          port to send to (default: 9)
```

### Service Management

```bash
# Check service status
systemctl status proxmoxwol-vm

# View logs
journalctl -u proxmoxwol-vm -f

# Restart service
systemctl restart proxmoxwol-vm
```

## Requirements

- Python 3.6+
- python3-systemd (for journald logging)
- Proxmox VE
- Root access for installation

## Security

The service:
- Runs with minimal privileges
- Uses systemd security hardening
- Only starts VMs that are configured in Proxmox
- Requires no additional open ports (uses standard WoL port 9)

## Troubleshooting

1. Check if the service is running:
   ```bash
   systemctl status proxmoxwol-vm
   ```

2. Monitor logs in real-time:
   ```bash
   journalctl -u proxmoxwol-vm -f
   ```

3. Verify VM configuration:
   - Check if the MAC address matches your Proxmox VM network interface
   - Ensure the VM configuration exists in `/etc/pve/qemu-server/`

4. Test WoL packet:
   ```bash
   # From another machine
   ./magicpacket.py TARGET_MAC_ADDRESS
   ```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This is a fork of an existing GPL-3.0 licensed project, maintaining the same license terms.
