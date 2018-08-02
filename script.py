import sys

import framwork

import ns.applications
import ns.core
import ns.internet
import ns.mobility
import ns.network
import ns.point_to_point
import ns.wifi

def SetPosition(node, position):
    mobility = node.GetObject(ns.mobility.MobilityModel.GetTypeId())
    mobility.SetPosition(position)


def GetPosition(node):
    mobility = node.GetObject(ns.mobility.MobilityModel.GetTypeId())
    return mobility.GetPosition()

def AdvancePosition(node):
    pos = GetPosition(node);
    pos.x += 5.0
    if pos.x >= 210.0:
      return
    SetPosition(node, pos)
    ns.core.Simulator.Schedule(ns.core.Seconds(1.0), AdvancePosition, node)


def main(argv):
    framework.start()
    ns.core.CommandLine().Parse(argv)

    ns.network.Packet.EnablePrinting();

    # enable rts cts all the time.
    ns.core.Config.SetDefault("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue("0"))
    # disable fragmentation
    ns.core.Config.SetDefault("ns3::WifiRemoteStationManager::FragmentationThreshold", ns.core.StringValue("2200"))

    wifi = ns.wifi.WifiHelper()
    mobility = ns.mobility.MobilityHelper()
    stas = ns.network.NodeContainer()
    ap = ns.network.NodeContainer()
    #NetDeviceContainer staDevs;
    packetSocket = ns.network.PacketSocketHelper()

    stas.Create(2)
    ap.Create(1)

    # give packet socket powers to nodes.
    packetSocket.Install(stas)
    packetSocket.Install(ap)

    wifiPhy = ns.wifi.YansWifiPhyHelper.Default()
    wifiChannel = ns.wifi.YansWifiChannelHelper.Default()
    wifiPhy.SetChannel(wifiChannel.Create())

    ssid = ns.wifi.Ssid("wifi-default")
    wifi.SetRemoteStationManager("ns3::ArfWifiManager")
    wifiMac = ns.wifi.WifiMacHelper()

    # setup stas.
    wifiMac.SetType("ns3::StaWifiMac",
                    "Ssid", ns.wifi.SsidValue(ssid))
    staDevs = wifi.Install(wifiPhy, wifiMac, stas)
    # setup ap.
    wifiMac.SetType("ns3::ApWifiMac",
                    "Ssid", ns.wifi.SsidValue(ssid),
                    "BeaconInterval", ns.core.TimeValue(ns.core.Seconds(2.5)))
    wifi.Install(wifiPhy, wifiMac, ap)

    # mobility.
    mobility.Install(stas)
    mobility.Install(ap)

    ns.core.Simulator.Schedule(ns.core.Seconds(1.0), AdvancePosition, ap.Get(0))

    socket = ns.network.PacketSocketAddress()
    socket.SetSingleDevice(staDevs.Get(0).GetIfIndex())
    socket.SetPhysicalAddress(staDevs.Get(1).GetAddress())
    socket.SetProtocol(1)

    onoff = ns.applications.OnOffHelper("ns3::PacketSocketFactory", ns.network.Address(socket))
    onoff.SetConstantRate (ns.network.DataRate ("500kb/s"))

    apps = onoff.Install(ns.network.NodeContainer(stas.Get(0)))
    apps.Start(ns.core.Seconds(0.5))
    apps.Stop(ns.core.Seconds(43.0))

    ns.core.Simulator.Stop(ns.core.Seconds(44.0))

    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()
    
    framework.stop()


if __name__ == '__main__':
    sys.exit(main(sys.argv))