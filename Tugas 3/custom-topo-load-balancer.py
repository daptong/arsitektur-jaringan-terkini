from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.util import dumpNodeConnnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from functools import partial

class customTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        info('*** Add switch\n')
        s1 = self.addSwitch('s1', protocols = 'OpenFlow13')

        info('*** Add hosts\n')
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        info('*** Add links\n')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

def run():
    topo = customTopo()
    net = Mininet(topo = topo, controller = RemoteController, autoSetMacs = True, waitConnected = True)

    info('\n*** Disabling IPv6\n')
    for host in net.hosts:
        print('Disabling IPv6 in', host)
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")

    for sw in net.switches:
        print('Disabling IPv6 in, sw')
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")

    info('\n*** Running Web Server\n')
    for web in ["h2", "h3", "h4"]:
        info("Web Server running in", web, net[web].cmd("python -m http.server 80 &"))

    net.start()
    net.pingAll()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
