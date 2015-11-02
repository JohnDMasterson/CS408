import unittest
import iclicker
import binascii

def generatePacket(response, clickerId):
    clickerId_0 = int(clickerId[0:2], 16)
    clickerId_1 = int(clickerId[2:4], 16)
    clickerId_2 = int(clickerId[4:6], 16)

    packetData = [0x02, 0x13, int(response, 16), clickerId_0, clickerId_1, clickerId_2, generatePacket.count, 0x00]

    packet = iclicker.iPacket(packetData)
generatePacket.count = 0;


base = iclicker.iClickerBaseMock()

class TestIClickerBase(unittest.TestCase):

    # init_base tests
    def test_init_base(self):
        print "init_base:"

        base.init_base()
        assert(base.frequency == [0, 0])

    # set_frequency tests
    def test_set_frequency(self):
        base.set_frequency('A', 'A')
        assert(base.frequency == [0, 0])

        base.set_frequency('A', 'B')
        assert(base.frequency == [0, 1])

        base.set_frequency('b', 'A')
        assert(base.frequency == [1, 0])

        base.set_frequency('C', 'c')
        assert(base.frequency == [2, 2])

        base.set_frequency('D', 'd')
        assert(base.frequency == [3, 3])


    # set_poll_type tests
    def test_set_poll_type(self):
        base.set_poll_type()
        assert(base.poll_type == 0)

        base.set_poll_type('alpha')
        assert(base.poll_type == 0)

        base.set_poll_type('numeric')
        assert(base.poll_type == 1)

        base.set_poll_type('alphanumeric')
        assert(base.poll_type == 2)


    # polling tests
    def test_polling(self):
        # stopping a non-existent poll
        error = False
        try:
            base.stop_poll()
        except ValueError as e:
            error = True
        assert(error == True)

        # default poll success
        error = False
        try:
            base.start_poll()
            assert(base.poll_type == 0)
            base.stop_poll()
        except ValueError as e:
            error = True
        assert(error == False)

        # alphanumeric poll success
        error = False
        try:
            base.start_poll('alphanumeric')
            assert(base.poll_type == 2)
            base.stop_poll()
        except ValueError as e:
            error = True
        assert(error == False)

        # starting a poll twice
        error = False
        try:
            base.start_poll()
            base.start_poll()
        except ValueError as e:
            error = True
        assert(error == True)

        # stopping a poll twice
        error = False
        try:
            base.start_poll()
            base.stop_poll()
            base.stop_poll()
        except ValueError as e:
            error = True
        assert(error == True)


    # poll response tests
    def test_poll_responses(self):
        error = False
        try:
            base.start_poll()

            # send responses
            generatePacket('A', '1F156963')

            base.stop_poll()
        except ValueError as e:
            error = True
        assert(error == False)

if __name__ == '__main__':
    unittest.main()
