"""
F1 Live streaming client.
"""
import logging
import Packet
import http
import db
import firebase
import config
from twisted.internet.protocol import Protocol
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import ClientFactory
from twisted.internet.defer import Deferred
from tools.dump import hexdump

__all__ = ['StreamingClientFactory']

log = logging.getLogger(__name__)

POLL_REQUEST = '\x10'

class StreamingClientProtocol(Protocol, TimeoutMixin):
    """streaming client protocol implementation."""
    def __init__(self, factory):
        self.factory = factory
        self.data = ''

        # high-level protocol properties
        self.comment = ''

    def init_state(self, packet):
        """initialize state with data from key frame packets."""
        key_frame_id = '{0:0>5d}'.format(packet.key_frame_id)
        defer = Deferred()
        defer.addCallback(self.keyframeReceived, key_frame_id)
        http.get_async(defer, 'http://{0}/keyframe_{1}.bin'
                        .format(http.F1_LIVE_SERVER, key_frame_id))
        # start polling if no activity after 1 second
        self.setTimeout(1)

    def update_state(self, packet):
        """update state with data from packet."""
        if type(packet) == Packet.SystemCommentary:
            self.comment += packet.comment
            if packet.last:
                self.comment_received(self.comment)
                self.comment = ''

    def comment_received(self, comment):
        """callback when complete comment is received."""
        self.factory.comment_finished(comment)

    def keyframeReceived(self, keyframe, key_frame_id):
        """parse received key frame into packets; a key frame represents
           the current state."""
        db.save_key_frame(keyframe, key_frame_id)
        offset = 0
        totlen = len(keyframe)
        while offset < totlen:
            try:
                packet = Packet.packetize(keyframe[offset:])
            except Packet.UnknownPacketType as err:
                log.debug(str(err))
                offset += 2
            else:
                if type(packet) == Packet.SystemEvent:
                    try:
                        self.factory.create_firebase_ref(
                                        packet.get_event_type())
                    except Packet.UnknownEventType as err:
                        log.info(str(err))
                self.update_state(packet)
                db.save_packet(packet)
                offset += len(packet)

    def dataReceived(self, data):
        """parse received data into packets."""
        log.debug(hexdump(data))
        self.resetTimeout()
        self.data += data
        try:
            packet = Packet.packetize(self.data)
        except Packet.NeedMoreData:
            return
        except Packet.UnknownPacketType as err:
            log.debug(str(err))
            self.data = self.data[2:]
        else:
            self.handle_packet(packet)
            db.save_packet(packet)
            self.data = self.data[len(packet):]

    def handle_packet(self, packet):
        """handle received packet."""
        if type(packet) == Packet.SystemKeyFrame:
            self.init_state(packet)
        else:
            self.update_state(packet)

    def timeoutConnection(self):
        """poll for more data from server."""
        self.transport.write(POLL_REQUEST)
        self.setTimeout(1)

class StreamingClientFactory(ClientFactory):
    """streaming client protocol factory."""
    def __init__(self):
        self.comment_ref = None

    def startedConnecting(self, connector):
        log.debug('Started connecting...')

    def buildProtocol(self, addr):
        log.info('Connected to {0}'.format(addr))
        return StreamingClientProtocol(self)

    def clientConnectionLost(self, connector, reason):
        log.info('Connection lost. Reason: {0}'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        log.info('Connection failed. Reason: {0}'.format(reason))

    def comment_finished(self, comment):
        """push full comment to firebase reference."""
        if self.comment_ref:
            self.comment_ref.push(comment)

    def create_firebase_ref(self, event):
        """create our firebase references."""
        url = config.get_firebase()
        if url:
            root = firebase.Firebase(url)
            self.comment_ref = root.child('{0}/commentary'.format(event))

