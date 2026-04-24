from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ipv4

log = core.getLogger()

packet_count = 0
protocol_stats = {"ICMP": 0, "TCP": 0, "UDP": 0, "OTHER": 0}

def _handle_PacketIn(event):
    global packet_count
    packet_count += 1

    packet = event.parsed
    if not packet.parsed:
        return

    ip_packet = packet.find(ipv4)
    pkt_type = "OTHER"

    if ip_packet:
        if ip_packet.protocol == 1:
            protocol_stats["ICMP"] += 1
            pkt_type = "ICMP"
        elif ip_packet.protocol == 6:
            protocol_stats["TCP"] += 1
            pkt_type = "TCP"
        elif ip_packet.protocol == 17:
            protocol_stats["UDP"] += 1
            pkt_type = "UDP"
        else:
            protocol_stats["OTHER"] += 1

    log.info(f"Total Packets: {packet_count}")
    log.info(f"Protocol Stats: {protocol_stats}")

    if pkt_type == "ICMP":
        log.info("Blocking ICMP packet")
        return

    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet)
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)

def launch():
    log.info("Advanced Traffic Monitoring Controller Started")
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
