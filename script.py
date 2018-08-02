### ENV float dist "Distance in meters"
### ENV float freq "Wi-Fi frequency"
### ENV int mcs "MCS" aka. DataRate
### ENV int ch_width "Channel width"
### ENV int gi "GI"

import framework

import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

# This is a simple example in order to show how to configure an IEEE 802.11n Wi-Fi network.
#
# It ouputs the UDP goodput for every VHT bitrate value, which depends on the MCS value (0 to 7), the
# channel width (20 or 40 MHz) and the guard interval (long or short). The PHY bitrate is constant over all
# the simulation run. The user can also specify the distance between the access point and the station: the
# larger the distance the smaller the goodput.
#
# The simulation assumes a single station in an infrastructure network:
#
#  STA     AP
#    *     *
#    |     |
#   n1     n2
#
# Packets in this simulation aren't marked with a QosTag so they are considered
# belonging to BestEffort Access Class (AC_BE).

def main(argv):
    framework.start()

    cmd = ns.core.CommandLine ()
    cmd.udp = "True"
    cmd.simulationTime = 10 #seconds
    cmd.distance = {{dist}}
    cmd.frequency = {{freq}}

    cmd.AddValue ("frequency", "Whether working in the 2.4 or 5.0 GHz band (other values gets rejected)")
    cmd.AddValue ("distance", "Distance in meters between the station and the access point")
    cmd.AddValue ("simulationTime", "Simulation time in seconds")
    cmd.AddValue ("udp", "UDP if set to True, TCP otherwise")
    cmd.Parse (sys.argv)

    udp = cmd.udp
    simulationTime = float(cmd.simulationTime)
    distance = float(cmd.distance)
    frequency = float(cmd.frequency)

    payloadSize = 1472

    print "MCS value" , "\t\t", "Channel width", "\t\t", "short GI","\t\t","Throughput" ,'\n'

    wifiStaNode = ns.network.NodeContainer ()
    wifiStaNode.Create (1)
    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)

    channel = ns.wifi.YansWifiChannelHelper.Default ()
    phy = ns.wifi.YansWifiPhyHelper.Default ()
    phy.SetChannel (channel.Create ())

    # Set guard interval
    phy.Set ("ShortGuardEnabled", ns.core.BooleanValue ({{gi}}))
    wifi = ns.wifi.WifiHelper.Default ()
    if frequency == 5.0:
        wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)

    elif frequency == 2.4:
        wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_2_4GHZ)
        ns.core.Config.SetDefault ("ns3::LogDistancePropagationLossModel::ReferenceLoss", ns.core.DoubleValue (40.046))

    mac = ns.wifi.HtWifiMacHelper.Default ()
    DataRate = ns.wifi.HtWifiMacHelper.DataRateForMcs ({{mcs}})
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", DataRate,
                                "ControlMode", DataRate)

    ssid = ns.wifi.Ssid ("ns3-80211n")

    mac.SetType ("ns3::StaWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid),
                "ActiveProbing", ns.core.BooleanValue (False))

    staDevice = wifi.Install (phy, mac, wifiStaNode)
    mac.SetType ("ns3::ApWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid))

    apDevice = wifi.Install (phy, mac, wifiApNode)

    # Set channel width
    ns.core.Config.Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue ({{ch_width}}))

    # mobility
    mobility = ns.mobility.MobilityHelper ()
    positionAlloc = ns.mobility.ListPositionAllocator ()

    positionAlloc.Add (ns.core.Vector3D (0.0, 0.0, 0.0))
    positionAlloc.Add (ns.core.Vector3D (distance, 0.0, 0.0))
    mobility.SetPositionAllocator (positionAlloc)

    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

    mobility.Install (wifiApNode)
    mobility.Install (wifiStaNode)

    # Internet stack
    stack = ns.internet.InternetStackHelper ()
    stack.Install (wifiApNode)
    stack.Install (wifiStaNode)

    address = ns.internet.Ipv4AddressHelper ()

    address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
    staNodeInterface = address.Assign (staDevice)
    apNodeInterface = address.Assign (apDevice)

    # Setting applications
    serverApp = ns.network.ApplicationContainer ()
    sinkApp = ns.network.ApplicationContainer ()

    # UDP flow
    myServer=ns.applications.UdpServerHelper (9)
    serverApp = myServer.Install (ns.network.NodeContainer (wifiStaNode.Get (0)))
    serverApp.Start (ns.core.Seconds (0.0))
    serverApp.Stop (ns.core.Seconds (simulationTime + 1))

    myClient = ns.applications.UdpClientHelper (staNodeInterface.GetAddress (0), 9)
    myClient.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
    myClient.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00001"))) # packets/s
    myClient.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

    clientApp = myClient.Install (ns.network.NodeContainer (wifiApNode.Get (0)))
    clientApp.Start (ns.core.Seconds (1.0))
    clientApp.Stop (ns.core.Seconds (simulationTime + 1))

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
    ns.core.Simulator.Run ()
    ns.core.Simulator.Destroy ()

    totalPacketsThrough = serverApp.Get (0).GetReceived ()
    throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0) # Mbit/s

    print i, "\t\t\t", {{ch_width}} , " MHz\t\t\t", k , "\t\t\t" , throughput , " Mbit/s"

    framework.stop()

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))