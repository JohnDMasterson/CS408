#!/usr/bin/phthon

from usb import USBError
import usb.core, usb.util
import usb.backend.libusb1
from array import array
from collections import defaultdict, Counter
import logging, time, sys
import threading

# packets should be 64 bytes long
# packts should be padded with 0x0 after data being sent
class iPacket(object):

    def __init__(self, data = None):
        if data is None:
            data = []
        #copy data from packet
        self.packet = array('B', data[:len(data)])

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


class BaseInterface(object):
    initialized = False
    frequency = None
    poll_type = None
    poll_active = False
    FREQ_DICT = {'a':0,'A':0, 'b':1,'B':1, 'c':2,'C':2, 'd':3,'D':3}
    POLL_DICT = {'alpha':0, 'numeric':1, 'alphanumeric':2}

    def set_poll_type(self, poll_type = 'alpha'):
        self.poll_type = self.POLL_DICT[poll_type]

    def set_frequency(self, first = 'A', second = 'A'):
        self.frequency = [self.FREQ_DICT[first], self.FREQ_DICT[second]]

    def set_base_display(self):
        raise NotImplementedError()

    def init_base(self):
        self.set_frequency()

    def start_poll(self):
        if (self.poll_active == True):
            raise ValueError('Attempted to start a poll while a poll was already active.')

        self.poll_active = True

    def stop_poll(self):
        if (self.poll_active == False):
            raise ValueError('Attempted to stop a poll while there\'s no active poll.')

        self.poll_active = False

    def get_responses(self):
        raise NotImplementedError()

    def show_responses(self):
        raise NotImplementedError()

class iClickerBaseMock(BaseInterface):
        def set_poll_type(self, poll_type = 'alpha'):
            super(iClickerBaseMock, self).set_poll_type(poll_type)

        def set_frequency(self, first = 'A', second = 'A'):
            super(iClickerBaseMock, self).set_frequency(first, second)

        def init_base(self):
            super(iClickerBaseMock, self).init_base()
            self.initialized = True

        def start_poll(self, poll_type = 'alpha'):
            self.set_poll_type(poll_type)
            super(iClickerBaseMock, self).start_poll()

        def stop_poll(self):
            super(iClickerBaseMock, self).stop_poll()

        def get_responses(self):
            print "not setup"

        def show_responses(self):
            print "not setup"

class iClickerBase(BaseInterface):
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

    POLL_DICT = {'alpha':0, 'numeric':1, 'alphanumeric':2}

    def __init__(self):
        self.iBase = None
        self.initialized = False
        self.frequency = None
        self.usb_lock = threading.RLock()

    def ctrl_transfer(self, data):
        try:
            packet = iPacket(data)
            with self.usb_lock:
                self.iBase.ctrl_transfer(self.BRT, self.PBR, self.VAL, self.IDX, packet.packet_data())
            time.sleep(0.2)
        except:
            time.sleep(0.2)

    def syncronous_ctrl_transfer(self, data):
        self.ctrl_transfer(data)
        packet = self.read_packet()

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
            try:
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
                self.iBase = usb.core.find(idVendor=self.VID, idProduct=self.PID, backend=backend)
                if self.iBase.is_kernel_driver_active(0):
                    self.iBase.detach_kernel_driver(0)
                self.iBase.set_configuration()
            except:
                self.iBase = None
                raise ValueError('iClicker base not recognized: Make sure that it\'s plugged in.')

    def set_poll_type(self, poll_type = 'alpha'):
        self.poll_type = self.POLL_DICT[poll_type]
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

    def set_base_display(self, string, line):
        line = 0x13 + line
        data = [0x01, line]
        string = string[:16]
        string = string + ' '*(16-len(string))
        data.extend(ord(c) for c in string)
        self.syncronous_ctrl_transfer(data)

    def init_base(self):
        self.set_frequency()

        data = [0x01, 0x2A, 0x21, 0x41, 0x05]
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

    def stop_poll(self):
        data = [0x01, 0x12]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x16]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x01]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x03]
        self.syncronous_ctrl_transfer(data)
        data = [0x01, 0x17, 0x04]
        self.syncronous_ctrl_transfer(data)

    def get_responses(self):
        responses = []
        data = self.read_data()
        if data is not None:
            packet = iPacket(data)
            response1 = iClickerResponse(data[:32])
            response1.parse_alpha_response()
            response2 = iClickerResponse(data[32:64])
            response2.parse_alpha_response()
            responses = [response1, response2]
        return responses

class iClickerResponse(object):

    def __init__(self, data):
        self.data = data
        self.response = None
        self.clicker_id = None
        self.response_num = None

    def parse_alpha_response(self):
        if self.is_valid_response():
            # response - 0x81 + 65 get an 'a' response to equal to ascii a value
            self.response = self.data[2] - 0x80 + 65
            self.get_id_from_alpha_response()
        else:
            self.response = -1
            self.clicker_id = -1
            self.response_num = -1

    def get_id_from_alpha_response(self):
        self.response_num = self.data[6]
        clicker_seq = self.data[3 : 6]
        clicker_check = clicker_seq[0] ^ clicker_seq[1] ^ clicker_seq[2]
        clicker_seq.append(clicker_check)
        clicker_id = ''.join("%02X" % b for b in clicker_seq)
        self.clicker_id = clicker_id

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

    def is_valid_response(self):
        # responses should be 32 bytes long
        responseLength = len(self.data);
        # first byte is 0x02
        # second bytes is 0x13
        return self.data[0] == 0x02 and self.data[1] == 0x13

class iClickerPoll(object):

    def __init__(self):
        self.iClickerBase = None
        self.iClickerResponses = defaultdict(list)
        self.last_response_num = 0
        self.isPolling = False
        self.pollThread = None
        self._init_base()

    def _init_base(self):
        if self.iClickerBase is None:
            self.iClickerBase = iClickerBase()
            self.iClickerBase.get_base()
        if self.iClickerBase.initialized is False:
            self.iClickerBase.init_base()

    def start_poll(self):
        self.iClickerBase.start_poll()
        self.isPolling = True
        self.poll_loop()

    def poll_loop(self):
        t = threading.Thread(target = self._poll_loop_thread)
        t.daemon = True
        t.start()

    # can be up to two responses in each iclicker response
    # each response is 32 bytes long
    def _poll_loop_thread(self):
        while self.isPolling is True:
            responses = self.iClickerBase.get_responses()
            # add first response from poll
            self.add_response(responses[-1])

    def end_poll(self):
        self.isPolling = False
        self.iClickerBase.stop_poll()

    def clear_responses(self):
        self.iClickerResponses = defaultdict(list)

    def add_response(self, response):
        # every response has a number 0-255. This number is incremented by 1 for each response recieved
        # it resets to 0 after 255

        # reset bucket for each response when a new one is given
        self.iClickerResponses[response.clicker_id] = []
        # append to end of bucket
        self.iClickerResponses[response.clicker_id].append(response)

    def get_all_responses(self):
        return self.iClickerResponses

    def get_latest_responses(self):
        responses = defaultdict(list)
        for key in self.iClickerResponses:
            curr = self.iClickerResponses[key][-1]
            responses[curr.clicker_id] = curr
        return responses

    def get_responses_for_clicker_ids(self, clicker_ids):
        responses = []
        for clicker_id in clicker_ids:
            response = self.iClickerResponses[clicker_id]
            if len(response) > 0:
                response = response[-1]
                responses.append(response.response)
        return responses

    def set_display(self, text, line):
        self.iClickerBase.set_base_display(text, line)

class iClickerPollMock(iClickerPoll):
    def __init__(self):
        super(iClickerPollMock, self).__init__()

    def _init_base(self):
        if self.iClickerBase is None:
            self.iClickerBase = iClickerBaseMock()
        if self.iClickerBase.initialized is False:
            self.iClickerBase.init_base()

    def start_poll(self):
        self.iClickerBase.start_poll()
        self.isPolling = True

    def add_response(self, response):
        super(iClickerPollMock, self).add_response(response)

    def get_all_responses(self):
        return self.iClickerResponses

    def get_latest_responses(self):
        responses = defaultdict(list)
        for key in self.iClickerResponses:
            curr = self.iClickerResponses[key][-1]
            responses[curr.clicker_id] = curr
        return responses

if __name__ == '__main__':
    try:
        poll = iClickerPoll()
    except ValueError as e:
        print e

    poll.set_display("polling", 0)
    poll.start_poll()
    time.sleep(10)
    poll.end_poll()
    poll.set_display("done", 0)

    responses = poll.get_all_responses()
    for key in responses:
        responses[key][1].print_response()
