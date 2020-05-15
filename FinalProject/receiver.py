# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")

class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive()  # receive data
                 self.logger.info("Got data from socket: {}".format(
                     data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
	         sys.stdout.write(data)
                 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()

class OurReceiver(Receiver):
    ACK_DATA = bytes(123)
    ACK_NEG = bytes(456)

    def __init__(self):
        super(OurReceiver, self).__init__()

    def receive(self):
        N = 10
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive() # receive data
                 checksum_sndr = data[:N]
                 data_sndr = data[N:]
                 checksum_rcvr = bytes(OurReceiver.checksum(self, data_sndr))
                 if checksum_sndr == checksum_rcvr:
                    self.logger.info("Got data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    sys.stdout.write(data_sndr)
                    self.simulator.u_send(bytearray(OurReceiver.ACK_DATA))  # send ACK
                 else:
                    self.logger.info("incorrect data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    self.simulator.u_send(bytearray(OurReceiver.ACK_NEG))  # send ACK
            except socket.timeout:
                sys.exit()

    def checksum(self, data_array):
        checksum_arr = bytearray()
        N = 10 # number of bytes allocated for checksum
        checksum_val = sum(bytearray(data_array))
        ones = N - int(len(str(checksum_val)))
        print(ones)
        checksum_arr.extend(bytes(checksum_val))
        for i in range(ones):
            checksum_arr.extend(bytes(1))
        return checksum_arr


if __name__ == "__main__":
    # test out BogoReceiver
    #rcvr = BogoReceiver()
    rcvr = OurReceiver()
    rcvr.receive()
