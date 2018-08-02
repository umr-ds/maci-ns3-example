### ENV int mean_bw "The mean bandwidth at the bottleneck"
### ENV int delay "The delay per link"

import ns.core as ns3
import framework

def main(argv):

    framework.start()

    cmd = ns3.CommandLine()
    cmd.Parse (argv)

    # Configuration.

    # Build nodes
    term_0 = ns3.NodeContainer()
    term_0.Create (1)
    term_1 = ns3.NodeContainer()
    term_1.Create (1)
    bridge_0 = ns3.NodeContainer()
    bridge_0.Create (1)
    bridge_1 = ns3.NodeContainer()
    bridge_1.Create (1)

    # Build link.
    csma_bridge_0 = ns3.CsmaHelper();
    csma_bridge_0.SetChannelAttribute("DataRate", ns3.DataRateValue (ns3.DataRate(100000000)))
    csma_bridge_0.SetChannelAttribute("Delay",  ns3.TimeValue (ns3.MilliSeconds({{delay}})))
    csma_bridge_1 = ns3.CsmaHelper();
    csma_bridge_1.SetChannelAttribute("DataRate", ns3.DataRateValue (ns3.DataRate(100000000)))
    csma_bridge_1.SetChannelAttribute("Delay",  ns3.TimeValue (ns3.MilliSeconds({{delay}})))
    csma_hub_0 = ns3.CsmaHelper()
    csma_hub_0.SetChannelAttribute("DataRate", ns3.DataRateValue(ns3.DataRate({{mean_bw}})))
    csma_hub_0.SetChannelAttribute("Delay",  ns3.TimeValue(ns3.MilliSeconds({{delay}})))

    # Build link net device container.
    all_bridge_0 = ns3.NodeContainer()
    all_bridge_0.Add (term_0)
    terminalDevices_bridge_0 = ns3.NetDeviceContainer()
    BridgeDevices_bridge_0 = ns3.NetDeviceContainer()
    for i in range(1):
        link = csma_bridge_0.Install(NodeContainer(all_bridge_0.Get(i), bridge_0))
        terminalDevices_bridge_0.Add(link.Get(0))
        BridgeDevices_bridge_0.Add(link.Get(1))
    bridge_bridge_0 = ns3.BridgeHelper
    bridge_bridge_0.Install(bridge_0.Get(0), BridgeDevices_bridge_0)
    ndc_bridge_0 = terminalDevices_bridge_0
    all_bridge_1 = ns3.NodeContainer()
    all_bridge_1.Add (term_1)
    terminalDevices_bridge_1 = ns3.NetDeviceContainer()
    BridgeDevices_bridge_1 = ns3.NetDeviceContainer()
    for i in range(1):
        link = csma_bridge_1.Install(NodeContainer(all_bridge_1.Get(i), bridge_1))
        terminalDevices_bridge_1.Add(link.Get(0))
        BridgeDevices_bridge_1.Add(link.Get(1))
    bridge_bridge_1 = ns3.BridgeHelper
    bridge_bridge_1.Install(bridge_1.Get(0), BridgeDevices_bridge_1)
    ndc_bridge_1 = terminalDevices_bridge_1
    all_hub_0 = ns3.NodeContainer()
    all_hub_0.Add (bridge_0)
    all_hub_0.Add (bridge_1)
    ndc_hub_0 = csma_hub_0.Install(all_hub_0)

    # Install the IP stack.
    internetStackH = ns3.InternetStackHelper()
    internetStackH.Install (term_0)
    internetStackH.Install (term_1)

    # IP assign.
    ipv4 = ns3.Ipv4AddressHelper()
    ipv4.SetBase (ns3.Ipv4Address("10.0.0.0"), ns3.Ipv4Mask("255.255.255.0"))
    iface_ndc_bridge_0 = ipv4.Assign (ndc_bridge_0)
    ipv4.SetBase (ns3.Ipv4Address("10.0.1.0"), ns3.Ipv4Mask("255.255.255.0"))
    iface_ndc_bridge_1 = ipv4.Assign (ndc_bridge_1)
    ipv4.SetBase (ns3.Ipv4Address("10.0.2.0"), ns3.Ipv4Mask("255.255.255.0"))
    iface_ndc_hub_0 = ipv4.Assign (ndc_hub_0)

    # Generate Route.
    ns3.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    # Generate Application.
    port_tcp_0 = 5500
    sinkLocalAddress_tcp_0 = ns3.Address(ns3.InetSocketAddress(ns3.Ipv4Address.GetAny(), port_tcp_0))
    sinkHelper_tcp_0 = ns3.PacketSinkHelper("ns3::TcpSocketFactory", sinkLocalAddress_tcp_0)
    sinkApp_tcp_0 = sinkHelper_tcp_0.Install(term_1)
    sinkApp_tcp_0.Start(ns3.Seconds(1.0))
    sinkApp_tcp_0.Stop(ns3.Seconds(10.0))
    clientHelper_tcp_0 = ns3.OnOffHelper("ns3::TcpSocketFactory", ns3.Address())
    clientHelper_tcp_0.SetAttribute("OnTime", ns3.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    clientHelper_tcp_0.SetAttribute("OffTime", ns3.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
    clientApps_tcp_0 = ns3.ApplicationContainer()
    remoteAddress_tcp_0 = ns3.AddressValue(ns3.InetSocketAddress(iface_ndc_bridge_1.GetAddress(0), port_tcp_0))
    clientHelper_tcp_0.SetAttribute("Remote", remoteAddress_tcp_0)
    clientApps_tcp_0.Add(clientHelper_tcp_0.Install(term_0))
    clientApps_tcp_0.Start(ns3.Seconds(1.0))
    clientApps_tcp_0.Stop(ns3.Seconds(10.0))

    # Simulation.
    # Pcap output.
    # Stop the simulation after x seconds.
    stopTime = 11
    ns3.Simulator.Stop (ns3.Seconds(stopTime))
    # Start and clean simulation.
    ns3.Simulator.Run()
    ns3.Simulator.Destroy()

    framework.stop()

if __name__ == '__main__':
    import sys
    main(sys.argv)