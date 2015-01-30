"""
F1 Live streaming client.
"""
import logging
import Packet
import http
import db
from twisted.internet.protocol import Protocol
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import ClientFactory
from twisted.internet.defer import Deferred
from tools.dump import hexdump

__all__ = ['StreamingClientFactory']

_LOGGER = logging.getLogger(__name__)

POLL_REQUEST = '\x10'

class StreamingClientProtocol(Protocol, TimeoutMixin):
    """streaming client protocol implementation."""
    def __init__(self):
        self.data = ''

    def init_state(self, packet):
        """initialize state with data from key frame packets."""
        defer = Deferred()
        defer.addCallback(self.keyframeReceived)
        http.get_async(defer, 'http://{0}/keyframe_{1:0>5d}.bin'
                        .format(http.F1_LIVE_SERVER, packet.key_frame_id))
        # start polling if no activity after 1 second
        self.setTimeout(1)

    def update_state(self, packet):
        """update state with data from packet."""
        pass

    def keyframeReceived(self, keyframe):
        """parse received key frame into packets; a key frame represents
           the current state."""
        offset = 0
        totlen = len(keyframe)
        while offset < totlen:
            try:
                packet = Packet.packetize(keyframe[offset:])
            except Packet.UnknownPacketType as err:
                _LOGGER.debug(str(err))
                offset += 2
            else:
                self.update_state(packet)
                db.save_frame(packet)
                offset += len(packet)

    def dataReceived(self, data):
        """parse received data into packets."""
        _LOGGER.debug(hexdump(data))
        self.resetTimeout()
        self.data += data
        try:
            packet = Packet.packetize(self.data)
        except Packet.NeedMoreData:
            return
        except Packet.UnknownPacketType as err:
            _LOGGER.debug(str(err))
            self.data = self.data[2:]
        else:
            if type(packet) == Packet.SystemKeyFrame:
                self.init_state(packet)
            else:
                self.update_state(packet)
            db.save_frame(packet)
            self.data = self.data[len(packet):]

    def timeoutConnection(self):
        self.transport.write(POLL_REQUEST)
        self.setTimeout(1)

class StreamingClientFactory(ClientFactory):
    """streaming client protocol factory."""
    def startedConnecting(self, connector):
        _LOGGER.debug('Started connecting...')

    def buildProtocol(self, addr):
        _LOGGER.info('Connected to {0}'.format(addr))
        return StreamingClientProtocol()

    def clientConnectionLost(self, connector, reason):
        _LOGGER.info('Connection lost. Reason: {0}'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        _LOGGER.info('Connection failed. Reason: {0}'.format(reason))

