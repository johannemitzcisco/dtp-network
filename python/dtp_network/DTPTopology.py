# -*- mode: python; python-indent: 4 -*-
import ncs
# from ncs.application import Service
from ncs.dp import Action
# from ncs.maapi import Maapi
# import sys
# from nso_device_management import NSODeviceManagement
# import importlib
# import _ncs.dp as DP

# class RegisterVirlTracker(ncs.application.NanoService):
#     @ncs.application.NanoService.create
#     def cb_nano_create(self, tctx, root, service, component, state, proplist):
#         currstate = service.plan.component[component].state[state]
#         network = service._parent._parent
#         dtp = network._parent._parent
#         topology = service
#         self.log.info(state, " (CREATE): ", component, ":", state, ":", currstate.status, ":", topology.name)
#         self.log.info(state, " (CREATE): ", proplist)
#         for node in (node for node in topology.node 
#             if network.deployment_target[network.node[node.name].deployment_target].name == "VIRL"):
#             self.log.info(state, " (CREATE): ", network.deployment_target[network.node[node.name].deployment_target].type)
#             self.create_virl_tracker_kicker(root, network, topology, node)
#             network.node[node.name].state = "Deploying"

#     @ncs.application.NanoService.delete
#     def cb_nano_delete(self, tctx, root, service, component, state, proplist):
#         currstate = service.plan.component[component].state[state]
#         self.log.info("deploy-virl-topology(DELETE) ", component, " ", state, " ", currstate.status)
#         self.log.info("deploy-virl-topology(DELETE) ", proplist)

#     def create_virl_tracker_kicker(self, root, network, topology, node):
#         kicker = root.kickers.data_kicker.create(topology.name+"-"+node.name)
#         kicker.monitor = "/dtp/network[name='{network_name}']/node[name='{node_name}']".format(network_name=network.name,node_name=node.name)
#         kicker.trigger_expr = "state = 'Undeploying' or state = 'Deploying'"
#         kicker.kick_node = "/dtp/network/topology[name='{topo_name}']".format(topo_name=topology.name)
#         kicker.action_name = "Track-Virl-Topology-Deployment"

class NSODevicesRegistration(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        readystate = service.plan.component[component].state['ready']
        topology = service
        network = service._parent._parent
        dtp = network._parent._parent
        self.log.info("Num Kickers: ", len(root.kickers.data_kicker)-1)
        for dk in root.kickers.data_kicker:
            if dk.id != 'ncs-internal-side-effects':
                self.log.info("DK ID: ",dk.id)
        self.log.info(state, " (CREATE): ", component, ":", state, ":", currstate.status, ":", readystate.status) #, ":", node.name, ":", node.state)
        for n in topology.node:
            node = network.node[n.name]
            template = ncs.template.Template(dtp)
            vars = ncs.template.Variables()
            vars.add('NODE-NAME', node.name)
            vars.add('NETWORK-NAME', network.name)
            self.log.info(state, " (CREATE): ", node.name, " Applying Template: ", dtp.node_type[node.node_type].nso_device.template)
            template.apply(dtp.node_type[node.node_type].nso_device.template, vars)
            node.state = "Registered"
        return proplist

class CheckNodeConnectivity(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        readystate = service.plan.component[component].state['ready']
        network = service._parent._parent
        dtp = network._parent._parent
        topology = service
        self.log.info("Num Kickers: ", len(root.kickers.data_kicker)-1)
        for dk in root.kickers.data_kicker:
            if dk.id != 'ncs-internal-side-effects':
                self.log.info("DK ID: ",dk.id)
        self.log.info(state, " (CREATE): ", component, ":", state, ":", currstate.status, ":", readystate.status) #, ":", node.name, ":", node.state)
        for n in topology.node:
            node = network.node[n.name]
            output = root.devices.device[node.nso_device.name].connect()
            self.log.info(state, " (CREATE): Connect Result ", node.name, ": " , output.result)
            if output.result:
                node.state = "Ready"
                self.log.info('NEW STATE: %s' % (node.state))

class DeployVirlTopology(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        network = service._parent._parent
        dtp = network._parent._parent
        topology = service
        self.log.info("deploy-virl-topology(CREATE) ", component, ":", state, ":", currstate.status, ":", network.name)
        self.log.info("deploy-virl-topology(CREATE) proplist: ", proplist)
        # propdict = dict(proplist)
        # self.log.info("deploy-virl-topology(CREATE) propdict: ", propdict)
        template = ncs.template.Template(dtp)
        vars = ncs.template.Variables()
        vars.add('NETWORK-NAME', network.name)
        vars.add('TOPOLOGY-NAME', topology.name)
        sim_name = network.name+'-'+topology.name
        for topo_node in (node for node in topology.node 
         if network.deployment_target[network.node[node.name].deployment_target].type.type == "Virl"):
            node = network.node[topo_node.name]
            self.log.info("deploy-virl-topology(CREATE) Node: ", node.name, " is a VIRL Node")
            vars.add('NODE-NAME', node.name)
            vars.add('NODE-TYPE', dtp.node_type[node.node_type].virl_device.type)
            self.log.info("deploy-virl-topology(CREATE) NODE-TYPE: ", dtp.node_type[node.node_type].virl_device.type)
            vars.add('NODE-SUBTYPE', dtp.node_type[node.node_type].virl_device.subtype)
            self.log.info("deploy-virl-topology(CREATE) NODE-SUBTYPE: ", dtp.node_type[node.node_type].virl_device.subtype)
            vars.add('VIRL-DEVICE-NAME', network.deployment_target[node.deployment_target].type.Virl.virl_server)
            vars.add('SIMULATION-NAME', sim_name)
            self.log.info("deploy-virl-topology(CREATE) VIRL-DEVICE-NAME: ", network.deployment_target[node.deployment_target].type.Virl.virl_server)
            self.log.info("deploy-virl-topology(CREATE) Device State: ", node.state, ' ',
                node.state.value)
            template.apply(network.deployment_target[node.deployment_target].type.Virl.template, vars)
            template.apply(dtp.node_type[node.node_type].virl_device.template, vars)
            virl_server_name = network.deployment_target[node.deployment_target].type.Virl.virl_server
            virl_server = root.devices.device[virl_server_name]
            network.node[node.name].state = "Deploying"
            if sim_name in virl_server.live_status.simulations.simulation:
                sim_node_count = len(virl_server.live_status.simulations.simulation[sim_name].topology.node)
                topology_node_count = sum(1 for node in topology.node 
                                          if network.deployment_target[network.node[node.name].deployment_target].type.type == "Virl")
                self.log.info("deploy-virl-topology(CREATE) Sim Node Count: ", sim_node_count, " Topology Node Count: ", topology_node_count)
                if sim_node_count == topology_node_count:
                    network.node[node.name].state = "Deployed"
            self.log.info("deploy-virl-topology(CREATE) Node state: ", network.node[node.name].state)
        topology.virl_simulation_status.simulation_name = sim_name
        topology.virl_simulation_status.state = "Deployed"
        for topo_node in (node for node in topology.node 
         if network.deployment_target[network.node[node.name].deployment_target].type.type == "Virl"):
            node = network.node[topo_node.name]
            if node.state.value < 5:
                topology.virl_simulation_status.state = "Deploying"

    @ncs.application.NanoService.delete
    def cb_nano_delete(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        self.log.info("deploy-virl-topology(DELETE) ", component, " ", state, " ", currstate.status)
        self.log.info("deploy-virl-topology(DELETE) ", proplist)
        currstate.status = 'not-reached'
        self.log.info("deploy-virl-topology(DELETE) ", currstate.status)
        return proplist


class UpdateNodeState(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        state = input.state
        self.log.info('ACTION NAME: %s' % name)
        self.log.info('KEYPATH: %s' % (kp))
        output.result = "FAILED"
        with ncs.maapi.Maapi() as m:
            with ncs.maapi.Session(m, uinfo.username, uinfo.context):
                with m.start_write_trans() as t:
                    node = ncs.maagic.get_node(t, kp)
                    self.log.info('OLD STATE: %s' % (node.state))
                    self.log.info('NEW STATE: %s' % (state))
                    node.state = state
                    t.apply()
                    output.result = "Success"

class UpdateVirlTopologyState(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        state = input.state
        self.log.info('ACTION NAME: %s' % name)
        self.log.info('KEYPATH: %s' % (kp))
        output.result = "FAILED"
        with ncs.maapi.Maapi() as m:
            with ncs.maapi.Session(m, uinfo.username, uinfo.context):
                with m.start_write_trans() as t:
                    topology = ncs.maagic.get_node(t, kp)
                    self.log.info('OLD STATE: %s' % (topology.virl_simulation_status.state))
                    self.log.info('NEW STATE: %s' % (state))
                    topology.virl_simulation_status.state = state
                    t.apply()
                    output.result = "Success"

class CheckNodeConnectivityAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('ACTION NAME: %s' % name)
        self.log.info('KEYPATH: %s' % (kp))
        output.result = "FAILED"
        with ncs.maapi.Maapi() as m:
            with ncs.maapi.Session(m, uinfo.username, uinfo.context):
                with m.start_write_trans() as t:
                    node = ncs.maagic.get_node(t, kp)
                    device = ncs.maagic.get_node(t, "/devices/device{%s}" % node.nso_device.name)
                    self.log.info('OLD STATE: %s' % (node.state))
                    if device.connect():
                        node.state = "Ready"
                        self.log.info('NEW STATE: %s' % (node.state))
                        t.apply()
        output.result = "SUCCESS"

class ApplyTopologyConfigurations(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        topology = service
        network = topology._parent._parent
        dtp_node = network._parent._parent
        self.log.info("DTP Node: ", dtp_node._path)
        self.log.info("Network Node: ", network._path)
        self.log.info("Topology Node: ", topology._path)
        template = ncs.template.Template(dtp_node)
        vars = ncs.template.Variables()
        for foname in topology.function_objects: # This gets the list of different policy types defined
            self.log.info('Function Object Name: ', foname)
            folist = ncs.maagic.cd(topology.function_objects,foname)
            for foentryname in folist: # This get each list entry in the policy type
                self.log.info('foentryname: ', foentryname)
                foentrynode = ncs.maagic.cd(folist,foentryname)
                vars.add('FO-NAME', foentrynode.function_object_name)
                fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:topology/'+str(foname)+'{"'+foentrynode.function_object_name+'"}/template'
                self.log.info('Func. Object Template Location: ', fonodetemplatestr)
                fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                for node in topology.node:
                    vars.add('SERVICE-NAME', topology._parent._parent.name)
                    vars.add('TOPOLOGY-NAME', topology.name)
                    vars.add('NODE-NAME', node.name)
                    vars.add('DEVICE-NAME', network.node[node.name].nso_device.name)
                    vars.add('TEMPLATE-CONTEXT', "/network[name="+topology._parent._parent.name+"]/topology[name="+topology.name+"]/node[name="+node.name+"]/function-objects/banner[function-object-name="+foentrynode.function_object_name+"]")
                    self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
                    self.log.info('TOPOLOGY-NAME: ', topology.name)
                    self.log.info('NODE-NAME: ', node.name)
                    self.log.info('DEVICE-NAME: ', network.node[node.name].nso_device.name)
                    self.log.info('TEMPLATE-CONTEXT: ', "/network[name="+topology._parent._parent.name+"]/topology[name="+topology.name+"]/node[name="+node.name+"]/function-objects/banner[function-object-name="+foentrynode.function_object_name+"]")
                    self.log.info('APPLY TEMPLATE: Node: ', node.name, ' Template: ', fo_template_name)
#                    template = ncs.template.Template(service, network._path)
                    template.apply(fo_template_name, vars)

class ApplyNodeConfigurations(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        topology = service
        network = topology._parent._parent
        dtp_node = network._parent._parent
        self.log.info("DTP Node: ", dtp_node._path)
        self.log.info("Network Node: ", network._path)
        self.log.info("Topology Node: ", topology._path)
        template = ncs.template.Template(dtp_node)
        vars = ncs.template.Variables()
        for node in topology.node:
            self.log.info('Topology Node: ', node.name)
            if network.node[node.name].nso_device.name not in root.devices.device:  # If the node does not exist in NSO then we can't configure it
                self.log.info('Node not registered in NSO database')
                continue
            vars = ncs.template.Variables()
            vars.add('SERVICE-NAME', topology._parent._parent.name)
            vars.add('TOPOLOGY-NAME', topology.name)
            vars.add('NODE-NAME', node.name)
            vars.add('DEVICE-NAME', network.node[node.name].nso_device.name)
            self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
            self.log.info('TOPOLOGY-NAME:', topology.name)
            self.log.info('NODE-NAME: ', node.name)
            self.log.info('DEVICE-NAME: ', network.node[node.name].nso_device.name)
            for foname in node.function_objects: # This gets the list of different policy types defined
                self.log.info('foname: ', foname)
                folist = ncs.maagic.cd(node.function_objects,foname)
                for foentryname in folist: # This get each list entry in the policy type
                    self.log.info('foentryname: ', foentryname)
                    foentrynode = ncs.maagic.cd(folist,foentryname)
                    vars.add('FO-NAME', foentrynode.function_object_name)
                    self.log.info('FO-NAME: ', foentrynode.function_object_name)
                    fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:node/'+str(foname)+'{"'+str(foentrynode.function_object_name)+'"}/template'
                    self.log.info('Func. Object Template Location: ', fonodetemplatestr)
                    fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                    self.log.info('APPLY TEMPLATE: Node: ', node.name, ' Template: ', fo_template_name)
                    if fo_template_name is not None:
                        template.apply(fo_template_name, vars)



class ApplyLinkConfigurations(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        topology = service
        network = topology._parent._parent
        dtp_node = network._parent._parent
        self.log.info("DTP Node: ", dtp_node._path)
        self.log.info("Network Node: ", network._path)
        self.log.info("Topology Node: ", topology._path)
        template = ncs.template.Template(dtp_node)
        vars = ncs.template.Variables()
        for link in topology.link:
            link_name = link.name
            self.log.info('Link: ', link_name, ' Path: ', link._path)
            for side in link.side:
                self.log.info('SIDE: ', side.name)
                self.log.info('NODE-NAME: ', side.node)
                vars = ncs.template.Variables()
                vars.add('SERVICE-NAME', topology._parent._parent.name)
                vars.add('TOPOLOGY-NAME', topology.name)
                vars.add('DEVICE-NAME', topology.node[side.node].nso_device.name)
                vars.add('LINK-NAME', link_name)
                vars.add('NODE-NAME', side.node)
                self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
                self.log.info('TOPOLOGY-NAME:', topology.name)
                self.log.info('LINK-NAME: ', link_name)
                self.log.info('NODE-NAME: ', side.node)
                self.log.info('DEVICE-NAME: ', topology.node[side.node].nso_device.name)
                for foname in link.function_objects: # This gets the list of different policy types defined
                    self.log.info('foname: ', foname)
                    folist = ncs.maagic.cd(side.function_objects,foname)
                    for foentryname in folist: # This get each list entry in the policy type
                        self.log.info('foentryname: ', foentryname)
                        foentrynode = ncs.maagic.cd(folist,foentryname)
                        vars.add('FO-NAME', foentrynode.function_object_name)
                        self.log.info('FO-NAME: ', foentrynode.function_object_name)
                        fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:link/'+str(foname)+'{"'+str(foentrynode.function_object_name)+'"}/template'
                        self.log.info('Func. Object Template Location: ', fonodetemplatestr)
                        fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                        self.log.info('APPLY TEMPLATE: ', fo_template_name)
                        if fo_template_name is not None:
                            template.apply(fo_template_name, vars)


class ApplyLinkSideConfigurations(ncs.application.NanoService):
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        topology = service
        network = topology._parent._parent
        dtp_node = network._parent._parent
        self.log.info("DTP Node: ", dtp_node._path)
        self.log.info("Network Node: ", network._path)
        self.log.info("Topology Node: ", topology._path)
        template = ncs.template.Template(dtp_node)
        vars = ncs.template.Variables()
        for link in topology.link:
            link_name = link.name
            self.log.info('Link: ', link_name, ' Path: ', link._path)
            for side in link.side:
                self.log.info('SIDE: ', side.name)
                self.log.info('NODE-NAME: ', side.node)
                vars = ncs.template.Variables()
                vars.add('SERVICE-NAME', topology._parent._parent.name)
                vars.add('TOPOLOGY-NAME', topology.name)
                vars.add('DEVICE-NAME', topology.node[side.node].nso_device.name)
                vars.add('LINK-NAME', link_name)
                vars.add('NODE-NAME', side.node)
                self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
                self.log.info('TOPOLOGY-NAME:', topology.name)
                self.log.info('LINK-NAME: ', link_name)
                self.log.info('NODE-NAME: ', side.node)
                self.log.info('DEVICE-NAME: ', topology.node[side.node].nso_device.name)
                for foname in side.function_objects: # This gets the list of different policy types defined
                    self.log.info('foname: ', foname)
                    folist = ncs.maagic.cd(side.function_objects,foname)
                    for foentryname in folist: # This get each list entry in the policy type
                        self.log.info('foentryname: ', foentryname)
                        foentrynode = ncs.maagic.cd(folist,foentryname)
                        vars.add('FO-NAME', foentrynode.function_object_name)
                        self.log.info('FO-NAME: ', foentrynode.function_object_name)
                        fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:link/'+str(foname)+'{"'+str(foentrynode.function_object_name)+'"}/template'
                        self.log.info('Func. Object Template Location: ', fonodetemplatestr)
                        fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                        self.log.info('APPLY TEMPLATE: ', fo_template_name)
                        if fo_template_name is not None:
                            template.apply(fo_template_name, vars)

class Main(ncs.application.Application):
    def setup(self):
        self.register_action('update-node-state-action', UpdateNodeState)
        self.register_action('update-topology-virl-state-action', UpdateVirlTopologyState)
        self.register_action('check-node-connectivity-action', CheckNodeConnectivityAction)

        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:register-nodes',
                                    'dtpn:register-nodes-with-NSO',
                                    NSODevicesRegistration)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:deploy-virl-nodes',
                                    'dtpn:deploy-virl-topology',
                                    DeployVirlTopology)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:node-connectivity',
                                    'dtpn:check-connectivity',
                                    CheckNodeConnectivity)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:apply-configuration',
                                    'dtpn:topology-function-objects',
                                    ApplyTopologyConfigurations)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:apply-configuration',
                                    'dtpn:node-function-objects',
                                    ApplyNodeConfigurations)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:apply-configuration',
                                    'dtpn:link-function-objects',
                                    ApplyLinkConfigurations)
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:apply-configuration',
                                    'dtpn:link_side-function-objects',
                                    ApplyLinkSideConfigurations)

        self.log.info('DTPTopology Nano Service RUNNING')

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('DTPTopology Nano Service FINISHED')
