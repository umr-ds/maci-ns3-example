# Network topology
# 
#       n0    n1   n2   n3
#       |     |    |    |
#       =================
#              LAN
#
# - UDP flows from n0 to n1 and back
# - DropTail queues 
# - Tracing of queues and packet receptions to file "udp-echo-py.tr"

import sys

import ns.core
import ns.csma
import ns.applications
import ns.internet	

if __name__ == '__main__':
    
    framework.start()


    #
	# Users may find it convenient to turn on explicit debugging
	# for selected modules; the below lines suggest how to do this
	#
	ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_ALL)

	#
	# Allow the user to override any of the defaults at
	# run-time, via command-line arguments
	#
	cmd = ns.core.CommandLine()
	cmd.useIpv6 = "False"
	cmd.AddValue("useIpv6", "Use Ipv6")
	cmd.Parse(sys.argv)
	
	# 
	# Explicitly create the nodes required by the topology (shown above).
	# 
	print "Create nodes."
	n = ns.network.NodeContainer()
	n.Create(4)
	
	internetstack = ns.internet.InternetStackHelper()
	internetstack.Install(n)
	
	# 
	# Explicitly create the channels required by the topology (shown above).
	# 
	print "Create channels."
	csma = ns.csma.CsmaHelper()
	csma.SetChannelAttribute("DataRate", ns.core.StringValue("5000000"))
	csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
	csma.SetDeviceAttribute("Mtu", ns.core.UintegerValue(1400))
	d = csma.Install(n)
	
	# 
	# We've got the "hardware" in place.  Now we need to add IP addresses.
	# 
	print "Assign IP Addresses."
	ipv4 = ns.internet.Ipv4AddressHelper()
	ipv4.SetBase (ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
	i = ipv4.Assign(d)
	serverAddress = ns.network.Address(i.GetAddress(1))

	print "Create Applications."
	# 
	# Create a UdpEchoServer application on node one.
	#
	port = 9  # well-known echo port number
	server = ns.applications.UdpEchoServerHelper(port)
	serverapps = server.Install(n.Get(1))
	serverapps.Start(ns.core.Seconds(1.0))
	serverapps.Stop(ns.core.Seconds(10.0))
	
	# 
	# Create a UdpEchoClient application to send UDP datagrams from node zero to
	# node one
	#
	packetSize = 1024
	maxPacketCount = 1
	interPacketInterval = ns.core.Seconds(1.0)
	
	client = ns.applications.UdpEchoClientHelper(serverAddress, port)
	client.SetAttribute("MaxPackets", ns.core.UintegerValue(maxPacketCount))
	client.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval))
	client.SetAttribute("PacketSize", ns.core.UintegerValue(packetSize))
	
	apps = client.Install(n.Get(0))
	apps.Start(ns.core.Seconds(2.0))
	apps.Stop(ns.core.Seconds(10.0))
	
	#
	# Users may find it convenient to initialize echo packets with actual data;
	# the below lines suggest how to do this
	#
 	# client.SetFill (apps.Get (0), "Hello World")
	#
	# client.SetFill (apps.Get (0), 0xa5, 1024)
	#
	# Following does not work as intended.
	# fill = [0, 1, 2, 3, 4, 5, 6]
	# client.SetFill (apps.Get (0), fill[0], 1024)

	asciitracer = ns.network.AsciiTraceHelper()
	csma.EnableAsciiAll(asciitracer.CreateFileStream("udp-echo-py.tr"))
	csma.EnablePcapAll("udp-echo-py", False)
	
	# 
	# Now, do the actual simulation.
	# 
	print "Run Simulation."
	ns.core.Simulator.Run()
	ns.core.Simulator.Destroy()
	print "Done."

    framework.stop()