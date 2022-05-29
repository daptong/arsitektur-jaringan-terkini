<div align="center">
    <h1>Custom Topology 3 Switches and 6 Hosts + Spanning Tree</h1>
    <i>Tugas 2 - Tugas Akhir Mata Kuliah Arsitektur Jaringan Terkini</i>
</div>

## Langkah 1
Untuk Custom Topology dengan 3 Switch dan 6 Host, maka silahkan buat program baru bernama `custom-topo-3sw-6host.py`. Caranya adalah menggunakan Neovim. Masukkan perintah berikut ke terminal:

```bash
nvim custom-topo-3sw-6host.py
```
Setelah itu, klik tombol <b>I</b> di keyboard untuk mengisi code untuk `custom-topo-2sw-2host.py`. Isi code dengan code dibawah ini:

```python
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI

class customTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        info('*** Add switches\n')
        s1 = self.addSwitch('s1', mac = '00:00:00:00:00:01', protocols = 'OpenFlow13')
        s2 = self.addSwitch('s2', mac = '00:00:00:00:00:02', protocols = 'OpenFlow13')
        s3 = self.addSwitch('s3', mac = '00:00:00:00:00:03', protocols = 'OpenFlow13')

        info('*** Add hosts\n')
        h1 = self.addHost('h1', mac = '00:00:00:00:00:04', ip = '10.1.0.1/8')
        h2 = self.addHost('h2', mac = '00:00:00:00:00:05', ip = '10.1.0.2/8')
        h3 = self.addHost('h3', mac = '00:00:00:00:00:06', ip = '10.2.0.3/8')
        h4 = self.addHost('h4', mac = '00:00:00:00:00:07', ip = '10.2.0.4/8')
        h5 = self.addHost('h5', mac = '00:00:00:00:00:08', ip = '10.3.0.5/8')
        h6 = self.addHost('h6', mac = '00:00:00:00:00:09', ip = '10.3.0.6/8')

        info('*** Add links\n')
        self.addLink(h1, s1, port1=1, port2=2)
        self.addLink(h2, s1, port1=1, port2=3)
        self.addLink(h3, s2, port1=1, port2=3)
        self.addLink(h4, s2, port1=1, port2=4)
        self.addLink(h5, s3, port1=1, port2=2)
        self.addLink(h6, s3, port1=1, port2=1)

        self.addLink(s1, s2, port1=4, port2=2)
        self.addLink(s1, s3, port1=1, port2=3)
        self.addLink(s2, s3, port1=1, port2=4)

topos = {'customtopo': (lambda: customTopo())}
```

Setelah mengisi code diatas, maka klik tombol <b>ESC</b> di keyboard lalu ketik <b>:wq</b> untuk menyimpan file `custom-topo-3sw-6host.py`

--------------------------------------------------------------------------------

## Langkah 2
Langkah selanjutnya adalah menjalankan `custom-topo-3sw-6host` menggunakan Mininet + Ryu. Ryu disini akan menggunakan protocol Spanning Tree.<br>

> Pastikan Anda sudah masuk ke direktori ``TugasAkhir/CustomTopologyMininet``

Gunakan <b>tmux</b> agar bisa menggunakan dua terminal sekaligus.

Pada terminal 1, silahkan masukkan perintah dibawah ini untuk menjalankan Mininet:

```
sudo mn --custom custom-topo-3sw-6host.py --topo=customtopo --controller=remote --switch=ovsk
```

Dan pada terminal 2, silahkan masukkan perintah dibawah ini untuk menjalakan Ryu dengan protocol Spanning Tree:

```
ryu-manager ryu.app.simple_switch_stp_13
```

> <b>Jalankan terminal kedua terlebih dahulu</b>

Setelah menjalankan kedua terminal / perintah, maka tampilan akan berubah seperti dibawah ini: <br>

Selanjutnya ada mencoba / tes konektivitas antara Hosts dengan cara:

```
pingall
```

Nantinya, akan ada beberapa Host yang tidak bisa `ping` ke Host yang lain. Seperti contoh pada gambar berikut: <br>
<img src="https://daptong.files.wordpress.com/2022/05/t2_pingall1.png"><br>

Ini dapat disebabkan karena terjadinya looping pada proses pengiriman data. Untuk mencegah hal itu, maka kita bisa gunakan <b>Spanning Tree</b> dengan menggunakan perintah dibawah ini untuk menggunakan protocol <b>Spanning Tree</b> pada setiap Switch:

```
sh ovs-vsctl set bridge s1 stp-enable=true
sh ovs-vsctl set bridge s2 stp-enable=true
sh ovs-vsctl set bridge s3 stp-enable=true
```

Setelah kita menggunakan protocol <b>Spanning Tree</b>, maka selanjutnya kita <i>cross-check</i> dengan melihat tabel <i>flows</i> dengan cara:

```
dpctl dump-flows -O OpenFlow13
```

Tampilan tabel <i>flows</i> akan seperti gambar di bawah ini:<br>
<img src="https://daptong.files.wordpress.com/2022/05/t2_dpctl2.png"><br>

Dapat dilihat, ada beberapa column `action` yang memiliki nilai <b>`DROP`</b>, ini dikarenakan protocol <b>Spanning Tree</b> berhasil dijalankan dan berhasil mencegah terjadinya looping pada saat pengiriman data. Dan pada terminal 2, ketika ada proses looping, maka `DESIGNATED_PORT` akan memblokir portnya dan men-<b>DROP</b> data tersebut untuk mencegah proses looping terjadi.

--------------------------------------------------------------------------------

## Tambahan
Buatlah program Ryu bernama `simple_switch_stp_13.py` pada direktori `/CustomTopologyMininet` dengan cara:

```bash
nvim simple_switch_stp_13.py
```

Lalu, masukkan code dibawah ini:

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app import simple_switch_13


class SimpleSwitch13(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']

        # Sample of stplib config.
        #  please refer to stplib.Stp.set_config() for details.
        config = {dpid_lib.str_to_dpid('0000000000000001'):
                  {'bridge': {'priority': 0x8000}},
                  dpid_lib.str_to_dpid('0000000000000002'):
                  {'bridge': {'priority': 0x9000}},
                  dpid_lib.str_to_dpid('0000000000000003'):
                  {'bridge': {'priority': 0xa000}}}
        self.stp.set_config(config)

    def delete_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(
                datapath, command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                priority=1, match=match)
            datapath.send_msg(mod)

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(stplib.EventTopologyChange, MAIN_DISPATCHER)
    def _topology_change_handler(self, ev):
        dp = ev.dp
        dpid_str = dpid_lib.dpid_to_str(dp.id)
        msg = 'Receive topology change event. Flush MAC table.'
        self.logger.debug("[dpid=%s] %s", dpid_str, msg)

        if dp.id in self.mac_to_port:
            self.delete_flow(dp)
            del self.mac_to_port[dp.id]

    @set_ev_cls(stplib.EventPortStateChange, MAIN_DISPATCHER)
    def _port_state_change_handler(self, ev):
        dpid_str = dpid_lib.dpid_to_str(ev.dp.id)
        of_state = {stplib.PORT_STATE_DISABLE: 'DISABLE',
                    stplib.PORT_STATE_BLOCK: 'BLOCK',
                    stplib.PORT_STATE_LISTEN: 'LISTEN',
                    stplib.PORT_STATE_LEARN: 'LEARN',
                    stplib.PORT_STATE_FORWARD: 'FORWARD'}
        self.logger.debug("[dpid=%s][port=%d] state=%s",
                          dpid_str, ev.port_no, of_state[ev.port_state])
```
