<div align="center">
    <h1>Tugas 4 - Ryu Shortest Path</h1>
    <i>Tugas Akhir Mata Kuliah Arsitektur Jaringan Terkini</i>
</div>

## Description
Pada percobaan kali ini, kita akan mencoba <i>routing</i> menggunakan <b>Shortest Path First</b> untuk mencari path terpendek dengan menggunakan Ryu Controller untuk algoritma Dijkstra dan custom topology.

------------------------------------------------------------------------------

## Langkah 1
Sebelum melakukan percobaan untuk <b>Server Load Balancing</b>, maka kita harus membuat dua file <b>Python</b> baru. Yang pertama kita buat file `custom-topo-spf.py` untuk custom topology. Gunakan perintah dibawah ini:

> Note:<br>
> - Pastikan Anda sudah masuk ke direktori `/TugasAkhir/ShortestPathFirstRouting`
> - Kedua source code dibawah ini merupakan source code dari [Shortest Path First Routing](https://github.com/abazh/learn_sdn/tree/main/SPF) oleh Bapak Achmad Basuki ([abazh](https://github.com/abazh))

```bash
nvim custom-topo-spf.py
```

Lalu, masukkan source code di bawah ini ke `custom-topo-spf.py`:

```python
#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from functools import partial

class MyTopo( Topo ):
    "Tugas SDN04 Finding Shortest Paths."

    def addSwitch( self, name, **opts ):
        kwargs = { 'protocols' : 'OpenFlow13'}
        kwargs.update( opts )
        return super(MyTopo, self).addSwitch( name, **kwargs )

    def __init__( self ):
        # Inisialisasi Topology
        "Custom Topology 3 Switch 6 Host - Topology Ring"
        Topo.__init__( self )

        # Add hosts
        info('*** Add Hosts\n')
        h1 = self.addHost('h1', ip='10.1.0.1/8')
        h2 = self.addHost('h2', ip='10.1.0.2/8')
        h3 = self.addHost('h3', ip='10.2.0.3/8')
        h4 = self.addHost('h4', ip='10.2.0.4/8')
        h5 = self.addHost('h5', ip='10.3.0.5/8')
        h6 = self.addHost('h6', ip='10.3.0.6/8')

	    # Add switches
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )

        # Add links host to switch
        self.addLink(s1, h1, 1, 1)
        self.addLink(s2, h2, 1, 1)
        self.addLink(s3, h3, 1, 1)
        self.addLink(s4, h4, 1, 1)
        self.addLink(s5, h5, 1, 1)
        self.addLink(s6, h6, 1, 1)
        # Add links switch to switch
        self.addLink(s1, s2, 2, 2)
        self.addLink(s1, s3, 3, 2)
        self.addLink(s2, s4, 3, 2)
        self.addLink(s2, s5, 4, 2)
        self.addLink(s3, s4, 3, 3)
        self.addLink(s3, s6, 4, 2)
        self.addLink(s4, s5, 4, 3)
        self.addLink(s4, s6, 5, 3)

def run():
    "The Topology for Server - Round Robin LoadBalancing"
    topo = MyTopo()
    net = Mininet( topo=topo, controller=RemoteController, autoSetMacs=True, autoStaticArp=True, waitConnected=True )
    
    info("\n***Disabling IPv6***\n")
    for host in net.hosts:
        print("disable ipv6 in", host)
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    
    for sw in net.switches:
        print("disable ipv6 in", sw)
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")

    info("\n\n************************\n")
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
```

Dengan cara yang sama, simpan file `custom-topo-spf.py` dengan cara tekan tombol `ESC` lalu ketika `:wq`.

Setelah itu, kita baut file baru untuk Ryu Controller yang menggunakan algoritma Dijkstra. Gunakan perintah di bawah ini:

```bash
nvim ryu-spf-dijkstra.py
```

Lalu, masukkan source code di bawah ini:

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import mac
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event, switches
from collections import defaultdict

# switches
switches = []

# mymacs[srcmac]->(switch, port)
mymacs = {}

# adjacency map [sw1][sw2]->port from sw1 to sw2
adjacency = defaultdict(lambda:defaultdict(lambda:None))


# getting the node with lowest distance in Q
def minimum_distance(distance, Q):
    min = float('Inf')
    node = 0
    for v in Q:
        if distance[v] < min:
            min = distance[v]
            node = v
    return node

 

def get_path (src, dst, first_port, final_port):
    # executing Dijkstra's algorithm
    print( "get_path function is called, src=", src," dst=", dst, " first_port=", first_port, " final_port=", final_port)
    
    # defining dictionaries for saving each node's distance and its previous node in the path from first node to that node
    distance = {}
    previous = {}

    # setting initial distance of every node to infinity
    for dpid in switches:
        distance[dpid] = float('Inf')
        previous[dpid] = None

    # setting distance of the source to 0
    distance[src] = 0

    # creating a set of all nodes
    Q = set(switches)

    # checking for all undiscovered nodes whether there is a path that goes through them to their adjacent nodes which will make its adjacent nodes closer to src
    while len(Q) > 0:
        # getting the closest node to src among undiscovered nodes
        u = minimum_distance(distance, Q)
        # removing the node from Q
        Q.remove(u)
        # calculate minimum distance for all adjacent nodes to u
        for p in switches:
            # if u and other switches are adjacent
            if adjacency[u][p] != None:
                # setting the weight to 1 so that we count the number of routers in the path
                w = 1
                # if the path via u to p has lower cost then make the cost equal to this new path's cost
                if distance[u] + w < distance[p]:
                    distance[p] = distance[u] + w
                    previous[p] = u

    # creating a list of switches between src and dst which are in the shortest path obtained by Dijkstra's algorithm reversely
    r = []
    p = dst
    r.append(p)
    # set q to the last node before dst 
    q = previous[p]
    while q is not None:
        if q == src:
            r.append(q)
            break
        p = q
        r.append(p)
        q = previous[p]

    # reversing r as it was from dst to src
    r.reverse()

    # setting path 
    if src == dst:
        path=[src]
    else:
        path=r

    # Now adding in_port and out_port to the path
    r = []
    in_port = first_port
    for s1, s2 in zip(path[:-1], path[1:]):
        out_port = adjacency[s1][s2]
        r.append((s1, in_port, out_port))
        in_port = adjacency[s2][s1]
    r.append((dst, in_port, final_port))
    return r

 

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.datapath_list = []

    def install_path(self, p, ev, src_mac, dst_mac):
       print("install_path function is called!")
       #print( "p=", p, " src_mac=", src_mac, " dst_mac=", dst_mac)
       msg = ev.msg
       datapath = msg.datapath
       ofproto = datapath.ofproto
       parser = datapath.ofproto_parser
       # adding path to flow table of each switch inside the shortest path
       for sw, in_port, out_port in p:
            #print( src_mac,"->", dst_mac, "via ", sw, " in_port=", in_port, " out_port=", out_port)
            # setting match part of the flow table
            match = parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
            # setting actions part of the flow table
            actions = [parser.OFPActionOutput(out_port)]
            # getting the datapath
            datapath = self.datapath_list[int(sw)-1]
            # getting instructions based on the actions
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
            mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=0, hard_timeout=0,
                                                     priority=1, instructions=inst)
            # finalizing the change to switch datapath
            datapath.send_msg(mod)

 
    # defining event handler for setup and configuring of switches
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER)
    def switch_features_handler(self , ev):
        print("switch_features_handler function is called")
        # getting the datapath, ofproto and parser objects of the event
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # setting match condition to nothing so that it will match to anything
        match = parser.OFPMatch()
        # setting action to send packets to OpenFlow Controller without buffering
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
        # setting the priority to 0 so that it will be that last entry to match any packet inside any flow table
        mod = datapath.ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, cookie=0,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            priority=0, instructions=inst)
        # finalizing the mod 
        datapath.send_msg(mod)

 
    # defining an event handler for packets coming to switches event
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # getting msg, datapath, ofproto and parser objects
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # getting the port switch received the packet with
        in_port = msg.match['in_port']
        # creating a packet encoder/decoder class with the raw data obtained by msg
        pkt = packet.Packet(msg.data)
        # getting the protocl that matches the received packet
        eth = pkt.get_protocol(ethernet.ethernet)

        # avoid broadcasts from LLDP 
        if eth.ethertype == 35020 or eth.ethertype == 34525:
            return

        # getting source and destination of the link
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        print("packet in. src=", src, " dst=", dst," dpid=", dpid)

        # add the host to the mymacs of the first switch that gets the packet
        if src not in mymacs.keys():
            mymacs[src] = (dpid, in_port)
            print("mymacs=", mymacs)

        # finding shortest path if destination exists in mymacs
        if dst in mymacs.keys():
            print("destination is known.")
            p = get_path(mymacs[src][0], mymacs[dst][0], mymacs[src][1], mymacs[dst][1])
            self.install_path(p, ev, src, dst)
            print("installed path=", p)
            out_port = p[0][2]
        else:
            print("destination is unknown.Flood has happened.")
            out_port = ofproto.OFPP_FLOOD

        # getting actions part of the flow table
        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                                  actions=actions, data=data)
        datapath.send_msg(out)

    
    # defining an event handler for adding/deleting of switches, hosts, ports and links event
    events = [event.EventSwitchEnter,
              event.EventSwitchLeave, event.EventPortAdd,
              event.EventPortDelete, event.EventPortModify,
              event.EventLinkAdd, event.EventLinkDelete]
    @set_ev_cls(events)
    def get_topology_data(self, ev):
        global switches
        print("get_topology_data is called.")
        # getting the list of known switches 
        switch_list = get_switch(self.topology_api_app, None)  
        switches = [switch.dp.id for switch in switch_list]
        print("current known switches=", switches)
        # getting the list of datapaths from the list of switches
        self.datapath_list = [switch.dp for switch in switch_list]
        # sorting the datapath list based on their id so that indexing them in install_function will be correct
        self.datapath_list.sort(key=lambda dp: dp.id)

        # getting the list of links between switches
        links_list = get_link(self.topology_api_app, None)
        mylinks = [(link.src.dpid,link.dst.dpid,link.src.port_no,link.dst.port_no) for link in links_list]

        # setting adjacency of nodes
        for s1, s2, port1, port2 in mylinks:
            adjacency[s1][s2] = port1
            adjacency[s2][s1] = port2
```

------------------------------------------------------------------------------

## Langkah 2

Langkah kedua adalah membuat terminal baru menggunakan `tmux`. Gunakan perintah `tmux` lalu ketik `CTRL+B %` untuk men-<i>split</i> terminal secara vertikal.

Dan gunakan `CTRL+B O` untuk berpindah ke terminal lain.

Pada terminal 1, ketik perintah di bawah ini untuk menjalankan `custom-topo-spf` menggunakan Mininet.

```bash
sudo python3 custom-topo-spf.py
```

Dan pada terminal 2, ketik perintah di bawah untuk menjalankan Ryu Controller dengan algoritma Dijkstra.

```bash
ryu-manager --observe-links ryu-spf-dijkstra.py
```

> <b>Jalankan terminal 2 terlebih dahulu</b>

Setelah kedua perintah pada masing-masing terminal dijalankan, maka tampilan akan seperti gambar berikut:
<img src="https://daptong.files.wordpress.com/2022/05/t4_tmux5.png"><br>

Selanjutnya, mari kita coba ping/tes konektivitas antar Host. Gunakan perintah di bawah ini untuk ping Host 1 ke Host 4.

```
h1 ping -c 4 h4
```

<img src="https://daptong.files.wordpress.com/2022/05/t4-ping1.png"><br>

Setelah melakukan ping dari Host 1 ke Host 4, maka tampilan pada Ryu Controller akan berubah seperti gambar berikut:
<img src="https://daptong.files.wordpress.com/2022/05/t4-path1.png"><br>

Jadi pada gambar diatas, Ryu Controller berhasil mencari <i>path</i> terpendek menggunakan algoritma Dijkstra. Dapat dilihat pada baris `installed path`, terdapat tiga buah array dengan masing-masing array terdapat tiga kolom.

<img src="https://daptong.files.wordpress.com/2022/05/t4-path1-1.png"><br>

- Pada kolom pertama <span style="color:lightgreen">(Hijau)</span> pada masing-masing array, ini merupakan <b>Switch</b> yang digunakan sebagai jalur. Jadi dari Host 1 ke Host 4, data ICMP (ping) akan melewati Switch 1, lalu ke Switch 2, dan yang terakhir adalah Switch 4
- Pada kolom kedua <span style="color:#7FB5FF">(Biru)</span> pada masing-masing array, ini adalah <b>in_port</b> dari Switch yang digunakan sebagai jalur. Jadi pada Switch 1, in_portnya adalah port 1, pada Switch 2, in_portnya adalah port 2, dan pada Switch 4, in_portnya adalah port 1.
- Pada kolom ketiga <span style="color:red">(Merah)</span> pada masing-masing array, ini adalah <b>out_port</b> dari Switch yang digunakan sebagai jalur. Pada Switch 1, out_portnya adalah port 2, pada Switch 2 out_portnya adalah port 3 dan pada Switch 4, out_portnya adalah port 1.

Selanjutnya, mari kita coba ping antara Host 4 ke Host 2.

```
h2 ping -c 4 h4
```

<img src="https://daptong.files.wordpress.com/2022/05/t4-ping4.png"><br>

Tampilan pada Ryu Controller akan seperti gambar berikut:

<img src="https://daptong.files.wordpress.com/2022/05/t4-path4.png"><br>

- Pada kolom pertama, ini adalah <b>Switch</b> yang dilewati paket ICMP (ping) dari Host 4 ke Host 2, jadi Host yang digunakan untuk mengirim paket adalah yang pertama Switch 2 kemudian ke Switch 4.
- Pada kolom kedua, ini adalah <b>in_port</b> dari masing-masing Switch yang digunakan sebagai jalur. Jadi pada Switch 2, in_portnya adalah port 1, dan pada Switch 4, in_portnya adalah port 2.
- Pada kolom ketiga, ini adalah <b>out_port</b> dari masing-masing Switch yang digunakan sebagai jalur. Jadi pada Switch 2, out_portnya adalah port 3, dan pada Switch 4, out_portnya adalah port 1.

