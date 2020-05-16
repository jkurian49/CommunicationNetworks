# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
import hashlib

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=5, debug_level=logging.INFO):
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

class OurReceiver(BogoReceiver):
    #ACK_DATA = bytes()
    ACK_NEG = bytes(456)

    def __init__(self):
        super(OurReceiver, self).__init__()

    def receive(self):
        N = 16
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive() # receive data
                 checksum_sndr = data[:N]
                 seq_sndr = data[N:N+2]
                 ACK_DATA = bytes(seq_sndr)
                 data_sndr = data[N+2:]
                 checksum_rcvr = bytes(OurReceiver.checksum(self, data_sndr))
                 self.logger.info("Sender checksum: " + checksum_sndr)
                 self.logger.info("Receiver checksum: " + checksum_rcvr)
                 if checksum_sndr == checksum_rcvr:
                    self.logger.info("Got data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    #sys.stdout.write(data_sndr)
                    self.simulator.u_send(ACK_DATA)  # send ACK
                 else:
                    if (seq_sndr == 0):
                        seq_sndr = 99
                    #else:
                        #seq_sndr = seq_sndr - 1
                    ACK_NEG = bytes(seq_sndr)
                    self.logger.info("incorrect data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    self.simulator.u_send(ACK_NEG)  # send ACK
            except socket.timeout:
                a = 1
                #sys.exit()

    def checksum(self, data_array):
        # checksum_arr = bytearray()
        # N = 10 # number of bytes allocated for checksum
        # checksum_val = sum(bytearray(data_array))
        # ones = N - int(len(str(checksum_val)))
        # checksum_arr.extend(bytes(checksum_val))
        # for i in range(ones):
        #     checksum_arr.extend(bytes(1))
        # return checksum_arr
        checksum_val = hashlib.md5()
        checksum_val.update(bytearray(data_array))
        return checksum_val.digest()


if __name__ == "__main__":
    # test out BogoReceiver
    #rcvr = BogoReceiver()
    rcvr = OurReceiver()
    rcvr.receive()
