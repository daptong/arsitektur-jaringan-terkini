import random
import sys
import warnings
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types, arp, tcp, ipv4

"""
    virtual ip server: 10.0.0.100
    host: h1, h2, h3, h4
    h1 as client web
    h2 - h4 as web server
    h2 - h4 algorithm using round-robin
    
    sudo mn --controller=remote --topo=single,4 --mac
"""


class loadBalancer(app_manager.RyuApp):
    sys.tracebacklimit = 0      # ignore traceback warnings
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(loadBalancer, self).__init__(*args, **kwargs)
        self.virtual_ip = "10.0.0.100"
        self.virtual_mac = "AA:AA:AA:AA:AA:AA"
        self.serverlist = []
        self.counter = 0

        self.serverlist.append({'ip': "10.0.0.2", 'mac': "00:00:00:00:00:02", 'port': "2"})
        self.serverlist.append({'ip': "10.0.0.3", 'mac': "00:00:00:00:00:03", 'port': "3"})
        self.serverlist.append({'ip': "10.0.0.4", 'mac': "00:00:00:00:00:04", 'port': "4"})
        print("Done with initial setup related to server list creation.")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)

        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)

        datapath.send_msg(mod)

    def arp_response(self, dst_ip, dst_mac):
        print("Entered ARP response function to build a packet and reply back appropriately")
        arp_target_ip = dst_ip
        arp_target_mac = dst_mac
        src_ip = self.virtual_ip
        src_mac = self.virtual_mac

        arp_opcode = 2
        hardware_type = 1
        arp_protocol = 2048
        ether_protocol = 2054
        len_of_mac = 6
        len_of_ip = 4

        pkt = packet.Packet()
        ether_frame = ethernet.ethernet(dst_mac, src_mac, ether_protocol)
        arp_reply_pkt = arp.arp(hardware_type, arp_protocol, len_of_mac,
                                len_of_ip, arp_opcode, src_mac, src_ip,
                                arp_target_mac, dst_ip)
        pkt.add_protocol(ether_frame)
        pkt.add_protocol(arp_reply_pkt)
        pkt.serialize()
        print("Exiting ARP response function as done with processing for ARP response packet")

        return pkt

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        warnings.filterwarnings("ignore")       # ignore warnings messages
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("Packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        if eth.ethertype == ether.ETH_TYPE_ARP:
            arp_header = pkt.get_protocols(arp.arp)[0]

            if arp_header.dst_ip == self.virtual_ip and arp_header.opcode == arp.ARP_REQUEST:
                reply_packet = self.arp_response(arp_header.src_ip, arp_header.src_mac)
                actions = [parser.OFPActionOutput(in_port)]
                packet_out = parser.OFPPacketOut(datapath=datapath, in_port=ofproto.OFPP_ANY,
                                                 data=reply_packet.data, actions=actions,
                                                 buffer_id=0xffffffff)
                datapath.send_msg(packet_out)
                print("Debug: Sent the packet out.")

            return

        ip_header = pkt.get_protocols(ipv4.ipv4)[0]
        tcp_header = pkt.get_protocols(tcp.tcp)[0]

        count = self.counter % 3
        server_ip_selected = self.serverlist[count]['ip']
        server_mac_selected = self.serverlist[count]['mac']
        server_outport_selected = self.serverlist[count]['port']
        server_outport_selected = int(server_outport_selected)
        self.counter = self.counter + 1
        print("Selected server: ", server_ip_selected)

        match = parser.OFPMatch(in_port=in_port, eth_type=eth.ethertype,
                                eth_src=eth.src, eth_dst=eth.dst,
                                ip_proto=ip_header.proto, ipv4_src=ip_header.src,
                                ipv4_dst=ip_header.dst, tcp_src=tcp_header.src_port,
                                tcp_dst=tcp_header.dst_port)
        actions = [parser.OFPActionSetField(ipv4_src=self.virtual_ip),
                   parser.OFPActionSetField(eth_src=self.virtual_mac),
                   parser.OFPActionSetField(ipv4_dst=server_ip_selected),
                   parser.OFPActionOutput(server_outport_selected)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        cookie = random.randint(0, 0xffffffffffffffff)
        flow_mod = parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=7,
                                     instructions=inst, buffer_id=msg.buffer_id,
                                     cookie=cookie)
        datapath.send_msg(flow_mod)
        print("Packet from client: "+str(ip_header.src)+
              ". Sent to server: "+str(server_ip_selected)+
              ", MAC: "+str(server_mac_selected)+
              " and on switch port: "+str(server_outport_selected))

        match = parser.OFPMatch(in_port=server_outport_selected, eth_type=eth.ethertype,
                                eth_src=server_mac_selected, eth_dst=self.virtual_mac,
                                ip_proto=ip_header.proto, ipv4_src=server_ip_selected,
                                ipv4_dst=self.virtual_ip, tcp_src=tcp_header.dst_port,
                                tcp_dst=tcp_header.src_port)
        actions = [parser.OFPActionSetField(eth_src=self.virtual_mac),
                   parser.OFPActionSetField(ipv4_src=self.virtual_ip),
                   parser.OFPActionSetField(ipv4_dst=ip_header.src),
                   parser.OFPActionSetField(eth_dst=eth.src),
                   parser.OFPActionOutput(in_port)]
        inst2 = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        cookie = random.randint(0, 0xffffffffffffffff)
        flow_mod2 = parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=7,
                                      instructions=inst2, cookie=cookie)
        datapath.send_msg(flow_mod2)
        print("Reply sent from server: "+str(server_ip_selected)+
              ", MAC: "+str(server_mac_selected)+
              ". Via load balancer: "+str(self.virtual_ip)+
              ". To client: "+str(ip_header.src))
