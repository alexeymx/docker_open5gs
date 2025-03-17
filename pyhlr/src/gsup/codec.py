from construct import Struct, Byte, Int8ul, Int16ul, Bytes, Const, this, GreedyBytes
from .constants import MessageType, IEType, SubscriberStatus, NetworkAccessMode
from src.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GSUP message header
gsup_header = Struct(
    "message_type" / Byte,
    "length" / Int16ul,
)

# Information Element header
ie_header = Struct(
    "type" / Byte,
    "length" / Int8ul,
)

class GSUPCodec:
    @staticmethod
    def encode_message(message_type: int, ies: dict) -> bytes:
        """Encode a GSUP message with its IEs into bytes."""
        message = bytearray()
        payload = bytearray()

        # Encode IEs
        for ie_type, value in ies.items():
            ie_data = GSUPCodec._encode_ie(ie_type, value)
            payload.extend(ie_data)

        # Create header
        header = gsup_header.build({"message_type": message_type, "length": len(payload)})
        message.extend(header)
        message.extend(payload)
        
        return bytes(message)

    @staticmethod
    def decode_message(data: bytes) -> tuple:
        """Decode a GSUP message from bytes into message type and IEs."""
        header = gsup_header.parse(data[:3])
        message_type = header.message_type
        length = header.length
        
        ies = {}
        offset = 3  # Skip header

        while offset < len(data):
            ie_head = ie_header.parse(data[offset:offset+2])
            ie_type = ie_head.type
            ie_length = ie_head.length
            
            value = data[offset+2:offset+2+ie_length]
            ies[ie_type] = value
            
            offset += 2 + ie_length

        return message_type, ies

    @staticmethod
    def _encode_ie(ie_type: int, value: bytes) -> bytes:
        """Encode a single Information Element."""
        ie = bytearray()
        ie.extend(ie_header.build({"type": ie_type, "length": len(value)}))
        ie.extend(value)
        return bytes(ie)

    @staticmethod
    def create_auth_request(imsi: str) -> bytes:
        """Create a Send Authentication Info request message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii')
        }
        return GSUPCodec.encode_message(MessageType.SEND_AUTH_INFO_REQUEST, ies)

    @staticmethod
    def create_auth_response(imsi: str, rand: bytes, autn: bytes) -> bytes:
        """Create a Send Authentication Info response message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii'),
            IEType.RAND: rand,
            IEType.AUTN: autn
        }
        logger.info(f"Creating authentication response with IES: {ies}")
        return GSUPCodec.encode_message(MessageType.SEND_AUTH_INFO_RESULT, ies)

    @staticmethod
    def create_subscriber_data_request(imsi: str) -> bytes:
        """Create a Send Subscriber Data request message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii')
        }
        return GSUPCodec.encode_message(MessageType.SEND_SUBSCRIBER_DATA_REQUEST, ies)

    @staticmethod
    def create_subscriber_data_response(
        imsi: str,
        msisdn: str,
        subscriber_status: int,
        network_access_mode: int,
        bearer_services: bytes = None,
        teleservices: bytes = None
    ) -> bytes:
        """Create a Send Subscriber Data response message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii'),
            IEType.MSISDN: msisdn.encode('ascii'),
            IEType.SUBSCRIBER_STATUS: bytes([subscriber_status]),
            IEType.NETWORK_ACCESS_MODE: bytes([network_access_mode])
        }
        
        if bearer_services:
            ies[IEType.BEARER_SERVICES] = bearer_services
        if teleservices:
            ies[IEType.TELESERVICES] = teleservices
            
        return GSUPCodec.encode_message(MessageType.SEND_SUBSCRIBER_DATA_RESULT, ies)

    @staticmethod
    def create_send_routing_info_for_sm_request(
        imsi: str,
        sm_rp_da: bytes,
        sm_rp_oa: bytes
    ) -> bytes:
        """Create a Send Routing Info for SM request message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii'),
            IEType.SM_RP_DA: sm_rp_da,
            IEType.SM_RP_OA: sm_rp_oa
        }
        return GSUPCodec.encode_message(MessageType.SEND_ROUTING_INFO_FOR_SM_REQUEST, ies)

    @staticmethod
    def create_send_routing_info_for_sm_response(
        imsi: str,
        msc_number: str = None,
        sgsn_number: str = None,
        mme_number: str = None
    ) -> bytes:
        """Create a Send Routing Info for SM response message."""
        ies = {
            IEType.IMSI: imsi.encode('ascii')
        }
        
        # Add available routing numbers
        if msc_number:
            ies[IEType.MSC_NUMBER] = msc_number.encode('ascii')
        if sgsn_number:
            ies[IEType.SGSN_NUMBER] = sgsn_number.encode('ascii')
        if mme_number:
            ies[IEType.MME_NUMBER] = mme_number.encode('ascii')
            
        return GSUPCodec.encode_message(MessageType.SEND_ROUTING_INFO_FOR_SM_RESULT, ies) 