# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class OurSender(Sender):

    def __init__(self):
        super(OurSender, self).__init__()

    def send(self, data):
            self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))

            slicedData = self.slice_frames(data)
            segments  = []
            for i in range(len(slicedData)):
                finalData = bytearray()

                seg = Segment(slicedData[i], 0, 0, 0)
                seg.checksum = Segment.checksum(seg,slicedData[i])
                finalData.extend(bytes(seg.checksum)) # problem is that checksum is not being added on in python 2. final data is only the data
                finalData.extend(seg.data)
                # send first packet, then send based on current ack
                while True:
                    try:
                        self.simulator.u_send(finalData)  # send data
                        ack = self.simulator.u_receive()  # receive ACK
                        self.logger.info("Got ACK from socket: {}".format(
                            ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                        #if ack.decode('ascii') == '123':
                            # send next: format next segment
                            # set ack
                            # set seq num
                        break
                    except socket.timeout:
                        # resend packet based on ack
                        pass


    def slice_frames(self, data):
        """
        Slice input into BUFFER_SIZE frames
        :param data_bytes: input bytes
        :return: list of frames of size BUFFER_SIZE
        """
        frames = list()
        num_bytes = len(data)
        extra = 1 if num_bytes % 1012 else 0

        for i in xrange(num_bytes / 1012 + extra):
            # split data into 1024 byte frames
            frames.append(
                data[
                    i * 1012:
                    i * 1012+ 1012
                ]
            )
        return frames

class Segment(object):
        def __init__(self, data = [],checksum = 0,seqnum = 0,acknum = 0):
            self.data = data
            self.checksum = checksum
            self.seqnum = seqnum
            self.acknum = acknum

        def checksum(self, data_array):
             checksum_arr = bytearray()
             N = 10 # number of bytes allocated for checksum
             checksum_val = sum(bytearray(data_array))
             ones = N - int(len(str(checksum_val)))
             checksum_arr.extend(bytes(checksum_val))
             for i in range(ones):
                checksum_arr.extend(bytes(1))
             return checksum_arr



if __name__ == "__main__":
    # test out BogoSender
    DATA = bytes(sys.stdin.read())
    #sndr = BogoSender()
    sndr = OurSender()
    sndr.send(DATA)
