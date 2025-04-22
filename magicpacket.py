#!/usr/bin/env python3
# simple script to send magic packets

import sys
import binascii
import socket
import argparse

def send_magic_packet(mac: str, broadcast: str = '255.255.255.255', port: int = 9):
    """Send a Wake-on-LAN magic packet."""
    # Clean the MAC address
    mac = ''.join(c for c in mac.upper() if c not in ':-')
    if len(mac) != 12:
        raise ValueError("Invalid MAC address format")

    # Create magic packet
    header = 'FF' * 6
    payload = header + mac * 16
    packet = binascii.unhexlify(payload)

    # Send packet
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast, port))

def main():
    parser = argparse.ArgumentParser(description='Send Wake-on-LAN magic packet')
    parser.add_argument('mac', help='MAC address of target machine')
    parser.add_argument('--broadcast', default='255.255.255.255',
                      help='Broadcast address (default: 255.255.255.255)')
    parser.add_argument('--port', type=int, default=9,
                      help='Port to send to (default: 9)')
    
    args = parser.parse_args()
    
    try:
        send_magic_packet(args.mac, args.broadcast, args.port)
        print(f"Sent magic packet to {args.mac}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error sending packet: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
