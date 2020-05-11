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

    def __init__(self):
        super(OurReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 segment = self.simulator.u_receive()  # receive data
                 checksum_sndr = segment[0:5]
                 data_sndr = segment[6:len(segment)]
                 checksum_rcvr = OurReceiver.checksum(self, data_sndr)
                 if checksum_sndr == checksum_rcvr:
                    print('same')
                    #data = self.simulator.u_receive()  # receive data
                    self.logger.info("Got data from socket: {}".format(data_sndr.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    sys.stdout.write(data_sndr)
                    self.simulator.u_send(OurReceiver.ACK_DATA)  # send ACK
                 else:
                    print('not same')
            except socket.timeout:
                sys.exit()

    def checksum(self, data_array):
        checksum_val = 0
        for i in xrange(len(data_array)): # i dont think we need for loop here anymore
            checksum_val += data_array[i]
        checksum_arr = [int(x) for x in str(checksum_val)]
        print('checksum')
        print(bytearray(checksum_arr))
        return bytearray(checksum_arr)


if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = BogoReceiver()
    #rcvr = OurReceiver()
    rcvr.receive()
