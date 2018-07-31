### ENV int bandwidth "BW"
### ENV int delay "Delay"
### ENV int packetSize "Packet Size"
### ENV int maxPacketCount "Count"
### ENV float interval "Interval"

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

import framework
import sys

import ns.core
import ns.csma
import ns.applications
import ns.internet
import ns.netanim

if __name__ == '__main__':

    framework.start()
    
    #ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_ALL)
    #ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_ALL)
    
    cmd = ns.core.CommandLine()
    cmd.useIpv6 = "False"
    cmd.AddValue("useIpv6", "Use Ipv6")
    cmd.Parse(sys.argv)
    
    print "Create nodes."
    n = ns.network.NodeContainer()
    n.Create(4)
	
    internetstack = ns.internet.InternetStackHelper()
    internetstack.Install(n)
    
    print "Create channels."
    csma = ns.csma.CsmaHelper()
    csma.SetChannelAttribute("DataRate", ns.core.StringValue(str(framework.param('bandwidth'))))
    csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds({{delay}})))
    csma.SetDeviceAttribute("Mtu", ns.core.UintegerValue(1400))
    d = csma.Install(n)
    
    print "Assign IP Addresses."
    ipv4 = ns.internet.Ipv4AddressHelper()
    ipv4.SetBase (ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
    i = ipv4.Assign(d)
    serverAddress = ns.network.Address(i.GetAddress(1))
    
    print "Create Applications."
    port = 9
    server = ns.applications.UdpEchoServerHelper(port)
    serverapps = server.Install(n.Get(1))
    serverapps.Start(ns.core.Seconds(1.0))
    serverapps.Stop(ns.core.Seconds(10.0))
    
    interPacketInterval = ns.core.Seconds({{interval}})
    
    client = ns.applications.UdpEchoClientHelper(serverAddress, port)
    client.SetAttribute("MaxPackets", ns.core.UintegerValue({{maxPacketCount}}))
    client.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval))
    client.SetAttribute("PacketSize", ns.core.UintegerValue({{packetSize}}))
    
    apps = client.Install(n.Get(0))
    apps.Start(ns.core.Seconds(2.0))
    apps.Stop(ns.core.Seconds(10.0))
    
    client.SetFill (apps.Get (0), "Hello World")
    client.SetFill (apps.Get (0), 0xa5, 1024)
    
    asciitracer = ns.network.AsciiTraceHelper()
    csma.EnableAsciiAll(asciitracer.CreateFileStream("udp-echo-py.tr"))
    csma.EnablePcapAll("udp-echo-py", False)
    
    print "Run Simulation."
    anim = ns.animation.AnimationInterface("animation.xml")
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()
    print "Done."
    
    framework.stop()