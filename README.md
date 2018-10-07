# Packet-Sniffer_v-0.1


This is a basic packet sniffer, which i created by following a tutorial by thenewboston Youtube.
This Sniffer classifies data as Ethernet frame or other.
The ethernet frame is further classified as either:
  - IPv4 packet
  The IPv4 packet is further classified as:
    - ICMP (Internet Controll Message Protcol) packet
    - TCP (Transfer Controll Protocol)
    - UDP (User Datagram Protocol)
    - Other

Testing: Download the sniffer.py file and then sudo python sniffer.py and follow the prompts . Copy the Destination IP inside IPv4 datasets to check where the IP is located at 
