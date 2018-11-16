# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
from ncs.maapi import Maapi
import sys
# from nso_device_management import NSODeviceManagement
import importlib
import _ncs.dp as DP

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    def __init__():
        virl_nodes = {}

    def build_virl_topology(self, root, vars, template, topology_obj):
        self.log.info('topology_obj: %s' % (topology_obj._path))
        if (topology_obj._path.contains("node")):
            if network.deployment_target[network.node[node.name].deployment_target].type != 'VIRL':
                return
            self.virl_nodes[topology_obj.name] = topology_obj
            topology = node._parent.parent
            network = topology._parent._parent
            dtp = network._parent._parent._parent._parent
            vars.add('NODE-NAME', node.name)
            vars.add('INDEX', virl_nodes.len())
        elif (topology_obj._path.contains("link")):
            link = topology_obj
            topology = node._parent.parent
            network = topology._parent._parent
            dtp = network._parent._parent._parent._parent
            if (link.side[0] is not None): self.virl_nodes[link.side[0].node] = network.node[link.side[0].node]
            if (link.side[1] is not None): self.nodes[link.side[1].node] = network.node[link.side[1].node]
            if (network.deployment_target[nodes[0].deployment_target].type != 'VIRL'
                    and network.deployment_target[nodes[0].deployment_target].type != 'VIRL'):
                return
        virl_server = network.deployment_target[nodes[0].deployment_target].virl_server
        if (virl_server is None): virl_server = network.deployment_target[nodes[1].deployment_target].virl_server

        if (virl_server is None):
            self.log.info('Node %s is not marked for Virl Deployment' % (node.name))
            return
        dtp = network._parent._parent._parent._parent
        network = topology._parent._parent
        template_name = dtp.node_type[network.node[node.name].node_type].virl_device.design_template
        template.apply(template_name, vars)

    def deploy_virl(virl_server, topology):
        if (virl_server is None): raise Exception("Bad input, 'virl_server'")
        if (topology is None): raise Exception("Bad input, 'topology':")
        if (root.devices.device[virl_server].live_status.simulations.simulation.exists(topology.name)):
            raise Exception("Topology %s is already deployed, please stop on Virl Server %s" % (topology.name, virl_server))
        input = root.virl.topology[topology.name].Start_Simulation.get_input()
        input.virl_server = virl_server
        output = root.virl.topology[topology.name].Start_Simulation(input)

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ' ', service.name, ')')
        network = service._parent._parent
        dtp_node = network._parent._parent
        self.log.info("Service Node: ", service._path)
        self.log.info("Network Node: ", network._path)
        self.log.info("DTP Node: ", dtp_node._path)
        self.log.info("Root Node: ", root._path)
        self.log.info("Root: ", root.__str__)

        topology = service
        template = ncs.template.Template(dtp_node)
        vars = ncs.template.Variables()
        i = 0
        # vars.add('NETWORK-NAME', network.name)
        # vars.add('TOPOLOGY-NAME', topology.name)
        # self.log.info('======= Create Topology Devices =============')

        # for node in topology.node:
        #     self.log.info('Topology Node: ', node.name)
        #     self.build_virl_topology(root, node)
        #     vars.add('NODE-NAME', node.name)
        #     if network.deployment_target[network.node[node.name].deployment_target].type == 'VIRL':
        #         i - i + 1
        #         vars.add('INDEX', i)
        #         template_name = dtp_node.node_type[network.node[node.name].node_type].virl_device.design_template
        #         self.log.info('Virl Template Name: ', node.name)
        #         template.apply(template_name, vars)
        #         virl_server = network.deployment_target[network.node[node.name].deployment_target].virl_server
        #         self.log.info('Virl Server: %s ' % (virl_server))
        # if (virl_server is not None 
        #         and not root.devices.device[virl_server].live_status.simulations.simulation.exists(topology.name)):
        #     input = root.virl.topology[topology.name].Start_Simulation.get_input()
        #     input.virl_server = virl_server
        #     output = root.virl.topology[topology.name].Start_Simulation(input)





        # Apply topology templates
        self.log.info('======= Topology Specific Policies =============')
#        for topology in service.topology:
        # if deploynode.callback_class == 'NONE':
        #     self.log.info("Deployment type has no callback, assuming devices are registered with NSO")
        # else:
        #     deploynode = ncs.maagic.cd(topology.deployment_type, str(topology.deployment_type.deployment_type))
        #     self.log.info("Deployment Callback Class: ", deploynode.callback_class)
        #     callback_module = importlib.import_module(str(deploynode.callback_class).rsplit('.',1)[0])
        #     callback_class = getattr(callback_module, str(deploynode.callback_class).rsplit('.',1)[1])
        #     callback = callback_class()
        #     callback.create_topology(root, service, topology, self.log)
        self.log.info('Topology: ', topology.name)
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
                    if node.nso_device.name not in root.devices.device:  # If the node does not exist in NSO then we can't configure it
                        self.log.info('Node not registered in NSO database')
                        continue
                    vars.add('SERVICE-NAME', topology._parent._parent.name)
                    vars.add('TOPOLOGY-NAME', topology.name)
                    vars.add('NODE-NAME', node.name)
                    vars.add('DEVICE-NAME', node.nso_device.name)
                    vars.add('TEMPLATE-CONTEXT', "/network[name="+topology._parent._parent.name+"]/topology[name="+topology.name+"]/node[name="+node.name+"]/function-objects/banner[function-object-name="+foentrynode.function_object_name+"]")
                    self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
                    self.log.info('TOPOLOGY-NAME: ', topology.name)
                    self.log.info('NODE-NAME: ', node.name)
                    self.log.info('DEVICE-NAME: ', node.nso_device.name)
                    self.log.info('TEMPLATE-CONTEXT: ', "/network[name="+topology._parent._parent.name+"]/topology[name="+topology.name+"]/node[name="+node.name+"]/function-objects/banner[function-object-name="+foentrynode.function_object_name+"]")
                    self.log.info('APPLY TEMPLATE: Node: ', node.name, ' Template: ', fo_template_name)
#                    template = ncs.template.Template(service, network._path)
                    template.apply(fo_template_name, vars)
        self.log.info('======= Node Specific Policies =============')
        for node in topology.node:
            self.log.info('Topology Node: ', node.name)
            if network.node[node.name].nso_device.name not in root.devices.device:  # If the node does not exist in NSO then we can't configure it
                self.log.info('Node not registered in NSO database')
                continue
            vars = ncs.template.Variables()
            vars.add('SERVICE-NAME', topology._parent._parent.name)
            vars.add('TOPOLOGY-NAME', topology.name)
            vars.add('NODE-NAME', node.name)
            vars.add('DEVICE-NAME', node.nso_device.name)
            self.log.info('SERVICE-NAME: ', topology._parent._parent.name)
            self.log.info('TOPOLOGY-NAME:', topology.name)
            self.log.info('NODE-NAME: ', node.name)
            self.log.info('DEVICE-NAME: ', node.nso_device.name)
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
        self.log.info('======= Link Specific Policies =============')
        for link in topology.link:
            link_name = link.name
            self.log.info('Link: ', link_name, ' Path: ', link._path)
            # for linktype in link.type:
            #     linktypenode = ncs.maagic.cd(link.type,linktype)
            #     self.log.info('Link Type: ', linktype, ' ', type(linktypenode))
            #     try:
            #         if linktypenode is not None and not isinstance(linktypenode, ncs.maagic.Case) and linktypenode.function_object_name is not None:
            #             self.log.info('Func. Object Name: ', linktypenode.function_object_name)
            #             break
            #     except AttributeError as error:
            #         self.log.info('error: ', error)
            #         pass
            self.log.info('======= Side Specific Policies =============')
            for side in link.side:
                self.log.info('SIDE: ', side.name)
                self.log.info('NODE-NAME: ', side.node)
                if topology.node[side.node].nso_device.name not in root.devices.device: # If the node does not exist in NSO then we can't configure it
                    self.log.info(side, ' node ', side.node, 'not registered in NSO, skipping...')
                    continue
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
                # side.node_role_location = '/dtpn:network/dtpn:network-service{'+topology._parent._parent.name+'}/dtpn:topology{'+topology.name+'}/dtpn:node{'+side.node+'}/dtpn:policies/physical-node-policy-base:role'
                # self.log.info('Side Node: ', side.node, ' Location: ', side.node_role_location)
                # side.node_role = ncs.maagic.cd(root, side.node_role_location)
                # role = side.node_role.keys()[0][0] # Get the first key and get the first element from that tuple
                # self.log.info('Node role: ', role, ' side.node_role: ', type(side.node_role), ' ', side.node_role.keys(), ' ::: ', type(side.node_role.keys()))
                # fonodetemplatestr = '/dtpn:network/dtpn:function-object-definitions/dtpn:link/'+linktype+'{"'+linktypenode.function_object_name+'"}/link-policy-base:'+str(role)+'/link-policy-base:template'
                # self.log.info('Func. Object Node: ', fonodetemplatestr)
                # fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                # self.log.info('APPLY TEMPLATE: Node: ', side.node, ' Template: ', fo_template_name)
                # template.apply(fo_template_name, vars)
                for foname in side.function_objects: # This gets the list of different policy types defined
                    self.log.info('foname: ', foname)
                    folist = ncs.maagic.cd(side.function_objects,foname)
                    for foentryname in folist: # This get each list entry in the policy type
                        self.log.info('foentryname: ', foentryname)
                        foentrynode = ncs.maagic.cd(folist,foentryname)
                        vars.add('FO-NAME', foentrynode.function_object_name)
                        self.log.info('FO-NAME: ', foentrynode.function_object_name)
#                        fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:link'+'{"'+str(link_name)+'"}'+'/dtpn:side'+'{"'+str(side.name)+'"}/'+str(foname)+'{"'+str(foentrynode.function_object_name)+'"}/template'
                        fonodetemplatestr = '/dtpn:dtp/dtpn:function-object-definitions/dtpn:link/dtpn:side/'+str(foname)+'{"'+str(foentrynode.function_object_name)+'"}/template'
                        self.log.info('Func. Object Template Location: ', fonodetemplatestr)
                        fo_template_name = ncs.maagic.cd(root, fonodetemplatestr)
                        self.log.info('APPLY TEMPLATE: ', fo_template_name)
                        if fo_template_name is not None:
                            template.apply(fo_template_name, vars)


    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')


    @Service.pre_modification
    def cb_pre_modification(self, tctx, op, kp, root, proplist):
        self.log.info('Service premod(service=', kp, ", Operation: ", op, ')')

    @Service.post_modification
    def cb_post_modification(self, tctx, op, kp, root, proplist):
        self.log.info('Service postmod(service=', kp, ", Operation: ", op, ')')
# NCS_SERVICE_CREATE = 0
# NCS_SERVICE_DELETE = 2
# NCS_SERVICE_UPDATE = 1
        # if op == DP.NCS_SERVICE_DELETE:
        #     service = ncs.maagic.cd(root, kp)
        #     for topology in service.topology:
        #         deploynode = ncs.maagic.cd(topology.deployment_type, str(topology.deployment_type.deployment_type))
        #         self.log.info("Deployment Callback Class: ", deploynode.callback_class)
        #         if deploynode.callback_class == 'NONE':
        #             self.log.info("Deployment type has no callback, assuming devices are registered with NSO")
        #         else:
        #             callback_module = importlib.import_module(str(deploynode.callback_class).rsplit('.',1)[0])
        #             callback_class = getattr(callback_module, str(deploynode.callback_class).rsplit('.',1)[1])
        #             callback = callback_class()
        #             callback.delete_topology(root, service, topology, self.log)

class LoadServiceTemplate(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        service_name = input.network_name
        topology_template = input.topology_template
        self.log.info('action name: ', name)
        self.log.info('Service Name: ', service_name)
        self.log.info('Template: ', topology_template)
        self.log.info('Keypath: ', kp)
#        self.log.info('SELF WT: ', type(self._wt), ' ', dir(self._wt))
        # Updating the output data structure will result in a response
        # being returned to the caller.
        with ncs.maapi.Maapi() as m:
            with ncs.maapi.Session(m, uinfo.username, uinfo.context):
                with m.start_write_trans() as t:
                    template_name = t.get_elem("/network/policy-definitions/network/dtpn:topology-templates{"+topology_template+"}/model-template-file")
                    self.log.info('Topology Template Name: ', template_name)
                    vars = ncs.template.Variables()
                    vars.add('SERVICE-NAME', service_name)
                    m.apply_template(t.th,name=str(template_name),path=kp,vars=vars)
                    t.apply()

class TestService(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        self.log.info('Keypath: ', kp)

        with ncs.maapi.Maapi() as m:
            with ncs.maapi.Session(m, uinfo.username, uinfo.context):
                with m.start_write_trans() as t:
                    service = ncs.maagic.get_node(t, kp)
                    service_status = "PASSED"
                    for test in service.test:
                        self.log.info('test node: ', test.node)
                        node = ncs.maagic.get_node(t, '/devices/node{'+str(test.node)+'}')
                        command = test.command
                        match_criteria = test.match_criteria
                        self.log.info('node: ', node)
                        self.log.info('test command: ', command)
                        self.log.info('match_criteria: ', match_criteria)
                        action = node.live_status.ios_stats__exec.any
                        action_input = action.get_input()
                        action_input.args = str(command).split(' ')
                        action_result = action.request(action_input)
                        self.log.info('Command Returned: ', action_result.result)
                        test.command_output = action_result.result
                        test_result = "FAILED"
                        for line in action_result.result.splitlines():
                            if all(crition in line for crition in match_criteria):
                                test_result = "PASSED"
                                break;
                        if test_result == "FAILED":
                            service_status = "FAILED"
                        test.status = test_result
                        service.service_status = service_status
                    t.apply()

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('DTPService RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
#        self.register_service('dtp-network-servicepoint', ServiceCallbacks)
        self.register_action('loadservicetemplate-action', LoadServiceTemplate)
        self.register_action('testservice-action', TestService)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('DTPService FINISHED')
