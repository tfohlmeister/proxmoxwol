#!/usr/bin/env python3
# This is the listener

import socketserver
import binascii
import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from systemd.journal import JournalHandler
    SYSTEMD_PRESENT = True
except ImportError:
    print('python-systemd not present. Install for journald logging')
    SYSTEMD_PRESENT = False


class UDPListener(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.mac_to_vm: Dict[str, str] = {}
        self.configdir = Path('/etc/pve/qemu-server/')
        super().__init__(request, client_address, server)
    
    def handle(self):
        data = self.request[0]
        client_ip = self.client_address[0]
        logger.info(f'{client_ip} wrote:')
        
        if not self.is_wol_packet(data):
            return
            
        mac = self.parse_mac_from_packet(data)
        if not mac:
            return
            
        logger.info(f'WOL Packet found for mac {mac}...')
        
        self.load_vm_configs()
        if mac in self.mac_to_vm:
            vm_id = self.mac_to_vm[mac]
            logger.info(f"...and waking up vm {vm_id}")
            self.wake_machine(vm_id)
        else:
            logger.info('...but no matching VM found')

    def is_wol_packet(self, data: bytes) -> bool:
        if len(data) != 102:
            return False
        
        header = binascii.hexlify(data[:6]).upper()
        if header != b'FFFFFFFFFFFF':
            return False
            
        mac_repeats = [data[i:i+6] for i in range(6, len(data), 6)]
        if len(mac_repeats) != 16 or len(set(mac_repeats)) != 1:
            return False
            
        return True

    def parse_mac_from_packet(self, data: bytes) -> str:
        return binascii.hexlify(data[6:12]).decode('ascii').upper()

    def convert_mac(self, mac: str) -> str:
        return ''.join(c for c in mac.upper() if c not in ':-')
    
    def wake_machine(self, qemu_id: str):
        # First check if VM exists
        result = subprocess.run(['qm', 'status', qemu_id], 
                             capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f'VM {qemu_id} not found')
            return
            
        # Then check if it's already running
        if 'running' in result.stdout:
            logger.info(f'VM {qemu_id} already running')
            return
            
        # Start the VM
        result = subprocess.run(['qm', 'start', qemu_id],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f'Failed to start VM {qemu_id}: {result.stderr}')
        else:
            logger.info(f'Successfully started VM {qemu_id}')

    def load_vm_configs(self):
        self.mac_to_vm.clear()
        try:
            for conf_file in self.configdir.glob('*.conf'):
                vm_id = conf_file.stem
                content = conf_file.read_text()
                
                for line in content.splitlines():
                    if line.startswith('net'):
                        try:
                            mac = line.split('=')[1].split(',')[0]
                            self.mac_to_vm[self.convert_mac(mac)] = vm_id
                        except (IndexError, KeyError):
                            continue
        except Exception as e:
            logger.error(f'Error reading Proxmox configs: {e}')


def run_server():
    HOST, PORT = '', 9
    with socketserver.UDPServer((HOST, PORT), UDPListener) as server:
        server.serve_forever()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    if SYSTEMD_PRESENT:
        handler = JournalHandler()
        handler.setFormatter(logging.Formatter(
            '[%(levelname)s] %(message)s'))
        logger.addHandler(handler)
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
    
    run_server()
