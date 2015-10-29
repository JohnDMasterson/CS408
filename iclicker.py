#!/usr/bin/phthon

from usb import USBError
import usb.core, usb.util
import usb.backend.libusb1
from array import array
from collections import defaultdict, Counter
import logging, time, sys
import threading

class iPacket(object):
    def __init__(self, data=None):
        if data is None:
            data = []
        # Remove spaces
        data = data.replace(' ', '')
        # Make array of unsigned chars
        length = len(data)
        data = array('B', (int(data[i:i+2],16) for i in range(0, length, 2)))
        self.packet = array('B', data[:64])
        length = len(self.packet)
        self.packet.extend([0]*64-length)

    def packet_data(self):
        return self.packet.tostring()

    def print_packet(self):
        i = 0;
        for character in self.packet
            if i%16 == 0 :
                print("")
            if i%8 == 0 :
                print("\t"),
            print("%X ",character),
            i++

class iClickerBase(object):

    # Constants for usb stuff
    VID = 0x1881
    PID = 0x0150
    EIN = 0x0083
    BRT = 0x0021
    PBR = 0x0009
    VAL = 0x0200
    IDX = 0x0000

    PACKET_LENGTH = 64
    TIMEOUT = 100

    def __init__(self):
        self.iBase = None
        self.initialized = False

    def ctrl_transfer(self, data):
        packet = iPacket(data)
        self.iBase.ctrl_transfer(BTR, PBR, VAL, IDX, packet.packet_data))

    def _read(self):
        data = self.iBase.read(EIN, PACKET_LENGTH, TIMEOUT);
        packet = iPacket(data)
        return packet

    def get_base(self):
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
        self.iBase = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID, backend=backend)
        if self.device.is_kernel_driver_active(0):
            self.device.detach_kernel_driver(0)
        self.device.set_configuration()

    def set_poll_type(self, poll_type = 'alpha')
        self.poll_type = = {'alpha': 0, 'numeric': 1, 'alphanumeric': 2}[poll_type]
        data = [0x01, 0x19, 0x66+poll_type, 0x0a, 0x01]
        self.ctrl_transfer(data);

if __name__ == '__main__':
    packet = iPcaket([0x01, 0x83])
    packet.print_packet
