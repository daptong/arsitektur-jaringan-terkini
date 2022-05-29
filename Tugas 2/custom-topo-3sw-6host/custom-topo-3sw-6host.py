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
