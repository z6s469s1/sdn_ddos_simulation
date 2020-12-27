#!/usr/bin/env python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

CORES = {
	'cs1': {'dpid': '000000000000010%s'},
	'as1': {'dpid': '000000000000020%s'},
	'as2': {'dpid': '000000000000030%s'},
	'es1': {'dpid': '000000000000040%s'},
	'es2': {'dpid': '000000000000050%s'},
	'es3': {'dpid': '000000000000060%s'},
	'es4': {'dpid': '000000000000070%s'},
}

class TreeTopo(Topo):

	"Tree topology."
	def __init__(self, k=2, **opts):
		"""Init.
		hconf: host configuration options
		lconf: link configuration options"""
		super(TreeTopo, self).__init__(**opts)
		linkopts = dict(cls=TCLink)#, bw=10, delay='5ms', loss=10, use_hbt=True)
		self.cores = {}
		for switch in CORES:
			switch_obj = self.addSwitch(switch, dpid=(CORES[switch]['dpid'] % '0'))
			self.cores[switch] = switch_obj

		total_count = 1
		for switch in ['es1', 'es2', 'es3', 'es4']:
			for count in range(1, 3):
				host = 'h%s' % total_count
				ip = '10.0.0.%s' % total_count
				total_count = total_count + 1
				mac = CORES[switch]['dpid'][4:] % count
				h = self.addHost(host, ip=ip, mac=mac)
				self.addLink(h, self.cores[switch],bw=20, use_htb=True )
		
		self.addLink(self.cores['cs1'], self.cores['as1'],bw=50,   use_htb=True )
		self.addLink(self.cores['cs1'], self.cores['as2'],bw=50,   use_htb=True )
		self.addLink(self.cores['as1'], self.cores['es1'],bw=50,   use_htb=True )
		self.addLink(self.cores['as1'], self.cores['es2'],bw=50,   use_htb=True )
		self.addLink(self.cores['as2'], self.cores['es3'],bw=50,   use_htb=True )
		self.addLink(self.cores['as2'], self.cores['es4'],bw=50,   use_htb=True )
		
		

def simpleTest():
	"Create and test a simple network"
	topo = TreeTopo()
	#net = Mininet(topo, controller = RemoteController('c0', ip = '0.0.0.0', port = 6653))
	net = Mininet(topo, controller = RemoteController('c0', ip = '0.0.0.0', port = 6653), link=TCLink)
	# net = Mininet(topo, controller = RemoteController('c0', ip = '0.0.0.0', port = 10000))
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	#print "Testing network connectivity"
	#net.pingAll()
	CLI(net)
	net.stop()

topos = {'treetopo': (lambda: TreeTopo())}

if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest()
