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
            checkedData = []
            for i in range(len(slicedData)):
                checkedData.append(self.checksum(slicedData[i]))

            while True:
                try:
                    self.simulator.u_send(data)  # send data
                    ack = self.simulator.u_receive()  # receive ACK
                    self.logger.info("Got ACK from socket: {}".format(
                        ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    break
                except socket.timeout:
                    pass

    def slice_frames(self, data):
        """
        Slice input into BUFFER_SIZE frames
        :param data_bytes: input bytes
        :return: list of frames of size BUFFER_SIZE
        """
        frames = list()
        num_bytes = len(data)
        extra = 1 if num_bytes % 1024 else 0

        for i in xrange(num_bytes / 1024 + extra):
            # split data into 1024 byte frames
            frames.append(
                data[
                    i * 1024:
                    i * 1024+ 1024
                ]
            )
        return frames

    def checksum(self, data_array):
         checksum = 0
         for i in xrange(len(data_array)):
            checksum += data_array[i]

         print "checksum: " + str(checksum)
         return checksum




if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    #sndr = BogoSender()
    sndr = OurSender()
    sndr.send(DATA)
