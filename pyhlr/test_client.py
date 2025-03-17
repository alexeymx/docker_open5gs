#!/usr/bin/env python3
import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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

@dataclass
class GSUPMessage:
    """Represents a GSUP message with its type and IEs."""
    message_type: int
    ies: Dict[int, bytes]

class GSUPTestClient:
    """Test client for GSUP protocol."""

    # Message Types from GSUP specification
    MSG_UPDATE_LOCATION_REQUEST = 0x04
    MSG_UPDATE_LOCATION_RESULT = 0x06
    MSG_UPDATE_LOCATION_ERROR = 0x05
    
    MSG_INSERT_DATA_REQUEST = 0x10
    MSG_INSERT_DATA_RESULT = 0x12
    MSG_INSERT_DATA_ERROR = 0x11
    
    MSG_SEND_AUTH_INFO_REQUEST = 0x08
    MSG_SEND_AUTH_INFO_RESULT = 0x0A
    MSG_SEND_AUTH_INFO_ERROR = 0x09
    
    MSG_SEND_SUBSCRIBER_DATA_REQUEST = 0x10
    MSG_SEND_SUBSCRIBER_DATA_RESULT = 0x11
    MSG_SEND_SUBSCRIBER_DATA_ERROR = 0x12
    
    MSG_SEND_ROUTING_INFO_FOR_SM_REQUEST = 0x14
    MSG_SEND_ROUTING_INFO_FOR_SM_RESULT = 0x15
    MSG_SEND_ROUTING_INFO_FOR_SM_ERROR = 0x16

    # Information Element Types
    IE_IMSI = 0x01
    IE_CAUSE = 0x02
    IE_AUTH_TUPLE = 0x03
    IE_RAND = 0x04
    IE_SRES = 0x05
    IE_KC = 0x06
    IE_IK = 0x07
    IE_CK = 0x08
    IE_AUTN = 0x09
    IE_AUTS = 0x0A
    IE_RES = 0x0B
    IE_MSISDN = 0x0C
    IE_SUBSCRIBER_STATUS = 0x0D
    IE_NETWORK_ACCESS_MODE = 0x0E
    IE_VLR_NUMBER = 0x10
    IE_MSC_NUMBER = 0x11
    IE_GSM_BEARER_CAPABILITIES = 0x12

    def __init__(self, host: str = "localhost", port: int = 4222):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    def _create_ipa_header(self, length: int, proto: int = IPA_PROTO) -> bytes:
        """Create IPA header with length and protocol."""
        return length.to_bytes(2, 'big') + bytes([proto])

    def _create_ccm_ping(self) -> bytes:
        """Create CCM PING message."""
        payload = bytes([CCM_PING])
        header = self._create_ipa_header(len(payload))
        return header + payload

    def _create_ccm_id_request(self) -> bytes:
        """Create CCM Identity Request message."""
        # Add all required tags without values
        payload = bytes([CCM_ID_REQUEST])
        for tag in [CCM_TAG_UNIT_ID, CCM_TAG_MAC_ADDRESS, CCM_TAG_LOCATION,
                   CCM_TAG_UNIT_TYPE, CCM_TAG_EQUIPMENT_VERSION,
                   CCM_TAG_SOFTWARE_VERSION, CCM_TAG_UNIT_NAME,
                   CCM_TAG_SERIAL_NUMBER]:
            payload += bytes([tag])
        header = self._create_ipa_header(len(payload))
        return header + payload

    def _create_ccm_id_ack(self) -> bytes:
        """Create CCM Identity ACK message."""
        payload = bytes([CCM_ID_ACK])
        header = self._create_ipa_header(len(payload))
        return header + payload

    async def _read_ipa_message(self) -> Tuple[int, bytes]:
        """Read an IPA message and return protocol and payload."""
        if not self.reader:
            raise RuntimeError("Not connected")

        # Read IPA header
        header = await self.reader.read(3)
        if not header:
            raise RuntimeError("Connection closed by server")

        length = int.from_bytes(header[:2], 'big')
        proto = header[2]

        # Read payload
        payload = await self.reader.read(length)
        if not payload:
            raise RuntimeError("Connection closed by server")

        return proto, payload

    async def connect(self):
        """Connect to the HLR server and perform IPA handshake."""
        logger.info(f"Connecting to HLR at {self.host}:{self.port}")
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        logger.info("Connected successfully")

        # Perform IPA handshake
        # 1. Send Identity Request
        logger.info("Sending Identity Request")
        self.writer.write(self._create_ccm_id_request())
        await self.writer.drain()

        # 2. Receive Identity Response
        proto, payload = await self._read_ipa_message()
        if proto != IPA_PROTO or payload[0] != CCM_ID_RESPONSE:
            raise RuntimeError("Unexpected response to Identity Request")
        logger.info("Received Identity Response")

        # 3. Send Identity ACK
        logger.info("Sending Identity ACK")
        self.writer.write(self._create_ccm_id_ack())
        await self.writer.drain()

        # 4. Send initial PING
        logger.info("Sending PING")
        self.writer.write(self._create_ccm_ping())
        await self.writer.drain()

        # 5. Receive PONG
        proto, payload = await self._read_ipa_message()
        if proto != IPA_PROTO or payload[0] != CCM_PONG:
            raise RuntimeError("Unexpected response to PING")
        logger.info("Received PONG")

    async def close(self):
        """Close the connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("Connection closed")

    def _encode_message(self, msg_type: int, ies: Dict[int, bytes]) -> bytes:
        """Encode a GSUP message."""
        message = bytearray()
        message.extend([msg_type])  # Message type

        # Encode IEs
        for ie_type, value in ies.items():
            ie = bytearray()
            ie.extend([ie_type, len(value)])  # IE header
            ie.extend(value)  # IE value
            message.extend(ie)

        return bytes(message)

    def _decode_message(self, data: bytes) -> GSUPMessage:
        """Decode a GSUP message."""
        if not data:
            raise RuntimeError("Empty message received")
            
        msg_type = data[0]
        
        ies = {}
        offset = 1  # Skip message type

        while offset < len(data):
            if offset + 2 > len(data):
                logger.error(f"Malformed message: not enough bytes for IE header at offset {offset}")
                break
                
            ie_type = data[offset]
            ie_length = data[offset + 1]
            
            if offset + 2 + ie_length > len(data):
                logger.error(f"Malformed message: not enough bytes for IE value at offset {offset}")
                break
                
            ie_value = data[offset + 2:offset + 2 + ie_length]
            ies[ie_type] = ie_value
            offset += 2 + ie_length

        return GSUPMessage(msg_type, ies)

    async def send_and_receive(self, msg_type: int, ies: Dict[int, bytes]) -> GSUPMessage:
        """Send a message and wait for response."""
        if not self.writer or not self.reader:
            raise RuntimeError("Not connected")

        # Encode GSUP message
        message = self._encode_message(msg_type, ies)
        logger.debug(f"Sending GSUP message type: {msg_type:02x}, length: {len(message)}")
        
        # Wrap in IPA header
        ipa_message = self._create_ipa_header(len(message)) + message
        
        # Send message
        self.writer.write(ipa_message)
        await self.writer.drain()

        # Read response (IPA header)
        header = await self.reader.read(3)
        if not header:
            raise RuntimeError("Connection closed by server")
            
        length = int.from_bytes(header[:2], 'big')
        proto = header[2]
        
        if proto != IPA_PROTO:
            raise RuntimeError(f"Unexpected protocol in response: {proto:02x}")
            
        # Read GSUP payload
        payload = await self.reader.read(length)
        if not payload:
            raise RuntimeError("Connection closed while reading GSUP payload")
            
        logger.debug(f"Received GSUP message, length: {len(payload)}")
        return self._decode_message(payload)

    async def test_auth_info(self, imsi: str) -> bool:
        """Test Send Authentication Info operation."""
        logger.info(f"Testing Send Authentication Info for IMSI: {imsi}")
        
        response = await self.send_and_receive(
            self.MSG_SEND_AUTH_INFO_REQUEST,
            {self.IE_IMSI: imsi.encode('ascii')}
        )

        success = response.message_type == self.MSG_SEND_AUTH_INFO_RESULT
        if success:
            logger.info("Authentication Info request successful")
            logger.info(f"Received RAND: {response.ies.get(self.IE_RAND, b'').hex()}")
            logger.info(f"Received AUTN: {response.ies.get(self.IE_AUTN, b'').hex()}")
        else:
            logger.error("Authentication Info request failed")
            if self.IE_CAUSE in response.ies:
                logger.error(f"Cause: {response.ies[self.IE_CAUSE][0]}")

        return success

    async def test_subscriber_data(self, imsi: str) -> bool:
        """Test Send Subscriber Data operation."""
        logger.info(f"Testing Send Subscriber Data for IMSI: {imsi}")
        
        response = await self.send_and_receive(
            self.MSG_SEND_SUBSCRIBER_DATA_REQUEST,
            {self.IE_IMSI: imsi.encode('ascii')}
        )

        success = response.message_type == self.MSG_SEND_SUBSCRIBER_DATA_RESULT
        if success:
            logger.info(f"Subscriber Data request successful {response}")
            if self.IE_MSISDN in response.ies:
                logger.info(f"MSISDN: {response.ies[self.IE_MSISDN].decode('ascii')}")
            if self.IE_SUBSCRIBER_STATUS in response.ies:
                logger.info(f"Subscriber Status: {response.ies[self.IE_SUBSCRIBER_STATUS][0]}")
        else:
            logger.error("Subscriber Data request failed")
            if self.IE_CAUSE in response.ies:
                logger.error(f"Cause: {response.ies[self.IE_CAUSE][0]}")

        return success

    async def test_update_location(self, imsi: str) -> bool:
        """
        Test Update Location procedure according to 3GPP TS 29.002.
        
        The procedure flow is:
        1. Send Update Location Request
        2. Receive Insert Subscriber Data Request
        3. Send Insert Subscriber Data Result
        4. Receive Update Location Result
        """
        logger.info(f"Testing Update Location for IMSI: {imsi}")
        logger.info("Step 1: Sending Update Location Request")
        
        # Example VLR and MSC numbers
        vlr_number = "49123456789"
        msc_number = "49987654321"
        
        # Send Update Location Request
        response = await self.send_and_receive(
            self.MSG_UPDATE_LOCATION_REQUEST,
            {
                self.IE_IMSI: imsi.encode('ascii'),
                self.IE_VLR_NUMBER: vlr_number.encode('ascii'),
                self.IE_MSC_NUMBER: msc_number.encode('ascii')
            }
        )
        
        # We expect to receive Insert Subscriber Data Request first
        if response.message_type != self.MSG_INSERT_DATA_REQUEST:
            logger.error(f"Unexpected message type: {response.message_type:02x}, expected Insert Data Request ({self.MSG_INSERT_DATA_REQUEST:02x})")
            return False
            
        logger.info("Step 2: Received Insert Subscriber Data Request")
        # Log received subscriber data
        if self.IE_MSISDN in response.ies:
            logger.info(f"Received MSISDN: {response.ies[self.IE_MSISDN].decode('ascii')}")
        if self.IE_SUBSCRIBER_STATUS in response.ies:
            logger.info(f"Subscriber Status: {response.ies[self.IE_SUBSCRIBER_STATUS][0]}")
        if self.IE_NETWORK_ACCESS_MODE in response.ies:
            logger.info(f"Network Access Mode: {response.ies[self.IE_NETWORK_ACCESS_MODE][0]}")
        if self.IE_GSM_BEARER_CAPABILITIES in response.ies:
            logger.info(f"Bearer Capabilities: {response.ies[self.IE_GSM_BEARER_CAPABILITIES].hex()}")
            
        logger.info("Step 3: Sending Insert Subscriber Data Result")
        # Send Insert Subscriber Data Result
        response = await self.send_and_receive(
            self.MSG_INSERT_DATA_RESULT,
            {
                self.IE_IMSI: imsi.encode('ascii')
            }
        )
        
        logger.info("Step 4: Waiting for Update Location Result")
        # Now we should receive Update Location Result
        success = response.message_type == self.MSG_UPDATE_LOCATION_RESULT
        if success:
            logger.info("Update Location procedure completed successfully")
        else:
            logger.error(f"Update Location procedure failed, received message type: {response.message_type:02x}, expected: {self.MSG_UPDATE_LOCATION_RESULT:02x}")
            if self.IE_CAUSE in response.ies:
                logger.error(f"Cause: {response.ies[self.IE_CAUSE][0]}")
                
        return success

    async def test_routing_info_for_sm(self, imsi: str) -> bool:
        """Test Send Routing Info for SM operation."""
        logger.info(f"Testing Send Routing Info for SM for IMSI: {imsi}")
        
        # Example SM-RP-DA and SM-RP-OA values
        sm_rp_da = b'\x91\x44\x77\x58\x10\x06\x50\xf0'  # Example MSISDN in encoded form
        sm_rp_oa = b'\x91\x44\x77\x58\x10\x06\x40\xf0'  # Example Service Centre Address
        
        response = await self.send_and_receive(
            self.MSG_SEND_ROUTING_INFO_FOR_SM_REQUEST,
            {
                self.IE_IMSI: imsi.encode('ascii'),
                0x14: sm_rp_da,  # SM_RP_DA
                0x15: sm_rp_oa   # SM_RP_OA
            }
        )

        success = response.message_type == self.MSG_SEND_ROUTING_INFO_FOR_SM_RESULT
        if success:
            logger.info("Send Routing Info for SM successful")
            # Log routing numbers if present
            for ie_type, name in [(0x11, "MSC"), (0x12, "SGSN"), (0x13, "MME")]:
                if ie_type in response.ies:
                    logger.info(f"{name} Number: {response.ies[ie_type].decode('ascii')}")
        else:
            logger.error("Send Routing Info for SM failed")
            if self.IE_CAUSE in response.ies:
                logger.error(f"Cause: {response.ies[self.IE_CAUSE][0]}")

        return success

async def main():
    # Get HLR host and port from environment or use defaults
    hlr_host = os.getenv("HLR_HOST", "localhost")
    hlr_port = int(os.getenv("HLR_PORT", "4222"))
    
    # Test IMSI
    test_imsi = "001017890123453"  # Example IMSI
    
    client = GSUPTestClient(hlr_host, hlr_port)
    
    try:
        await client.connect()
        
        # Test all operations
        operations = [
            ("Authentication Info", client.test_auth_info),
            ("Subscriber Data", client.test_subscriber_data),
            ("Update Location", client.test_update_location),
            ("Routing Info for SM", client.test_routing_info_for_sm)
        ]
        
        results = []
        for name, test_func in operations:
            try:
                success = await test_func(test_imsi)
                results.append((name, success))
            except Exception as e:
                logger.error(f"Error testing {name}: {e}")
                results.append((name, False))
        
        # Print summary
        print("\nTest Results Summary:")
        print("-" * 40)
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{name:20} {status}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main()) 