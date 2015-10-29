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

    FREQ_DICT = {'a':0,'A':0, 'b':1,'B':1, 'c':2,'C':2, 'd':3,'D':3}

    def __init__(self):
        self.iBase = None
        self.initialized = False
        self.frequency = None
        self.usb_lock = threading.RLock()

    def ctrl_transfer(self, data):
        packet = iPacket(data)
        with self.usb_lock:
            self.iBase.ctrl_transfer(self.BRT, self.PBR, self.VAL, self.IDX, packet.packet_data())
        time.sleep(0.2)

    def syncronous_ctrl_transfer(self, data):
        self.ctrl_transfer(data)
        packet = self.read_packet()
        packet.print_packet()

    def _read(self):
        with self.usb_lock:
            try:
                data = self.iBase.read(self.EIN, self.PACKET_LENGTH, self.TIMEOUT)
            except:
                data = None
        return data

    def read_data(self):
        data = self._read()
        return data

    def read_packet(self):
        data = self._read()
        packet = iPacket(data)
        return packet

    def get_base(self):
        with self.usb_lock:
            backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
            self.iBase = usb.core.find(idVendor=self.VID, idProduct=self.PID, backend=backend)
            if self.iBase.is_kernel_driver_active(0):
                self.iBase.detach_kernel_driver(0)
            self.iBase.set_configuration()

    def set_poll_type(self, poll_type = 'alpha'):
        self.poll_type = {'alpha': 0, 'numeric': 1, 'alphanumeric': 2}[poll_type]
        data = [0x01, 0x19, 0x66+self.poll_type, 0x0a, 0x01]
        self.syncronous_ctrl_transfer(data)

    def set_version_2(self):
        data = [0x01, 0x2D]
        self.syncronous_ctrl_transfer(data)

    def set_frequency(self, first = 'A', second = 'A'):
        first = self.FREQ_DICT[first]
        second = self.FREQ_DICT[second]
        self.frequency = [first, second]
        first = (first + 0x21)
        second = 0x41 + second
        data = [0x01, 0x10, first, second]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x16]
        self.syncronous_ctrl_transfer(data)

    def init_base(self):
        self.set_frequency()

        data = [0x01, 0x2A, 0x21, 0x21, 0x05]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x12]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x15]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x16]
        self.syncronous_ctrl_transfer(data)

        self.set_version_2()

        data = [0x01, 0x29, 0xA1, 0x8F, 0x96, 0x8D, 0x99, 0x97, 0x8F]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x04]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x03]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x16]
        self.syncronous_ctrl_transfer(data)

        self.initialized = True

    def start_poll(self, poll_type = 'alpha'):
        data = [0x01, 0x17, 0x03]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x05]
        self.syncronous_ctrl_transfer(data)

        self.set_poll_type(poll_type)

        data = [0x01, 0x11]
        self.syncronous_ctrl_transfer(data)

    def show_responses(self):
        show = 0
        while show < 10:
            data = self.read_data()
            if data is not None:
                packet = iPacket(data)
                packet.print_packet()
                response = iClickerResponse(data[:32])
                response.parse_alpha_response()
                response.print_response()
                response = iClickerResponse(data[32:64])
                response.parse_alpha_response()
                response.print_response()
                show = show + 1

class iClickerResponse(object):

    def __init__(self, data):
        self.data = data
        self.response = None
        self.clicker_id = None
        self.response_num = None

    def parse_alpha_response(self):
        length = len(self.data)
        if length < 32:
            return
        self.response = self.data[2] - 0x81 + 65
        self.get_id_from_response()

    def get_id_from_response(self):
        for i in range(31, 0, -1):
            if self.data[i] != 0:
                break
        self.response_num = self.data[i]
        seq_start = i-3
        if seq_start > 27 or seq_start < 3:
            return
        clicker_seq = self.data[seq_start : seq_start+3]
        clicker_check = clicker_seq[0] ^ clicker_seq[1] ^ clicker_seq[2]
        clicker_seq.append(clicker_check)
        clicker_id = ''.join("%02X" % b for b in clicker_seq)
        self.clicker_id = clicker_id

    def print_response(self):
        print "Clicker Id: %s" % self.clicker_id
        print "Clicker Response: %s" % self.response
        print "Clicker Response Num: %d" % self.response_num

if __name__ == '__main__':
    packet = iPacket([0x01, 0x83])
    packet.print_packet()

    base = iClickerBase()
    base.get_base()
    base.init_base()
    base.start_poll()

    base.show_responses()
