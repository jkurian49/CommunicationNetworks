# Written by S. Mevawala, modified by D. Gitzel
# Jason Kurian, Rebecca Gartenberg, Sophie Jaro
# We implemented RDT 3.0 (checksum, timeout, sequence numbers, ACKS) and handled duplicate packets

import logging
import socket

import channelsimulator
import utils
import sys
import hashlib


class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=0.5, debug_level=logging.INFO):
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
        self.logger.info(
            "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


class OurSender(BogoSender):

    def __init__(self):
        super(OurSender, self).__init__()

    def send(self, data):
        curr_ack = 0
        curr_data = 0
        self.logger.info(
            "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))

        slicedData = self.slice_frames(data)
        segments = []
        while curr_data < len(slicedData):
            finalData = bytearray()
            seg = Segment(slicedData[curr_data], 0, curr_ack)
            seg.checksum = Segment.checksum(seg, slicedData[curr_data])
            finalData.extend(seg.checksum)
            if curr_ack < 10:
                finalData.extend(bytes(0))
            finalData.extend(bytes(curr_ack))
            finalData.extend(seg.data)
            while True:
                try:

                    self.simulator.u_send(finalData)  # send data
                    ack = self.simulator.u_receive()  # receive ACK
                    self.logger.info("Got ACK from socket: " + ack)  # note that ASCII will only decode bytes in the range 0-127g

                    if ack == finalData[16:18]:
                        # makes sure sequence numbers don't excede 2 bytes
                        if curr_ack == 99:
                            curr_ack = 0
                        else:
                            curr_ack += 1
                        curr_data += 1
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
        extra = 1 if num_bytes % 1006 else 0

        for i in xrange(num_bytes / 1006 + extra):
            # split data into 1012 byte frames
            frames.append(
                data[
                i * 1006:
                i * 1006 + 1006
                ]
            )
        return frames


class Segment(object):
    def __init__(self, data=[], checksum=0, seqnum=0):
        self.data = data
        self.checksum = checksum
        self.seqnum = seqnum

    def checksum(self, data_array):
        checksum_val = hashlib.md5()
        checksum_val.update(bytearray(data_array))
        return checksum_val.digest()


if __name__ == "__main__":
    DATA = bytes(sys.stdin.read())
    sndr = OurSender()
    sndr.send(DATA)
