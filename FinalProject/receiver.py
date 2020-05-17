# Written by S. Mevawala, modified by D. Gitzel
# Jason Kurian, Rebecca Gartenberg, Sophie Jaro
# We implemented RDT 3.0 (checksum, timeout, sequence numbers, ACKS) and handled duplicate packets

import logging

import channelsimulator
import utils
import sys
import socket
import hashlib

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=0.5, debug_level=logging.INFO):
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

    def __init__(self):
        super(OurReceiver, self).__init__()

    def receive(self):
        N = 16
        prev_seq = 99
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive() # receive data
                 checksum_sndr = data[:N]
                 seq_sndr = data[N:N+2]
                 ACK0 = bytearray("\x00\x00")
                 # Handles duplicate packets
                 if seq_sndr == ACK0 and prev_seq != ACK0:
                    prev_seq = 99
                 ACK_DATA = seq_sndr
                 data_sndr = data[N+2:]
                 checksum_rcvr = bytes(OurReceiver.checksum(self, data_sndr))
                 if checksum_sndr == checksum_rcvr:
                    self.logger.info("Got data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    # Handles duplicate packets
                    if seq_sndr != prev_seq:
                        sys.stdout.write(data_sndr)
                    self.simulator.u_send(ACK_DATA)  # send ACK
                    prev_seq = ACK_DATA
                 else:
                    ACK_NEG = bytes(123)
                    self.logger.info("incorrect data")  # note that ASCII will only decode bytes in the range 0-127
                    self.simulator.u_send(ACK_NEG)  # send ACK
            except socket.timeout:
                pass

    def checksum(self, data_array):
        checksum_val = hashlib.md5()
        checksum_val.update(bytearray(data_array))
        return checksum_val.digest()


if __name__ == "__main__":
    rcvr = OurReceiver()
    rcvr.receive()
