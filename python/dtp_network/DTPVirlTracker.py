# -*- mode: python; python-indent: 4 -*-
import ncs
# from ncs.application import Service
from ncs.dp import Action
# from ncs.maapi import Maapi
# import sys
# from nso_device_management import NSODeviceManagement
# import importlib
# import _ncs.dp as DP

# class VirlTopologyTracker():
    # @Action.action
    # def cb_action(self, uinfo, name, kp, input, output):
    #     self.log.info("VirlTopologyTracker Start ")
    #     output.result = "SUCCESS!!"

    # def create_virl_tracker_kicker(self, root, network, topology, node):
    #     kicker = root.kickers.data_kicker.create(topology.name+"-"+node.name)
    #     kicker.monitor = "/dtp/network[name='{network_name}']/node[name='{node_name}']".format(network_name=network.name,node_name=node.name)
    #     kicker.trigger_expr = "state = 'Undeploying' or state = 'Deploying'"
    #     kicker.kick_node = "/dtp/network/topology[name='{topo_name}']".format(topo_name=topology.name)
    #     kicker.action_name = "Track-Virl-Topology-Deployment"



class Main(ncs.application.Application):
    def setup(self):
        # self.register_action('VirlTopologyTracker', VirlTopologyTracker)
        # with ncs.maapi.Maapi() as m:
        #     with ncs.maapi.Session(m, 'admin', 'system'):
        #         with m.start_write_trans() as t:
        #             root = ncs.maagic.get_root(t)
        #             topology = root.devices.device[virl_server].live_status.simulations.simulation[simulation_name].topology
        #             self.copy_topology(root, topology, topology_name)
        #             t.apply()

        self.log.info('VirlTopologyTracker Application RUNNING')


    def teardown(self):
        self.log.info('VirlTopologyTracker FINISHED')
