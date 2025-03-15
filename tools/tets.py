from scapy.all import *
import time

# MME IP and S1AP Port
MME_IP = "localhost"
S1AP_PORT = 36412

# Create an S1AP Attach Request Packet
s1ap_attach_request = (
    IP(dst=MME_IP) /
    UDP(dport=S1AP_PORT, sport=RandShort()) /
    Raw(load=b'\x00\x08\x00\x00\x04\x00\x02\x00\x00\x00\x01')  # Dummy S1AP payload
)

# Send the packet and wait for a response
print(f"📡 Sending S1AP Attach Request to MME at {MME_IP}:{S1AP_PORT}")
response = sr1(s1ap_attach_request, timeout=3, verbose=True)

# Check if we got a response
if response:
    print(f"✅ Response received from {response.src}")
    response.show()
else:
    print("❌ No response from MME. Check S1AP connectivity and logs.")