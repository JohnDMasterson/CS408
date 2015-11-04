import unittest
import iclicker
import binascii

def generatePacket(response, clickerId):
    clickerId_0 = int(clickerId[0:2], 16)
    clickerId_1 = int(clickerId[2:4], 16)
    clickerId_2 = int(clickerId[4:6], 16)
    packetPadding = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    packetData = [0x02, 0x13, int(response, 16), clickerId_0, clickerId_1, clickerId_2, generatePacket.count, 0x00]
    return packetData + packetPadding + packetPadding + packetPadding + packetPadding
generatePacket.count = 1;

def generateResponse(response, clickerId):
    packet = generatePacket(response, clickerId)
    response = iclicker.iClickerResponse(packet[:32])
    response.parse_alpha_response()
    return response

base = iclicker.iClickerBaseMock()

class TestIClickerBase(unittest.TestCase):

    # init_base tests
    def test_init_base(self):
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

        # empty poll
        error = False
        try:
            poll = iclicker.iClickerPollMock()
            poll.start_poll()
            poll.end_poll()
            responses = poll.get_all_responses()
            assert(len(responses) == 0)
        except ValueError as e:
            error = True
        assert(error == False)


        # poll with one response
        error = False
        try:
            poll = iclicker.iClickerPollMock()
            poll.start_poll()

            response = generateResponse('A', '1F156963')

            poll.add_response(response)

            poll.end_poll()
            responses = poll.get_all_responses()
            assert(len(responses) == 1)
        except ValueError as e:
            error = True
        assert(error == False)


        # poll with two responses
        error = False
        try:
            poll = iclicker.iClickerPollMock()
            poll.start_poll()

            response = generateResponse('A', '1F156963')
            response2 = generateResponse('B', '2F156953')

            poll.add_response(response)
            poll.add_response(response2)

            poll.end_poll()
            responses = poll.get_all_responses()
            assert(len(responses) == 2)
        except ValueError as e:
            error = True
        assert(error == False)


        # poll with two responses but multiple from each user
        error = False
        try:
            poll = iclicker.iClickerPollMock()
            poll.start_poll()

            response = generateResponse('A', '1F156963')
            response2 = generateResponse('B', '2F156953')
            response3 = generateResponse('C', '1F156963')
            response4 = generateResponse('C', '2F156953')

            poll.add_response(response)
            poll.add_response(response2)
            poll.add_response(response3)
            poll.add_response(response4)

            poll.end_poll()
            responses = poll.get_all_responses()
            assert(len(responses) == 2)
            assert(len(responses['1F156963']) == 2)
            assert(len(responses['2F156953']) == 2)

            # check latest response
            latest = poll.get_latest_responses()
            assert(len(latest) == 2)
            assert latest['1F156963'].response == -52
            assert latest['2F156953'].response == -52
        except ValueError as e:
            error = True
        assert(error == False)

if __name__ == '__main__':
    unittest.main()
