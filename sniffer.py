import socket
import struct
import textwrap
import os
import signal,subprocess
import smtplib
import config



TAB_1="\t - "
TAB_2="\t\t - "
TAB_3="\t\t\t - "
TAB_4="\t\t\t\t - "

DATA_TAB_1="\t "
DATA_TAB_2="\t\t "
DATA_TAB_3="\t\t\t "
DATA_TAB_4="\t\t\t\t "

def main():
    conn = socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.ntohs(3))
    
    print("\n\nWelcome to packet sniffer v 0.1:!\n\n")
    print("Would you like us to sniff your packets? (yes/no)")
    choice=input()
    if choice=="no":
        print("Thank you for your time!")
        return 0
    
    print("Sniffing has begun!!- u will get tons of output shortly")
    while True:
        raw_data,addr=conn.recvfrom(65536)
        d_mac,s_mac,eth_prot,data=ethernet_frame(raw_data)
        print("\nEthernet Frame:")
        print(TAB_1+"Destination = {}, Source = {}, Protocol = {}".format(d_mac,s_mac,eth_prot))

        if eth_prot == 8:
            version,header_length,ttl,proto,src,target,data=ipv4_packet(data)
            print(TAB_1+"IPv4 Packet:")
            print(TAB_2+"Version = {}, Header Length= {}, TTL = {}".format(version,header_length,ttl))
            print(TAB_2+"Protocol = {}, Source= {}, Target = {}".format(proto,src,target))
            
            
            if src=='157.240.23.25':
                print("\n\n!!Dont try to open Facebook!!\n\n")
                subject="Test email"
                message="Its working!!"
                try:
                    email_sender(subject,message)
                except:
                    process_killer()
                return 0
            if src=='152.195.33.132':
                print("\n\nYou are not allowed to open this site!\n\n")
                return 0
            if src=='208.65.153.238' or src=='208.65.153.251' or src=='208.65.153.253' or src=='208.117.236.69':
                print("\n\nYoutube detected!!\n\n")
                return 0
            
            
            
            
            
            
            #ICMP
            if proto == 1:
                icmp_type,code,checksum,data=icmp_packet(data)
                print(TAB_1+"ICMP Packet:")
                print(TAB_2+"Type = {}, Code = {}, Checksum = {}".format(icmp_type,code,checksum))
                print(format_multi_line(DATA_TAB_3,data))

            #TCP
            elif proto == 6:
                src_port,dest_port,seq,ack,flag_urg,flag_ack,flag_psh,flag_rst,flag_syn,flag_fin,data=tcp_segment(data)
                print(TAB_1+"TCP Packet:")
                print(TAB_2+"Source port = {}, Destination port = {}".format(src_port,dest_port))
                print(TAB_2+"Sequence = {}, Acknowledgement = {}".format(seq,ack))
                print(TAB_2+"Flags:")
                print(TAB_3+"URG = {}, ACK = {}, PSH = {}, RST = {}, SYN = {}, FIN = {}".format(flag_urg,flag_ack,flag_psh,flag_rst,flag_syn,flag_fin))
                print(TAB_2+"Data:")
                print(format_multi_line(DATA_TAB_3,data))
            

            #UDP
            elif proto == 17:
                src_port,dest_port,size,data=udp_segment(data)
                print(TAB_1+"UDP Packet:")
                print(TAB_2+"Source port = {}, Destination port = {}, Size = {}".format(src_port,dest_port,size))
                print(TAB_2+"Data:")
                print(format_multi_line(DATA_TAB_3,data))
            
            #OTHER
            else:
                print(TAB_1+"Data:")
                print(format_multi_line(DATA_TAB_2,data))
        
        #other
        else:
            print("Data:")
            print(format_multi_line(DATA_TAB_1,data))


# unpack the ethernet frame
def ethernet_frame(data):
    dest_mac,src_mac,proto = struct.unpack('! 6s 6s H',data[:14])
    return get_mac_addr(dest_mac),get_mac_addr(src_mac),socket.htons(proto),data[14:]


#return properly formated mac address
def get_mac_addr(bytes_addr):
    bytes_addr=map('{:02x}'.format,bytes_addr)
    return ":".join(bytes_addr).upper()



#Unpack ipv4 packets
def ipv4_packet(data):
    version_header_length = data[0]
    version = version_header_length>>4
    header_length= (version_header_length & 15) *4
    ttl,proto,src,dest=struct.unpack('! 8x B B 2x 4s 4s',data[:20])
    return version,header_length,ttl,proto,ipv4(src),ipv4(dest),data[header_length:]

# REformat 1pv4 packet
def ipv4(addr):
    return '.'.join(map(str,addr))

# unpack icmp packet
def icmp_packet(data):
    icmp_type,code,checksum=struct.unpack('! B B H',data[:4])
    return icmp_type,code,checksum,data[4:]

# unpack tcp packet
def tcp_segment(data):
    src_port,dest_port,seq,ack,offset_reserved_flags = struct.unpack('! H H L L H',data[:14])
    offset=(offset_reserved_flags>>12) * 4
    flag_urg = (offset_reserved_flags & 32)>>5
    flag_ack = (offset_reserved_flags & 16)>>4
    flag_psh = (offset_reserved_flags & 8)>>3
    flag_rst = (offset_reserved_flags & 4)>>2
    flag_syn = (offset_reserved_flags & 2)>>1
    flag_fin = offset_reserved_flags & 1
    return src_port,dest_port,seq,ack,flag_urg,flag_ack,flag_psh,flag_rst,flag_syn,flag_fin,data[offset:]


# unpack udp segment
def udp_segment(data):
    src_port,dest_port,size = struct.unpack('! H H 2x H',data[:8])
    return src_port,dest_port,size,data[8:]

# formats multiline data
def format_multi_line(prefix,string,size=80):
    size-=len(prefix)
    if isinstance(string,bytes):
        string=''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size-=1
    return '\n'.join([prefix+line for line in textwrap.wrap(string,size)])



def process_killer():
    p=subprocess.Popen(['ps','-A'],stdout=subprocess.PIPE)
    out,err=p.communicate()
    lines=out.splitlines()
    for line in lines:
        ele=line.split()
        for i in ele:
            if i == b'chrome':
                pid=int(ele[0])
                os.kill(pid,signal.SIGKILL)


def email_sender(subject,msg):
    try:
        server=smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL,config.PASSWORD)
        message = ('Subject: {}\n\n{}'.format(subject,msg))
        server.sendmail(config.EMAIL,config.EMAIL,message)
        print('Email sent!')
        server.quit()
    except:
        print('Failed to send email!')

if __name__ == '__main__':
    main()