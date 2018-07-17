# -*- mode: python; python-indent: 4 -*-
import ncs
# from ncs.application import Service
# from ncs.dp import Action
# from ncs.maapi import Maapi
# import sys
# from nso_device_management import NSODeviceManagement
# import importlib
# import _ncs.dp as DP

class NodeServiceCallbacks(ncs.application.NanoService):

    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        self.log.info("dtpn:create-devices(CREATE) ", component, " ",state, " ", currstate.status)
        self.log.info("dtpn:create-devices(CREATE) ", proplist)
        root.devices.device['core-1'].description = "JOHAN TEST"
#        service.node[component].state = "done"
        pl = proplist + [('johan', 'created')]
        return pl;

    @ncs.application.NanoService.delete
    def cb_nano_delete(self, tctx, root, service, component, state, proplist):
        currstate = service.plan.component[component].state[state]
        self.log.info("dtpn:create-devices(DELETE) ", component, " ", state, " ", currstate.status)
        self.log.info("dtpn:create-devices(DELETE) ", proplist)
        currstate.status = 'not-reached'
        self.log.info("dtpn:create-devices(DELETE) ", currstate.status)
        return proplist
#        currstate.status = 'reached'

        # deploynode = ncs.maagic.cd(topology.deployment_type, str(topology.deployment_type.deployment_type))
        # self.log.info("Deployment Callback Class: ", deploynode.callback_class)
        # if deploynode.callback_class == 'NONE':
        #     self.log.info("Deployment type has no callback, assuming devices are registered with NSO")
        # else:
        #     callback_module = importlib.import_module(str(deploynode.callback_class).rsplit('.',1)[0])
        #     callback_class = getattr(callback_module, str(deploynode.callback_class).rsplit('.',1)[1])
        #     callback = callback_class()
        #     callback.create_topology(root, service, topology, self.log)

class Topology(ncs.application.Application):
    def setup(self):
        self.register_nano_service('dtp-topology-servicepoint',
                                    'dtpn:deploy-netsim-topology',
                                    'dtpn:create-topology',
                                    NodeServiceCallbacks)

        self.log.info('TopologyBuild Nano Service RUNNING')

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('DTPService FINISHED')
