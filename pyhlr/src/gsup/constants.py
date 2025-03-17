class MessageType:
    # Location Management Messages
    UPDATE_LOCATION_REQUEST = 0x04
    UPDATE_LOCATION_RESULT = 0x05
    UPDATE_LOCATION_ERROR = 0x06
    
    # Insert Subscriber Data Messages (3GPP TS 29.002)
    INSERT_SUBSCRIBER_DATA_REQUEST = 0x07
    INSERT_SUBSCRIBER_DATA_RESULT = 0x08
    INSERT_SUBSCRIBER_DATA_ERROR = 0x09
    
    SEND_AUTH_INFO_REQUEST = 0x0A
    SEND_AUTH_INFO_RESULT = 0x0B
    SEND_AUTH_INFO_ERROR = 0x0C

    PURGE_MS_REQUEST = 0x0D
    PURGE_MS_RESULT = 0x0E
    PURGE_MS_ERROR = 0x0F

    # Subscriber Data messages
    SEND_SUBSCRIBER_DATA_REQUEST = 0x10
    SEND_SUBSCRIBER_DATA_RESULT = 0x11
    SEND_SUBSCRIBER_DATA_ERROR = 0x12

    # SMS Routing messages
    SEND_ROUTING_INFO_FOR_SM_REQUEST = 0x14
    SEND_ROUTING_INFO_FOR_SM_RESULT = 0x15
    SEND_ROUTING_INFO_FOR_SM_ERROR = 0x16

class IEType:
    # Common IEs
    IMSI = 0x01
    CAUSE = 0x02
    
    # Authentication IEs
    AUTH_TUPLE = 0x03
    RAND = 0x04
    SRES = 0x05
    KC = 0x06
    IK = 0x07
    CK = 0x08
    AUTN = 0x09
    AUTS = 0x0A
    RES = 0x0B
    
    # Subscriber Data IEs
    MSISDN = 0x0C
    SUBSCRIBER_STATUS = 0x0D
    NETWORK_ACCESS_MODE = 0x0E
    BEARER_SERVICES = 0x0F
    TELESERVICES = 0x10
    
    # Location Management IEs
    VLR_NUMBER = 0x11
    MSC_NUMBER = 0x12
    SGSN_NUMBER = 0x13
    GMLC_NUMBER = 0x14
    
    # SMS Routing IEs
    SM_RP_DA = 0x15
    SM_RP_OA = 0x16
    
    # Additional IEs for Insert Subscriber Data
    CATEGORY = 0x17
    SUBSCRIBER_DATA_FLAGS = 0x18
    GSM_BEARER_CAPABILITIES = 0x19
    PROVISIONED_SS = 0x1A
    ODB_DATA = 0x1B
    ROAMING_RESTRICTION = 0x1C
    REGIONAL_SUBSCRIPTION_DATA = 0x1D

class Cause:
    # Error causes
    IMSI_UNKNOWN = 0x02
    ILLEGAL_MS = 0x03
    AUTH_UNACCEPTABLE = 0x05
    PROTOCOL_ERROR = 0x6F
    SUBSCRIBER_DATA_NOT_AVAILABLE = 0x1A
    SMS_ROUTING_ERROR = 0x1B
    
class SubscriberStatus:
    SERVICE_GRANTED = 0x00
    OPERATOR_DETERMINED_BARRING = 0x01
    ROAMING_NOT_ALLOWED = 0x02

class NetworkAccessMode:
    PACKET_AND_CIRCUIT = 0x00
    ONLY_PACKET = 0x01
    ONLY_CIRCUIT = 0x02 