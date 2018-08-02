### ENV int mean_bw "The mean bandwidth at the bottleneck"
### ENV int delay "The delay per link"

import ns.core
import ns.network
import ns.csma
import ns.internet
import framework

def main(argv):

    framework.start()

    cmd = ns.core.CommandLine()
    cmd.Parse (argv)

    # Configuration.

    # Build nodes
    term_0 = ns.network.NodeContainer()
    term_0.Create (1)
    term_1 = ns.network.NodeContainer()
    term_1.Create (1)
    bridge_0 = ns.network.NodeContainer()
    bridge_0.Create (1)
    bridge_1 = ns.network.NodeContainer()
    bridge_1.Create (1)

    # Build link.
    csma_bridge_0 = ns.csma.CsmaHelper();
    csma_bridge_0.SetChannelAttribute("DataRate", ns.network.DataRateValue (ns.network.DataRate(100000000)))
    csma_bridge_0.SetChannelAttribute("Delay",  ns.core.TimeValue (ns.core.MilliSeconds({{delay}})))
    csma_bridge_1 = ns.csma.CsmaHelper();
    csma_bridge_1.SetChannelAttribute("DataRate", ns.network.DataRateValue (ns.network.DataRate(100000000)))
    csma_bridge_1.SetChannelAttribute("Delay",  ns.core.TimeValue (ns.core.MilliSeconds({{delay}})))
    csma_hub_0 = ns.csma.CsmaHelper()
    csma_hub_0.SetChannelAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate({{mean_bw}})))
    csma_hub_0.SetChannelAttribute("Delay",  ns.core.TimeValue(ns.core.MilliSeconds({{delay}})))

    # Build link net device container.
    all_bridge_0 = ns.network.NodeContainer()
    all_bridge_0.Add (term_0)
    terminalDevices_bridge_0 = ns.network.NetDeviceContainer()
    BridgeDevices_bridge_0 = ns.network.NetDeviceContainer()
    for i in range(1):
        link = csma_bridge_0.Install(ns.network.NodeContainer(all_bridge_0.Get(i), bridge_0))
        terminalDevices_bridge_0.Add(link.Get(0))
        BridgeDevices_bridge_0.Add(link.Get(1))
    bridge_bridge_0 = ns.network.BridgeHelper
    bridge_bridge_0.Install(bridge_0.Get(0), BridgeDevices_bridge_0)
    ndc_bridge_0 = terminalDevices_bridge_0
    all_bridge_1 = ns.network.NodeContainer()
    all_bridge_1.Add (term_1)
    terminalDevices_bridge_1 = ns.network.NetDeviceContainer()
    BridgeDevices_bridge_1 = ns.network.NetDeviceContainer()
    for i in range(1):
        link = csma_bridge_1.Install(ns.network.NodeContainer(all_bridge_1.Get(i), bridge_1))
        terminalDevices_bridge_1.Add(link.Get(0))
        BridgeDevices_bridge_1.Add(link.Get(1))
    bridge_bridge_1 = ns.network.BridgeHelper
    bridge_bridge_1.Install(bridge_1.Get(0), BridgeDevices_bridge_1)
    ndc_bridge_1 = terminalDevices_bridge_1
    all_hub_0 = ns.network.NodeContainer()
    all_hub_0.Add (bridge_0)
    all_hub_0.Add (bridge_1)
    ndc_hub_0 = csma_hub_0.Install(all_hub_0)

    # Install the IP stack.
    internetStackH = ns.internet.InternetStackHelper()
    internetStackH.Install (term_0)
    internetStackH.Install (term_1)

    # IP assign.
    ipv4 = ns.internet.Ipv4AddressHelper()
    ipv4.SetBase (ns.network.Ipv4Address("10.0.0.0"), ns.network.Ipv4Mask("255.255.255.0"))
    iface_ndc_bridge_0 = ipv4.Assign (ndc_bridge_0)
    ipv4.SetBase (ns.network.Ipv4Address("10.0.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
    iface_ndc_bridge_1 = ipv4.Assign (ndc_bridge_1)
    ipv4.SetBase (ns.network.Ipv4Address("10.0.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
    iface_ndc_hub_0 = ipv4.Assign (ndc_hub_0)

    # Generate Route.
    ns.network.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    # Generate Application.
    port_tcp_0 = 5500
    sinkLocalAddress_tcp_0 = ns.network.Address(ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), port_tcp_0))
    sinkHelper_tcp_0 = ns.network.PacketSinkHelper("ns3::TcpSocketFactory", sinkLocalAddress_tcp_0)
    sinkApp_tcp_0 = sinkHelper_tcp_0.Install(term_1)
    sinkApp_tcp_0.Start(ns.core.Seconds(1.0))
    sinkApp_tcp_0.Stop(ns.core.Seconds(10.0))
    clientHelper_tcp_0 = ns.network.OnOffHelper("ns3::TcpSocketFactory", ns.network.Address())
    clientHelper_tcp_0.SetAttribute("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    clientHelper_tcp_0.SetAttribute("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    clientApps_tcp_0 = ns.network.ApplicationContainer()
    remoteAddress_tcp_0 = ns.network.AddressValue(ns.network.InetSocketAddress(iface_ndc_bridge_1.GetAddress(0), port_tcp_0))
    clientHelper_tcp_0.SetAttribute("Remote", remoteAddress_tcp_0)
    clientApps_tcp_0.Add(clientHelper_tcp_0.Install(term_0))
    clientApps_tcp_0.Start(ns.core.Seconds(1.0))
    clientApps_tcp_0.Stop(ns.core.Seconds(10.0))

    # Simulation.
    # Pcap output.
    # Stop the simulation after x seconds.
    stopTime = 11
    ns.core.Simulator.Stop (ns.core.Seconds(stopTime))
    # Start and clean simulation.
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()

    framework.stop()

if __name__ == '__main__':
    import sys
    main(sys.argv)