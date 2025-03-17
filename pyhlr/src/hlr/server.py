import asyncio
import logging
import traceback
from src.gsup.codec import GSUPCodec
from src.gsup.constants import MessageType, IEType, Cause, SubscriberStatus, NetworkAccessMode
from src.auth.client import AuthClient
from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IPA Constants
IPA_PROTO = 0xfe
CCM_PING = 0x00
CCM_PONG = 0x01
CCM_ID_REQUEST = 0x04
CCM_ID_RESPONSE = 0x05
CCM_ID_ACK = 0x06

# CCM Tags
CCM_TAG_SERIAL_NUMBER = 0x00
CCM_TAG_UNIT_NAME = 0x01
CCM_TAG_LOCATION = 0x02
CCM_TAG_UNIT_TYPE = 0x03
CCM_TAG_EQUIPMENT_VERSION = 0x04
CCM_TAG_SOFTWARE_VERSION = 0x05
CCM_TAG_MAC_ADDRESS = 0x07
CCM_TAG_UNIT_ID = 0x08

class GSUPServer:
    def __init__(self, host: str = settings.HLR_HOST, port: int = settings.HLR_PORT):
        self.host = host
        self.port = port
        self.auth_client = AuthClient(settings.AUTH_SERVICE_URL)
        # In-memory storage for subscriber routing info (in production, use a database)
        self.subscriber_routing = {}
        
        # GSUP Message Types from specification
        self.MSG_UPDATE_LOCATION_REQUEST = 0x04
        self.MSG_UPDATE_LOCATION_RESULT = 0x06
        self.MSG_UPDATE_LOCATION_ERROR = 0x05
        
        self.MSG_SEND_AUTH_INFO_REQUEST = 0x08
        self.MSG_SEND_AUTH_INFO_RESULT = 0x0A
        self.MSG_SEND_AUTH_INFO_ERROR = 0x09
        
        self.MSG_INSERT_DATA_REQUEST = 0x10
        self.MSG_INSERT_DATA_RESULT = 0x12
        self.MSG_INSERT_DATA_ERROR = 0x11
        
        self.MSG_SEND_SUBSCRIBER_DATA_REQUEST = 0x10
        self.MSG_SEND_SUBSCRIBER_DATA_RESULT = 0x11
        self.MSG_SEND_SUBSCRIBER_DATA_ERROR = 0x12
        
        self.MSG_SEND_ROUTING_INFO_FOR_SM_REQUEST = 0x14
        self.MSG_SEND_ROUTING_INFO_FOR_SM_RESULT = 0x15
        self.MSG_SEND_ROUTING_INFO_FOR_SM_ERROR = 0x16

    def _create_ipa_header(self, length: int, proto: int = IPA_PROTO) -> bytes:
        """Create IPA header with length and protocol."""
        return length.to_bytes(2, 'big') + bytes([proto])

    def _create_ccm_identity_response(self) -> bytes:
        """Create CCM Identity Response message."""
        # Helper function to create tag-value pairs
        def make_tag_value(tag: int, value: str) -> bytes:
            encoded_value = value.encode('utf-8')
            return bytes([tag]) + encoded_value + b'\x00'

        # Build the response payload
        payload = bytes([CCM_ID_RESPONSE])  # Message type
        payload += make_tag_value(CCM_TAG_UNIT_ID, "0/0/0")
        payload += make_tag_value(CCM_TAG_MAC_ADDRESS, "00:00:00:00:00:00")
        payload += make_tag_value(CCM_TAG_LOCATION, "")
        payload += make_tag_value(CCM_TAG_UNIT_TYPE, "")
        payload += make_tag_value(CCM_TAG_EQUIPMENT_VERSION, "")
        payload += make_tag_value(CCM_TAG_SOFTWARE_VERSION, "osmo-msc-1.13.0")
        payload += make_tag_value(CCM_TAG_UNIT_NAME, "MSC")
        payload += make_tag_value(CCM_TAG_SERIAL_NUMBER, "unnamed-MSC")

        # Add IPA header
        header = self._create_ipa_header(len(payload))
        return header + payload

    def _create_ccm_pong(self) -> bytes:
        """Create CCM PONG message."""
        payload = bytes([CCM_PONG])
        header = self._create_ipa_header(len(payload))
        return header + payload

    async def start(self):
        """Start the GSUP server."""
        server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming GSUP connection."""
        addr = writer.get_extra_info('peername')
        logger.info(f'New connection from {addr}')

        try:
            while True:
                # Read IPA header (3 bytes)
                header = await reader.read(3)
                if not header:
                    break

                length = int.from_bytes(header[:2], 'big')
                proto = header[2]

                logger.debug(f"Received header: Length: {length}, Protocol: {proto}")


                # Read payload
                payload = await reader.read(length)

                logger.debug(f"Received payload: {payload}")

                if not payload:
                    break

                if proto == IPA_PROTO:
                    # Handle IPA messages
                    msg_type = payload[0] if payload else None
                    logger.debug(f"Received IPA message type: {msg_type:02x}")
                    
                    if msg_type == CCM_PING:
                        logger.info("Received PING, sending PONG")
                        writer.write(self._create_ccm_pong())
                        await writer.drain()
                    
                    elif msg_type == CCM_ID_REQUEST:
                        logger.info("Received Identity Request, sending Identity Response")
                        writer.write(self._create_ccm_identity_response())
                        await writer.drain()
                    
                    elif msg_type == CCM_ID_ACK:
                        logger.info("Received Identity ACK")
                        continue


                else:
                    # This is a GSUP message wrapped in IPA
                    logger.debug(f"Processing GSUP message wrapped in IPA")
                    response = await self.process_message(payload, reader, writer)
                    if response:
                        # Wrap GSUP response in IPA header
                        ipa_response = self._create_ipa_header(len(response)) + response
                        writer.write(ipa_response)
                        await writer.drain()

        except Exception as e:
            logger.error(f'Error handling connection: {e}')
            traceback.print_exc()
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f'Connection closed for {addr}')

    async def process_message(self, message: bytes, reader: asyncio.StreamReader,
                              writer: asyncio.StreamWriter) -> bytes:
        """Process incoming GSUP message and generate response."""
        try:
            msg_type, ies = GSUPCodec.decode_message(message)

            if msg_type == self.MSG_UPDATE_LOCATION_REQUEST:
                logger.debug(f"Received Update Location Request")
                return await self.handle_update_location_request(ies, reader, writer)
            elif msg_type == self.MSG_UPDATE_LOCATION_RESULT:
                logger.debug(f"Received Update Location Result")
                # Handle Update Location Result if needed
                return None
            elif msg_type == self.MSG_INSERT_DATA_RESULT:
                logger.debug(f"Received Insert Data Result")
                return await self.handle_insert_data_result(ies)
            elif msg_type == self.MSG_SEND_AUTH_INFO_REQUEST:
                logger.debug(f"Received Send Authentication Info Request")
                return await self.handle_auth_info_request(ies)
            elif msg_type == self.MSG_SEND_SUBSCRIBER_DATA_REQUEST:
                logger.debug(f"Received Send Subscriber Data Request")
                return await self.handle_subscriber_data_request(ies)
            elif msg_type == self.MSG_SEND_ROUTING_INFO_FOR_SM_REQUEST:
                logger.debug(f"Received Send Routing Info for SM Request")
                return await self.handle_routing_info_for_sm_request(ies)
            else:
                logger.warning(f'Unsupported message type: {msg_type:02x}')
                return None

        except Exception as e:
            logger.error(f'Error processing message: {e}')
            return None

    async def handle_auth_info_request(self, ies: dict) -> bytes:
        """Handle Send Authentication Info request."""
        if IEType.IMSI not in ies:
            return self._create_error_response(
                self.MSG_SEND_AUTH_INFO_ERROR,
                Cause.PROTOCOL_ERROR
            )

        imsi = ies[IEType.IMSI].decode('ascii')
        try:
            logger.info(f"Handling Send Authentication Info request for IMSI: {imsi}")
            # Get authentication data from external service
            auth_data = await self.auth_client.get_auth_data(imsi)
            logger.info(f"Authentication data from PyHSS: {auth_data}")
            
            # Create response with authentication data
            auth_response = GSUPCodec.create_auth_response(
                imsi=imsi,
                rand=bytes.fromhex(auth_data['ki']),  # Using KI as RAND for example
                autn=bytes.fromhex(auth_data['opc'])  # Using OPC as AUTN for example
            )
            logger.info(f"Sending authentication response: {auth_response}")
            return auth_response
        except Exception as e:
            traceback.print_exc()
            logger.error(f'X Error getting auth data: {e}')
            return self._create_error_response(
                self.MSG_SEND_AUTH_INFO_ERROR,
                Cause.IMSI_UNKNOWN
            )

    def _create_error_response(self, msg_type: int, cause: int) -> bytes:
        """Create error response message."""
        ies = {IEType.CAUSE: bytes([cause])}
        return GSUPCodec.encode_message(msg_type, ies)

    async def handle_subscriber_data_request(self, ies: dict) -> bytes:
        """Handle Send Subscriber Data request."""
        if IEType.IMSI not in ies:
            return self._create_error_response(
                self.MSG_INSERT_DATA_ERROR,
                Cause.PROTOCOL_ERROR
            )

        imsi = ies[IEType.IMSI].decode('ascii')
        try:
            # Get subscriber data from external service
            subscriber_data = await self.auth_client.get_auth_data(imsi)
            
            # In a real implementation, you would have additional subscriber data
            # For now, we'll return some default values
            return GSUPCodec.create_subscriber_data_response(
                imsi=imsi,
                msisdn="1234567890",  # This should come from your subscriber database
                subscriber_status=SubscriberStatus.SERVICE_GRANTED,
                network_access_mode=NetworkAccessMode.PACKET_AND_CIRCUIT,
                bearer_services=bytes([0x11, 0x22]),  # Example bearer services
                teleservices=bytes([0x33, 0x44])      # Example teleservices
            )

        except Exception as e:
            logger.error(f'Error getting subscriber data: {e}')
            return self._create_error_response(
                self.MSG_INSERT_DATA_ERROR,
                Cause.SUBSCRIBER_DATA_NOT_AVAILABLE
            )

    async def handle_routing_info_for_sm_request(self, ies: dict) -> bytes:
        """Handle Send Routing Info for SM request."""
        if IEType.IMSI not in ies:
            return self._create_error_response(
                self.MSG_SEND_ROUTING_INFO_FOR_SM_ERROR,
                Cause.PROTOCOL_ERROR
            )

        imsi = ies[IEType.IMSI].decode('ascii')
        try:
            # Get routing info from storage
            routing_info = self.subscriber_routing.get(imsi, {})
            
            if not routing_info:
                # If no routing info is available, return error
                return self._create_error_response(
                    self.MSG_SEND_ROUTING_INFO_FOR_SM_ERROR,
                    Cause.SMS_ROUTING_ERROR
                )

            return GSUPCodec.create_send_routing_info_for_sm_response(
                imsi=imsi,
                msc_number=routing_info.get('msc_number'),
                sgsn_number=routing_info.get('sgsn_number'),
                mme_number=routing_info.get('mme_number')
            )

        except Exception as e:
            logger.error(f'Error getting routing info: {e}')
            return self._create_error_response(
                self.MSG_SEND_ROUTING_INFO_FOR_SM_ERROR,
                Cause.SMS_ROUTING_ERROR
            )

    async def handle_update_location_request(self, ies: dict, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> bytes:
        """
        Handle Update Location request according to 3GPP TS 29.002.
        The procedure consists of:
        1. Receive Update Location Request
        2. Send Insert Data Request
        3. Receive Insert Data Result
        4. Send Update Location Result
        """
        if IEType.IMSI not in ies:
            return self._create_error_response(
                self.MSG_UPDATE_LOCATION_ERROR,
                Cause.PROTOCOL_ERROR
            )

        imsi = ies[IEType.IMSI].decode('ascii')
        logger.info(f"Handling Update Location for IMSI: {imsi}")
        
        try:
            # Get subscriber data from external service
            subscriber_data = await self.auth_client.get_auth_data(imsi)
            
            # Send Insert Data Request
            insert_data_request = GSUPCodec.encode_message(
                self.MSG_INSERT_DATA_REQUEST,
                {
                    IEType.IMSI: imsi.encode('ascii'),
                    IEType.MSISDN: "1234567890".encode('ascii'),  # Should come from subscriber DB
                    IEType.SUBSCRIBER_STATUS: bytes([SubscriberStatus.SERVICE_GRANTED]),
                    IEType.NETWORK_ACCESS_MODE: bytes([NetworkAccessMode.PACKET_AND_CIRCUIT]),
                    IEType.SUBSCRIBER_DATA_FLAGS: bytes([0x01]),  # Example flags
                    IEType.GSM_BEARER_CAPABILITIES: bytes([0x11, 0x22]),  # Example capabilities
                }
            )
            
            # Wrap Insert Data Request in IPA header
            ipa_request = self._create_ipa_header(len(insert_data_request)) + insert_data_request
            writer.write(ipa_request)
            await writer.drain()
            
            # Wait for Insert Data Result
            header = await reader.read(3)  # Read IPA header
            if not header:
                raise RuntimeError("Connection closed while waiting for Insert Data Result")
                
            length = int.from_bytes(header[:2], 'big')
            proto = header[2]
            
            if proto != IPA_PROTO:
                raise RuntimeError(f"Unexpected protocol in response: {proto:02x}")
            
            payload = await reader.read(length)  # Read GSUP payload
            if not payload:
                raise RuntimeError("Connection closed while reading Insert Data Result payload")
            
            msg_type = payload[0]
            if msg_type != self.MSG_INSERT_DATA_RESULT:
                logger.error(f"Unexpected response type: {msg_type:02x}")
                return self._create_error_response(
                    self.MSG_UPDATE_LOCATION_ERROR,
                    Cause.PROTOCOL_ERROR
                )
            
            # Store routing information from the request
            self.subscriber_routing[imsi] = {
                'vlr_number': ies.get(IEType.VLR_NUMBER, b'').decode('ascii') or '12345',
                'msc_number': ies.get(IEType.MSC_NUMBER, b'').decode('ascii') or '67890',
                'sgsn_number': ies.get(IEType.SGSN_NUMBER, b'').decode('ascii') or '11111'
            }
            
            # Send Update Location Result
            return GSUPCodec.encode_message(
                self.MSG_UPDATE_LOCATION_RESULT,
                {
                    IEType.IMSI: imsi.encode('ascii')
                }
            )

        except Exception as e:
            logger.error(f"Error handling Update Location: {e}")
            traceback.print_exc()
            return self._create_error_response(
                self.MSG_UPDATE_LOCATION_ERROR,
                Cause.SUBSCRIBER_DATA_NOT_AVAILABLE
            ) 