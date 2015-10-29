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
        self.packet = array('B', data[:64])
        length = len(self.packet)
        self.packet.extend([0]* (64-length))

    def packet_data(self):
        return self.packet.tostring()

    def print_packet(self):
	print("Packet Data:")
        i = 0;
        for character in self.packet:
            if i%16 == 0 :
                print ""
            if i%8 == 0 :
                print "\t" ,
            print "%02X " % character ,
            i = i+1

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
        self.frequency = None

    def ctrl_transfer(self, data):
        packet = iPacket(data)
        self.iBase.ctrl_transfer(BTR, PBR, VAL, IDX, packet.packet_data())
        time.sleep(0.2)

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

    def set_poll_type(self, poll_type = 'alpha'):
        self.poll_type = {'alpha': 0, 'numeric': 1, 'alphanumeric': 2}[poll_type]
        data = [0x01, 0x19, 0x66+poll_type, 0x0a, 0x01]
        self.ctrl_transfer(data);

    def set_version_2(self):
        data = [0x01, 0x2D]
        self.ctrl_transfer(data);

    def set_frequency(self, first = 'A', second = 'A'):
        first = {'a':1,'A':1, 'b':2,'B':2, 'c':3,'C':3, 'd':4,'D':4, 'E':5,'E':5}
        second = {'a':1,'A':1, 'b':2,'B':2, 'c':3,'C':3, 'd':4,'D':4, 'E':5,'E':5}
        self.frequency = [first, second]
        data = [0x01, 0x10, 0x21 + first, 0x41 + second]
        self.ctrl_transfer(data)
        data = [0x01, 0x16]
        self.ctrl_transfer(data)

    def init_base(self):
        self.set_frequency()

        data = [0x01, 0x2A, 0x21, 0x21, 0x05]
        self.ctrl_transfer(data)
        data = [0x01, 0x12]
        self.ctrl_transfer(data)
        data = [0x01, 0x15]
        self.ctrl_transfer(data)
        data = [0x01, 0x16]
        self.ctrl_transfer(data)

        self.set_version_2()

        data = [0x01, 0x29, 0xA1, 0x8F, 0x96, 0x8D, 0x99, 0x97, 0x8F]
        self.ctrl_transfer(data)
        data = [0x01, 0x17, 0x04]
        self.ctrl_transfer(data)
        data = [0x01, 0x17, 0x03]
        self.ctrl_transfer(data)
        data = [0x01, 0x16]
        self.ctrl_transfer(data)

        self.initialized = True

    def start_poll(self, poll_type = 'alpha'):
        data = [0x01, 0x17, 0x03]
        self.ctrl_transfer(data)
        data = [0x01, 0x17, 0x05]
        self.ctrl_transfer(data)

        self.set_poll_type(poll_type)

        data = [0x01, 0x11]
        self.ctrl_transfer(data)

if __name__ == '__main__':
    packet = iPacket([0x01, 0x83])
    packet.print_packet()

    base = iClickerBase()
    base.get_base()
    base.init_base()
    base.start_poll()
