"""
TGEN Triggers
"""
import re
from attrdict import AttrDict
from star.infra.base import StarOperBase, StarLog
from utils.helper import Helper
from star.infra.globals import Globals
from star.infra.utils import setProxy, connect_to_tgen_session

from tgn.base import TGN
from tgn.spirent_resthttp import RestHttp
from tgn.spirent_results_analysis import SpirentResultAnalysis
from tgn.spirent_utils import TrafficStats, TgenDevice, TgenTrafficItem, MulticastGroup, LinkStatusInfo
from tgn.spirent_resthttp import RestHttpError
from tgn.stc_gen import StcGen
import logging

log = StarLog('star_trig_tgen')

class TgenBngPerformPPPOE(StarOperBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param.router_id = []
        self.param.command_action = 'connect'  # dynamic
        self.param.mode = "pbng"
        self.param.cmd_filter = "dummy"
        self.param.filter_type = 'dual'   # dynamic
        self.param.session_name = "STARLORD_session - SIT-BNG-LSP"
        #self.param.session_name = "SRG_session - SIT-BNG-LSP"
        #self.param.session_name = "TORCHWOOD_session - SIT-BNG-LSP"
        self.param.tgen = ''
        self.param.tgen_timeout = 600
        self.param.lease_time = 600
        self.param.filter_value = ""
        self.param.outer_vlan_id = ""
        self.param.inner_vlan_id = ""
        self.param.location = "all"
        self.param.output_from_file = ""
        self.param.session_count = "1000"
        self.param.scale = False
        self.param.dut_verify = []
        self.param.churn = False
        self.param.iteration = 1
        self.param.port_list = []
        self.param.tolerance = 0
        self.param.wait_after_session = 300
        self.set_params(kwargs)


    def execute(self):
        tgn_device = self.get_device_obj(self.param.tgen)
        max_retries = 20
        current_retry = 1 
        total_sub_up = 0
        command_action_list = ["connect","disconnect"]
        find_pppoe_devices = False
        device_database = False
        exception_hit_cnt = 10
        start_dev_once = True
        self.param.old_tgn_session = tgn_device.session_name
        TGN_session_ID= tgn_device._session_id()
        tgn_device.session_name, tgn_device.user_name = self.param.session_name.split(" - ")
        tgn_device.session_name = tgn_device.session_name.strip()
        tgn_device.user_name = tgn_device.user_name.strip()
        tgn_device.timeout = self.param.tgen_timeout
        stop_on_fail = True
        if self.param.churn:
            command_action_list = command_action_list*self.param.iteration
        else:
            command_action_list = []
            command_action_list.append(self.param.command_action)
        try:
            churn_iter = 1
            for command_action_item in command_action_list:
                #spm
                # import pdb; pdb.set_trace() #pdbm
                l_session_count = self.param.session_count
                self.param.command_action = command_action_item  
                churn_iter += 1
                if self.param.churn and (churn_iter % 2) == 0:
                    log.banner("Churn Iteration %s " %(int(churn_iter/2)))
                    #spm
                # import pdb; pdb.set_trace() #pdbm
                # log.banner("Start PPPOE %s" %(self.param.command_action))     
                # if ((churn_iter % 2) == 0):
                    #############reconnect block
                    log.info("Reconnecting to avoid time out")
                    log.info("Disconnect TGEN")
                    tgn_device._end_session(end_tcsession=False)
                    time.sleep(30)
                    log.info("reconnect TGEN after 5 mins")
                    # connect_to_tgen_session(tgn_device, self.param.session_name)
                    tgn_device.connect_to_session(sid=None, skip_protocols=True)


                log.banner("Start PPPOE %s" %(self.param.command_action))     
                tolerance_value = int(round(int(l_session_count)*float(self.param.tolerance)/100))
                final_session_count = int(l_session_count)-int(tolerance_value)
                list_to_remove = []  
                action_completed = []
                Total_action_completed = []      
                for dev_v in self.param.dut_verify:
                    device = self.get_device_obj(dev_v)
                    conn = self.get_connection(device_name=dev_v)
                    dev_bng_obj = Bng(device = conn.device, name='bng', mode=conn.mode)
                    expected_sub_count = dev_bng_obj.PbngSubscriberSummary(session_counts_type=l_session_count)
                    if self.param.cmd_filter == "dummy":
                            self.param.cmd_filter = None
                    key=["session_counts_type"]
                    sub_data =  dev_bng_obj.get_subscriber_summary(self.param.mode, self.param.cmd_filter, self.param.filter_value, \
                        self.param.filter_type, self.param.outer_vlan_id, self.param.inner_vlan_id, self.param.location, self.param.output_from_file)
                # 
                tgn_device.connect_to_session(sid=None, skip_protocols=True,)
                # import pdb; pdb.set_trace() #pdbm
                # pppoe_clinet_state = tgn_device.get_pppoe_client_state()
                resulttype='PppoeClientBlockResults'
                target_rdspppoe = tgn_device._result_subscribe_check(resulttype)
                tgn_device._get('project1','children-ResultDataSet').split()
                log.info("length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))

                pppoe_sub_up = False
                pppoe_sub_down = False
                total_up = False
                pppoe_block, pppoe_server, pppoe_bndcnt = ({} for i in range(3))
                total_sub_up_dual, total_sub_up_v4, total_sub_up_v6, total_sub_up_1 = ("0" for i in range(4))  #mcheck
                # v4_dhcp_block, v6_dhcp_block, v4_dhcp_server, v6_dhcp_server, v4bndcnt = ({} for i in range(5))
                # total_sub_up_dual, total_sub_up_v4, total_sub_up_v6, total_sub_up_1 = ("0" for i in range(4))
                v4_actual_blockstate, v6_actual_blockstate = ('' for i in range(2))

                if self.param.command_action == 'disconnect':
                    l_session_count = 0

                if not find_pppoe_devices:
                    find_pppoe_devices = True
                    dict_emulated_devices= tgn_device._get_dict_emulated_devices()
                    self.param.router_id = tgn_device.get_device_names()
                    list_of_devices_org = list(self.param.router_id)
                    list_of_devices = list_of_devices_org
                    log.info("%s Devices configured in TGEN %s" %(len(list_of_devices),list_of_devices))
                    device_details = AttrDict()
                    list_of_devices_edited = list_of_devices
                    list_to_remove = []
                    list_of_devices_new = []
                    v4_devices = []
                    v6_devices = []
                    max_obj = int(len(list_of_devices))
                    port4_devc_name_list, port6_devc_name_list = ([] for i in range(2))

                    # import pdb; pdb.set_trace()
                    if (self.param.filter_type == "dual") or (self.param.filter_type == "v4"):
                        var1 = tgn_device._perform("GetObjects", ClassName="emulateddevice", Condition=f".PppoeClientBlockConfig.Active ={True}")['ObjectList'].split()
                        var2 = tgn_device._bulk_get(var1, ['name','devicecount'], max_objects_per_request=40)
                        var3 = tgn_device._perform("GetObjects", ClassName="PppoeClientBlockConfig")['ObjectList'].split()
                        var4 = tgn_device._bulk_get(var3, 'parent', max_objects_per_request=40)

                        for v4_emu in var1:
                            port_devcname = tgn_device._get(v4_emu, 'affiliationport-Targets', 'name', 'DeviceCount')
                            devc_name = port_devcname['name']
                            devc_port = port_devcname['affiliationport-Targets']
                            devc_count = port_devcname['DeviceCount']
                            port_devcname['emudev'] = v4_emu
                            v4_devices.append(devc_name)
                            port4_devc_name_list.append(port_devcname)
                        log.info("%s v4 PPPOE Devices configured in TGEN %s" %(len(v4_devices),v4_devices))

                        for dict_key4 in var4.keys():
                            # print(dict_key)
                            # print(var4[dict_key]['parent'])
                            if var4[dict_key4]['parent'] in var2:
                                var2[var4[dict_key4]['parent']]['PppoeClientBlockConfig'] = dict_key4


                    if (self.param.filter_type == "dual") or (self.param.filter_type == "v6"):
                        var11 = tgn_device._perform("GetObjects", ClassName="emulateddevice", Condition=f".PppoeClientBlockConfig.Active ={True}")['ObjectList'].split()
                        var12 = tgn_device._bulk_get(var1, ['name','devicecount'], max_objects_per_request=40)
                        var13 = tgn_device._perform("GetObjects", ClassName="PppoeClientBlockConfig")['ObjectList'].split()
                        var14 = tgn_device._bulk_get(var3, 'parent', max_objects_per_request=40)
                    
                        for v6_emu in var11:
                            port_devcname = tgn_device._get(v6_emu, 'affiliationport-Targets', 'name', 'DeviceCount')
                            devc_name = port_devcname['name']
                            devc_port = port_devcname['affiliationport-Targets']
                            devc_count = port_devcname['DeviceCount']
                            port_devcname['emudev'] = v6_emu
                            v6_devices.append(devc_name)
                            port6_devc_name_list.append(port_devcname)
                            # v6_devices.append(tgn_device._get(v6_emu,'name'))
                        log.info("%s v6 PPPOE Devices configured in TGEN %s" %(len(v6_devices),v6_devices))
                        # import pdb; pdb.set_trace() #pdbm
                        for dict_key6 in var14.keys():
                            # print(dict_key11)
                            # print(var14[dict_key11]['parent'])
                            if var14[dict_key6]['parent'] in var12:
                                var12[var14[dict_key6]['parent']]['PppoeClientBlockConfig'] = dict_key6


                    #port based devices
                    # import pdb; pdb.set_trace() #pdbm
                    total_dev_count_portv4,total_dev_count_portv6 = [dict() for i in range(2)]
                    port_devc_v4devices_org,port_devc_v4count,port_devc_v4details,port_devc_v4emudev,port_namev4 = [dict() for i in range(5)]
                    unique_port_list = []

                    # import pdb; pdb.set_trace() #pdbm
                    for port_devc in port4_devc_name_list:
                        port_id4 = port_devc['affiliationport-Targets']
                        devcname4 = port_devc['name']
                        devccount = port_devc['DeviceCount']
                        v4_emu = port_devc['emudev']
                        
                        # print(port_id4,devcname4)
                        # print(port_devc_v4devices.keys(), port_devc_v4devices.values())
                        if port_id4 not in port_devc_v4devices_org.keys():
                            port_devc_v4devices_org[port_id4],port_devc_v4count[port_id4],port_devc_v4emudev[port_id4] = ([] for i in range(3))
                            port_devc_v4details[port_id4] = dict()
                        port_devc_v4devices_org[port_id4].append(devcname4)
                        port_devc_v4details[port_id4][devcname4] = dict()
                        port_devc_v4count[port_id4].append(int(devccount))
                        port_devc_v4emudev[port_id4].append(v4_emu)
                        port_devc_v4details[port_id4][devcname4]['DeviceCount'] = int(devccount)
                        port_devc_v4details[port_id4][devcname4]['emudev'] = v4_emu
                        # t_list4 = port_devc_v4devices_org[port_id4]
                        # port_devc_v4devices_org[port_id4] = tuple(t_list4)
                    # import pdb; pdb.set_trace()
                    for pkey in port_devc_v4details.keys():
                        prt_name = tgn_device._get(pkey, 'name')
                        port_namev4[pkey] = prt_name
                        
                    log.info("v4 Devices configured at Port: %s" %port_devc_v4devices_org)
                    log.info("v4 emulations configured at Port: %s" %port_devc_v4emudev)
                    log.info("v4 Session count of Devices at Port: %s" %port_devc_v4count)
                    for pk in port_devc_v4count:
                        total_dev_count_portv4[pk] = sum(port_devc_v4count[pk])
                    log.info("Total session of all v4 Devices at Port: %s" %total_dev_count_portv4)
                    
                    port_devc_v6devices_org,port_devc_v6count,port_devc_v6details,port_devc_v6emudev,port_namev6 = [dict() for i in range(5)]
                    # import pdb; pdb.set_trace() #pdbm
                    for port_devc in port6_devc_name_list:
                        port_id6 = port_devc['affiliationport-Targets']
                        devcname6 = port_devc['name']
                        devccount = port_devc['DeviceCount']
                        v6_emu = port_devc['emudev']
                        # print(port_id6,devcname6)
                        # print(port_devc_v6devices.keys(), port_devc_v6devices.values())
                        if port_id6 not in port_devc_v6devices_org.keys():
                            port_devc_v6devices_org[port_id6],port_devc_v6count[port_id6],port_devc_v6emudev[port_id6]= ([] for i in range(3))
                            port_devc_v6details[port_id6] = dict()
                        port_devc_v6devices_org[port_id6].append(devcname6)
                        port_devc_v6details[port_id6][devcname6] = dict()
                        port_devc_v6count[port_id6].append(int(devccount))
                        port_devc_v6emudev[port_id6].append(v6_emu)
                        port_devc_v6details[port_id6][devcname6]['DeviceCount'] = int(devccount)
                        port_devc_v6details[port_id6][devcname6]['emudev'] = v6_emu
                        # t_list6 = port_devc_v6devices_org[port_id6]
                        # port_devc_v6devices_org[port_id6] = tuple(t_list6)
                    # import pdb; pdb.set_trace() #pdbm
                    for pkey in port_devc_v6details.keys():
                        prt_name = tgn_device._get(pkey, 'name')
                        port_namev6[pkey] = prt_name
                        
                    log.info("v6 Devices configured at Port: %s" %port_devc_v6devices_org)
                    log.info("v6 emulations configured at Port: %s" %port_devc_v6emudev)
                    log.info("v6 Session count of Devices at Port: %s" %port_devc_v6count)

                    for pk in port_devc_v6count:
                        total_dev_count_portv6[pk] = sum(port_devc_v6count[pk])
                        if (self.param.filter_type == "v6"):
                            total_dev_count_portv4 = total_dev_count_portv6
                    log.info("Total session of all v6 Devices at Port: %s" %total_dev_count_portv6)                    

                    # import pdb; pdb.set_trace() #pdbm
                    

                    if (self.param.filter_type == "dual"):
                        if (len(v4_devices) == len(v6_devices)) and (v4_devices == v6_devices):
                            list_of_devices_new = v4_devices
                            log.info("v4 and v6 DHCP Devices configured in TGEN are equal")
                        elif (len(v4_devices) == len(v6_devices)) and (v4_devices != v6_devices) \
                             or (len(v4_devices) != len(v6_devices)):
                            log.info("v4 and v6 DHCP Devices configured in TGEN are not equal")
                            list_of_devices_new = v4_devices
                            if len(v4_devices) > len(v6_devices):
                                list_of_devices_new = v4_devices
                            elif len(v4_devices) < len(v6_devices):
                                list_of_devices_new = v6_devices
                            else:
                                list_of_devices_new = v4_devices
                            if len(v6_devices) > 0:
                                for dev_6 in v6_devices:
                                    if (dev_6 not in v4_devices) and (dev_6 not in list_of_devices_new):
                                        list_of_devices_new.append(dev_6)
                            if len(v4_devices) > 0:
                                for dev_4 in v4_devices:
                                    if (dev_4 not in v6_devices) and (dev_4 not in list_of_devices_new):
                                        list_of_devices_new.append(dev_4)
                    elif (self.param.filter_type == "v4"):
                        list_of_devices_new = v4_devices
                    elif (self.param.filter_type == "v6"):
                        list_of_devices_new = v6_devices

                    list_of_devices_edited = list_of_devices_new.copy()
                    list_of_devices = list_of_devices_new.copy()
                    #bulk

                    # import pdb; pdb.set_trace() #pdbm
                    list_of_emulated_device_v4 = []
                    list_of_emulated_device_v6 = []
                    if (self.param.filter_type == "dual") or (self.param.filter_type == "v4"):
                        for dict_key2 in var2.keys():
                            device_name = var2[dict_key2]['name']
                            if device_name in list_of_devices_new:
                                device_details[device_name] = device_name
                                device_details[device_name] = AttrDict()
                                device_details[device_name]['emulateddevice'] = dict_key2
                                device_details[device_name]['DeviceCount'] = var2[dict_key2]['devicecount']
                                if var2[dict_key2]['PppoeClientBlockConfig']:
                                    device_details[device_name]['v4_block'] = True
                                    device_details[device_name]['v4_pppoeblock_config'] = var2[dict_key2]['PppoeClientBlockConfig']
                                    list_of_emulated_device_v4.append(dict_key2)
                                else:
                                    device_details[device_name]['v4_block'] = False
                                #calculate port level count

                    if (self.param.filter_type == "dual") or (self.param.filter_type == "v6"):
                        for dict_key3 in var12.keys():
                            device_name = var12[dict_key3]['name']
                            if device_name in list_of_devices_new:
                                dev_details_exist = False
                                if (device_name in device_details.keys()) and \
                                (device_details[device_name]['emulateddevice'] == dict_key3) and \
                                (device_details[device_name]['DeviceCount'] == var12[dict_key3]['devicecount']):
                                    dev_details_exist = True
                                if not dev_details_exist:
                                    device_details[device_name] = device_name
                                    device_details[device_name] = AttrDict()
                                    device_details[device_name]['emulateddevice'] = dict_key3
                                    device_details[device_name]['DeviceCount'] = var12[dict_key3]['devicecount']
                                if var12[dict_key3]['PppoeClientBlockConfig']:
                                    device_details[device_name]['v6_block'] = True
                                    device_details[device_name]['v4_pppoeblock_config'] = var12[dict_key3]['PppoeClientBlockConfig']
                                    list_of_emulated_device_v6.append(dict_key3)
                                else:
                                    device_details[device_name]['v6_block'] = False

                    list_of_devices_edited = list_of_devices_new.copy()
                    list_of_devices = list_of_devices_new.copy()

                    port_devc_v4devices_edited, port_devc_v4devices = [dict() for i in range(0,2)]
                    for ky4 in port_devc_v4devices_org.keys():
                        tup_v4 = port_devc_v4devices_org[ky4]
                        port_devc_v4devices_org[ky4] = tuple(tup_v4)
                        port_devc_v4devices_edited[ky4] = list(tup_v4)
                        port_devc_v4devices[ky4] = list(tup_v4)


                    port_devc_v6devices_edited, port_devc_v6devices = [dict() for i in range(0,2)]
                    for ky6 in port_devc_v6devices_org.keys():
                        tup_v6 = port_devc_v6devices_org[ky6]
                        port_devc_v4devices_org[ky6] = tuple(tup_v6)
                        port_devc_v6devices_edited[ky6] = list(tup_v6)
                        port_devc_v6devices[ky6] = list(tup_v6)

                    # import pdb; pdb.set_trace() #pdbm

                    if self.param.filter_type == "v6":
                        port_devc_v4devices_org = port_devc_v6devices_org.copy()
                        port_devc_v4devices_edited = port_devc_v6devices_org.copy()
                        port_devc_v4devices = port_devc_v6devices_org.copy()
                log.info("%s Total PPPOE Devices configured in TGEN %s" %(len(list_of_devices_new),list_of_devices_new))

                for ky4 in port_devc_v4devices_org.keys():
                    tup_v4 = port_devc_v4devices_org[ky4]
                    port_devc_v4devices_edited[ky4] = list(tup_v4)
                    port_devc_v4devices[ky4] = list(tup_v4)
                

                for ky6 in port_devc_v6devices_org.keys():
                    tup_v6 = port_devc_v6devices_org[ky6]
                    port_devc_v6devices_edited[ky6] = list(tup_v6)
                    port_devc_v6devices[ky6] = list(tup_v6)
                
                log.info("id of port_devc_v4devices_org %s" %port_devc_v4devices_org)
                log.info("id of port_devc_v4devices_edited %s" %port_devc_v4devices_edited)
                log.info("id of port_devc_v4devices %s" %port_devc_v4devices)
                # import pdb; pdb.set_trace() #pdbm

                #####################
                #populate devices in ports in a list for comparision
                port_list_devc4, port_list_devc6 = ([] for i in range(2))
                for pkey in port_devc_v4devices:
                    for devcn in port_devc_v4devices[pkey]:
                        port_list_devc4.append(devcn)
                log.info("%s Total PPPOE Devices configured in ports v4 %s" %(len(port_list_devc4),port_list_devc4))
                for pkey in port_devc_v6devices:
                    for devcn in port_devc_v6devices[pkey]:
                        port_list_devc6.append(devcn)
                log.info("%s Total PPPOE Devices configured in ports v6 %s" %(len(port_list_devc6),port_list_devc6))
                
                ######################
                ######################
                #comparision
                # import pdb; pdb.set_trace()
                set_portv4 = set(port_list_devc4)
                set_portv6 = set(port_list_devc6)
                set_org_dev_list = set(list_of_devices_new)

                if len(set_portv4&set_org_dev_list) == len(list_of_devices_new) :
                    log.info("v4 devices in all ports %s are similar to total device list %s" %(port_list_devc4,list_of_devices_new))
                else:
                    if len(set_portv4^set_org_dev_list) == 0:
                        DUP_devices4 = {DUP_d4 for DUP_d4 in port_list_devc4 if port_list_devc4.count(DUP_d4) > 1}
                        log.banner("Duplicate devices in v4 port list and total list %s" %(DUP_devices4))
                    else:
                        log.banner("devices are not matching between v4 port list and total list %s" %(set_portv4^set_org_dev_list))
                if len(set_portv6&set_org_dev_list) == len(list_of_devices_new) :
                    log.info("v6 devices in all ports %s are similar to total device list %s" %(port_list_devc6,list_of_devices_new))
                else:
                    if len(set_portv6^set_org_dev_list) == 0:
                        DUP_devices6 = {DUP_d6 for DUP_d6 in port_list_devc6 if port_list_devc6.count(DUP_d6) > 1}
                        log.banner("Duplicate devices in v4 port list and total list %s" %(DUP_devices6))
                    else:
                        log.banner("devices are not matching between v6 port list and total list %s" %(set_portv6^set_org_dev_list))

                remove_port_devc_v4devices = dict()
                #counter for checking router session count
                if (self.param.command_action == 'disconnect'):
                    completed_portv4_count = int(self.param.session_count)
                    completed_portv6_count = int(self.param.session_count)
                elif (self.param.command_action != 'disconnect'): 
                    completed_portv4_count = 0
                    completed_portv6_count = 0
                #
                self.Total_CPS = 0
                self.total_port_action_time = 0
                self.PORT_CPS_LIST = []
                self.cps_port = dict()
                self.expected_cumulative_count = 0
                import time

                #edit dhcp starts
                ##
                tol_session_count_port = dict()   
                tol_total_count = 0
                
                for pkey in port_devc_v4devices:
                    #mara 1
                    # import pdb; pdb.set_trace()
                    self.start_emulation_time1 = 0
                    self.end_emulation_time2 = 0
                    self.emulation_time_diff = 0
                    self.emulation_port_cnt = len(port_devc_v4devices_org)
                    self.expected_cumulative_count += int(total_dev_count_portv4[pkey])
                    current_port_action_complete = False
                    check_only_router = False
                    # completed_portv4_count = 0
                    # completed_portv6_count = 0
                    if pppoe_sub_up or pppoe_sub_down:
                        break
                    if (self.param.command_action == 'disconnect'):
                        cumulative_port_bound_countv4 = int(total_dev_count_portv4[pkey])
                        cumulative_port_bound_countv6 = int(total_dev_count_portv6[pkey])
                        total_bound_countv4 = int(self.param.session_count)
                        total_bound_countv6 = int(self.param.session_count)
                        tmp_cnt_port = len(port_devc_v4devices_org[pkey])
                        device_cntr_port = tmp_cnt_port
                        # cumulative_port_bound_countv4,cumulative_port_bound_countv6 = (len(port_devc_v4devices_org[pkey]) for i in range(2))
                    elif (self.param.command_action != 'disconnect'): 
                        cumulative_port_bound_countv4,cumulative_port_bound_countv6 = (0 for i in range(2))
                        total_bound_countv4,total_bound_countv6 = (0 for i in range(2))
                        device_cntr_port = 0
                    if self.param.filter_type == "v6":
                        cumulative_port_bound_countv4 = cumulative_port_bound_countv6
                    log.banner(" PPPOE %s devices on port %s [%s] " %(self.param.command_action,pkey,port_namev4[pkey]))
                    # log.banner(" %s Total DHCP devices on port %s: %s " %(len(port_devc_v4devices[pkey]),pkey,port_devc_v4devices[pkey]))
                    log.banner(" %s Total PPPOE devices on port %s: %s " %(len(port_devc_v4devices_org[pkey]),pkey,port_devc_v4devices_org[pkey]))
                    if pkey not in remove_port_devc_v4devices.keys():
                        remove_port_devc_v4devices[pkey] = []
                    quit_port_loop = False     
                    tolerance_value_port = 0
                    session_count_port = 0      
                    for port_retry in range(1,max_retries):
                        try:
                            # import pdb; pdb.set_trace() #pdbm
                            #mara
                            log.info("ITERATION: %s on devices at port %s" % (port_retry,pkey))
                            # if int(port_retry) > 8:
                                # import pdb; pdb.set_trace()
                            # if ((current_retry % 2) == 0):
                            # #############reconnect block
                            # log.info("Reconnecting to avoid time out")
                            # log.info("Disconnect TGEN")
                            # tgn_device._end_session(end_tcsession=False)
                            # time.sleep(30)
                            # log.info("reconnect TGEN after 5 mins")
                            # # connect_to_tgen_session(tgn_device, self.param.session_name)
                            # tgn_device.connect_to_session(sid=None, skip_protocols=True)
                            # #######################
                            if remove_port_devc_v4devices[pkey]:
                                # import pdb; pdb.set_trace()
                                log.info("Modifying the device list for port %s: %s" %(pkey,remove_port_devc_v4devices[pkey]))
                                for device_name in remove_port_devc_v4devices[pkey]:
                                    if device_name in port_devc_v4devices_edited[pkey]:
                                        port_devc_v4devices_edited[pkey].remove(device_name)  
                                        # import pdb; pdb.set_trace()
                                log.info("%s PPPOE Devices configured on port %s: %s" %(len(port_devc_v4devices_org[pkey]),pkey,port_devc_v4devices_org[pkey]))
                                log.info("%s PPPOE Devices modified for verification %s" %(len(port_devc_v4devices_edited[pkey]),port_devc_v4devices_edited[pkey]))
                                action_completed.extend(remove_port_devc_v4devices[pkey])
                                log.info("%s PPPOE Devices completed action %s" %(len(action_completed),action_completed))
                            remove_port_devc_v4devices[pkey] = []
                            # tolerance_value_port = int(int(total_dev_count_portv4[pkey])*float(self.param.tolerance)/100)
                            # session_count_port = int(total_dev_count_portv4[pkey])-int(tolerance_value_port)
                            if (self.param.command_action != 'disconnect'):
                                tolerance_value_port = int(int(total_dev_count_portv4[pkey])*float(self.param.tolerance)/100)
                                session_count_port = int(total_dev_count_portv4[pkey])-int(tolerance_value_port)
                                tol_session_count_port[pkey] = session_count_port
                                tol_total_count =+ session_count_port
                                log.info("Tolerance Port value %s, Total Session value %s" %(tol_session_count_port[pkey],tol_total_count))
                                if self.param.tolerance != 0:
                                    if current_port_action_complete or (int(cumulative_port_bound_countv4) >= session_count_port):
                                        Total_action_completed = action_completed
                                        log.info("Tolerance %s, Port %s Tolerance value: %s, Session count Threshold: %s" %(self.param.tolerance,pkey,tolerance_value_port,session_count_port))
                                        log.info("Total bound count in port %s[%s] completed action %s: %s " %(pkey,port_namev4[pkey],self.param.command_action,cumulative_port_bound_countv4))
                                        log.info("All %s Devices in port %s[%s]completed action %s: %s " %(len(action_completed),pkey,port_namev4[pkey],self.param.command_action,device_cntr_port))
                                        action_completed = []
                                        # break
                                        if quit_port_loop:
                                            break
                                        else:
                                            check_only_router = True
                                            completed_portv4_count_tol = int(int(completed_portv4_count)*float(self.param.tolerance)/100)
                                            if int(total_sub_up_dual) >= completed_portv4_count_tol:
                                                #mara 2
                                                # import pdb; pdb.set_trace()
                                                # if check_only_router:
                                                log.info("Check only Router Passed after BIND2")
                                                check_only_router = False
                                                quit_port_loop = True
                                            else:
                                                log.info("total_sub_up_dual %s, completed_portv4_count_tol %s" %(total_sub_up_dual,completed_portv4_count_tol))
                                else:
                                    tolerance_value_port = int(int(total_dev_count_portv4[pkey])*float(self.param.tolerance)/100)
                                    session_count_port = int(total_dev_count_portv4[pkey])-int(tolerance_value_port)
                                    tol_session_count_port[pkey] = int(tolerance_value_port)
                                    tol_total_count =+ int(tolerance_value_port)
                                    log.info("Tolerance Port value %s, Total Session value %s" %(tol_session_count_port[pkey],tol_total_count))
                                    if current_port_action_complete or (int(device_cntr_port) == int(len(port_devc_v4devices_org[pkey]))):
                                        #mara 3
                                        # import pdb; pdb.set_trace()
                                        Total_action_completed = action_completed
                                        log.info("Total bound count in port %s[%s] completed action %s: %s " %(pkey,port_namev4[pkey],self.param.command_action,cumulative_port_bound_countv4))
                                        log.info("All %s Devices in port %s[%s]completed action %s: %s " %(len(action_completed),pkey,port_namev4[pkey],self.param.command_action,device_cntr_port))
                                        action_completed = []
                                        # log.info("All %s Devices in port %s completed action %s: %s " %(len(port_devc_v4devices_org[pkey]),pkey,self.param.command_action,device_cntr_port))
                                        # for dev_v in self.param.dut_verify:
                                        # break
                                        if quit_port_loop:
                                            break
                                        else:
                                            check_only_router = True
                                            if int(total_sub_up_dual) == completed_portv4_count:
                                                # import pdb; pdb.set_trace()
                                                # if check_only_router:
                                                log.info("Check only Router Passed after BIND2")
                                                check_only_router = False
                                                quit_port_loop = True
                                            else:
                                                log.info("total_sub_up_dual %s, completed_portv4_count_tol %s" %(total_sub_up_dual,completed_portv4_count))
                            elif (self.param.command_action == 'disconnect'):
                                if self.param.tolerance != 0:
                                    #mara 3
                                    # import pdb; pdb.set_trace()
                                    if current_port_action_complete or (int(cumulative_port_bound_countv4) <= tolerance_value_port):
                                        Total_action_completed = action_completed
                                        log.info("Tolerance %s, Port %s Tolerance value: %s, Session count Threshold: %s" %(self.param.tolerance,pkey,tolerance_value_port,session_count_port))
                                        log.info("Total bound count in port %s[%s] completed action %s: %s " %(pkey,port_namev4[pkey],self.param.command_action,cumulative_port_bound_countv4))
                                        log.info("All %s Devices in port %s[%s] completed action %s: %s " %(len(action_completed),pkey,port_namev4[pkey],self.param.command_action,device_cntr_port))
                                        action_completed = []
                                        # break
                                        if quit_port_loop:
                                            break
                                        else:
                                            check_only_router = True
                                            completed_portv4_count_tol = int(int(completed_portv4_count)*float(self.param.tolerance)/100)
                                            if int(total_sub_up_dual) <= completed_portv4_count_tol:
                                                # import pdb; pdb.set_trace()
                                                # if check_only_router:
                                                log.info("Check only Router Passed after REL2")
                                                check_only_router = False
                                                quit_port_loop = True
                                            else:
                                                log.info("total_sub_up_dual %s, completed_portv4_count_tol %s" %(total_sub_up_dual,completed_portv4_count_tol))
                                else:
                                    if current_port_action_complete or (int(device_cntr_port) == 0):
                                        # import pdb; pdb.set_trace()
                                        Total_action_completed = action_completed
                                        log.info("Total bound count in port %s[%s] completed action %s: %s " %(pkey,port_namev4[pkey],self.param.command_action,cumulative_port_bound_countv4))
                                        log.info("All %s Devices in port %s[%s] completed action %s: %s " %(len(action_completed),pkey,port_namev4[pkey],self.param.command_action,device_cntr_port))
                                        action_completed = []
                                        # log.info("All %s Devices in port %s completed action %s: %s " %(len(port_devc_v4devices_org[pkey]),pkey,self.param.command_action,device_cntr_port))
                                        # for dev_v in self.param.dut_verify:
                                        # break
                                        if quit_port_loop:
                                            break
                                        else:
                                            check_only_router = True
                                            if int(total_sub_up_dual) == completed_portv4_count:
                                                # import pdb; pdb.set_trace()
                                                # if check_only_router:
                                                log.info("Check only Router Passed after REL2")
                                                check_only_router = False
                                                quit_port_loop = True
                                            else:
                                                log.info("total_sub_up_dual %s, completed_portv4_count_tol %s" %(total_sub_up_dual,completed_portv4_count))

                            remove_port_devc_v4devices[pkey] = []
                            # import pdb; pdb.set_trace()

                            port_devc_v4devices = port_devc_v4devices_edited.copy()
                            log.info("%s PPPOE Devices configured on port %s: %s" %(len(port_devc_v4devices_org[pkey]),pkey,port_devc_v4devices_org[pkey]))
                            log.info("%s PPPOE Devices edited on port %s: %s" %(len(port_devc_v4devices_edited[pkey]),pkey,port_devc_v4devices_edited[pkey]))

                            ####
                            resulttype='PppoeClientBlockResults'
                            config_type='PppoeClientBlockConfig'
                            target_rdspppoe = tgn_device._result_subscribe_check(resulttype)
                            tgn_device._get('project1','children-ResultDataSet').split()
                            log.info("length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))
                            if target_rdspppoe == "":
                                v4results = tgn_device._perform('ResultsSubscribeCommand', resulttype=resulttype, Parent='project1',ConfigType=config_type)
                                v4result_dataset = v4results['ReturnedResultDataSet']
                                v4pppoeblock_results = tgn_device._get(v4result_dataset, 'ResultHandleList').split()
                                log.info("NEW:length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))
                            else:
                                v4pppoeblock_results = tgn_device._get(target_rdspppoe, 'ResultHandleList').split()
                                log.info("OLD:length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))
                            


                            # target_rdsv6 = tgn_device._result_subscribe_check(result_type6)
                            # tgn_device._get('project1','children-ResultDataSet').split()
                            # log.info("length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))
                            # if target_rdsv6 == "":
                            #     v6results = tgn_device._perform('ResultsSubscribeCommand', resulttype=result_type6, Parent='project1',ConfigType=config_type6)
                            #     v6result_dataset = v6results['ReturnedResultDataSet']
                            #     v6dhcpblock_results = tgn_device._get(v6result_dataset, 'ResultHandleList').split()
                            #     log.info("NEW:length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))
                            # else:
                            #     v6dhcpblock_results = tgn_device._get(target_rdsv6, 'ResultHandleList').split()
                            #     log.info("OLD:length of subscribe list in TGEN %s" %(len(tgn_device._get('project1','children-ResultDataSet').split())))

                            

                            # reconn block
                            # mid_len_device = len(list_of_devices) // 2
                            # reconnect_idx = 0
                            #change of loop from total dev to port by port
                            # for device_name in list_of_devices:
                            if not check_only_router:
                                if port_retry == 1 :
                                    # import pdb; pdb.set_trace()
                                    #mara
                                    if self.param.command_action != 'disconnect':
                                        log.info("v4 emulations configured at Port: %s" %port_devc_v4emudev)
                                        log.info("v6 emulations configured at Port: %s" %port_devc_v6emudev)
                                        log.banner("Starting all the emulated devices @ %s: %s" %(pkey,port_devc_v4emudev[pkey]))

                                        tgn_device._start_devices(port_devc_v4emudev[pkey])
                                        # start_emulation_time1 = time.time()
                                        self.start_emulation_time1 = datetime.datetime.now()
                                        time.sleep(60)
                                    elif self.param.command_action == 'disconnect':
                                        log.info("v4 emulations configured at Port: %s" %port_devc_v4emudev)
                                        log.info("v6 emulations configured at Port: %s" %port_devc_v6emudev)
                                        log.banner("Stoping all the emulated devices @ %s: %s" %(pkey,port_devc_v4emudev[pkey]))

                                        tgn_device._stop_devices(port_devc_v4emudev[pkey])
                                        time.sleep(60)
                                    continue
                                # import pdb; pdb.set_trace()
                                else:
                                    self.port_dev_idx = 1
                                    self.port_dev_count_reached = False
                                    # import pdb; pdb.set_trace()
                                    for device_name in port_devc_v4devices[pkey]:
                                        if self.param.command_action != 'disconnect':
                                            if ((len(port_devc_v4devices_org[pkey])) > 5 and (self.port_dev_idx >= 5)) \
                                            or ((len(port_devc_v4devices_org[pkey])) < 5 and (self.port_dev_idx == len(port_devc_v4devices_org[pkey]))):
                                                ##################################
                                                # import pdb; pdb.set_trace()
                                                log.info("Number of Devices @ port %s: %s, port idx:%s" %(pkey,len(port_devc_v4devices_org[pkey]),self.port_dev_idx))
                                                # return_dhcp_cps = self.get_dhcp_cps(dev_v,total_dev_count_portv4,pkey)
                                                
                                                self.port_dev_idx = 1
                                            else:
                                                self.port_dev_idx += 1
                                        
                                        ################# reconn block
                                        # reconnect_idx += 1
                                        # log.info("To reconnect TGEN: mid_dev_count: %s, reconnect_idx:%s" %(mid_len_device,reconnect_idx))
                                        # if reconnect_idx == mid_len_device:
                                        #     log.info("Disconnect TGEN")
                                        #     tgn_device._end_session(end_tcsession=False)
                                        #     log.info("reconnect TGEN")
                                        #     tgn_device.connect_to_session(sid=None, skip_protocols=True)
                                        #     # connect_to_tgen_session(tgn_device, self.param.session_name)
                                        #     reconnect_idx = 0
                                        ##############################
                                        remove_v4_device = remove_v6_device = False
                                        log.info("Device name %s" %(device_name))

                                        
                                          
                                    
                                        v4_actual_blockstate = v6_actual_blockstate = ''
                                        if device_details[device_name]['v4_pppoeblock_config'] and ((self.param.filter_type == "v4") or (self.param.filter_type == "dual")):

                                            for v4pppoeblock_result in v4pppoeblock_results:
                                                if tgn_device._get(v4pppoeblock_result, 'Parent') == device_details[device_name]['v4_pppoeblock_config']:
                                                    v4total_bound_count = tgn_device._get(v4pppoeblock_result, 'Sessions')
                                                    v4current_bound_count = tgn_device._get(v4pppoeblock_result, 'SessionsUp')
                                                    v6total_bound_count = v4total_bound_count
                                                    v6current_bound_count = v4current_bound_count
                                                    #portbyport
                                                    port_devc_v4details[pkey][device_name]['TotalBoundCount'] = v4total_bound_count
                                                    port_devc_v4details[pkey][device_name]['CurrentBoundCount'] = v4current_bound_count

                                                    port_devc_v6details[pkey][device_name]['TotalBoundCount'] = v4total_bound_count
                                                    port_devc_v6details[pkey][device_name]['CurrentBoundCount'] = v4current_bound_count
                                                    
                                                    # v4idle_count = tgn_device._get(v4pppoeblock_result, 'CurrentIdleCount')
                                                    v4_dev_count = device_details[device_name]['DeviceCount']
                                                    v6_dev_count = device_details[device_name]['DeviceCount']
                                                    log.info("TGEN: PPPOE Device: %s - total configured %s,total bound %s,current bound %s"  % (device_name,v4_dev_count,v4total_bound_count,v4current_bound_count))
                                                    if (self.param.command_action == 'disconnect' and int(v4current_bound_count) != 0) or \
                                                       (self.param.command_action != 'disconnect' and v4_dev_count != v4current_bound_count):
                                                    # if v4_dev_count != v4current_bound_count:
                                                        #debug @ http error
                                                        try:
                                                            # import pdb; pdb.set_trace()
                                                            #mara
                                                            log.info("Performing PPPOE %s" %(self.param.command_action))
                                                            # if (int(churn_iter/2)) == 2:
                                                            #     self.GoHereOnError(tgn_device)
                                                            # tgn_device.perform_dhcpv4_command(router_id=device_name, command_action=self.param.command_action)
                                                            tgn_device.perform_pppoe_action(router_id=device_name, action=self.param.command_action)
                                                            time.sleep(10)
                                                            # tgn_device.perform_pppoe_action(router_id=device_name, action=self.param.command_action)
                                                            # if stop_on_fail:
                                                            #     import pdb; pdb.set_trace()
                                                            remove_v4_device = False
                                                            remove_v6_device = False
                                                            #
                                                            v4total_bound_count = tgn_device._get(v4pppoeblock_result, 'Sessions')
                                                            v4current_bound_count = tgn_device._get(v4pppoeblock_result, 'SessionsUp')
                                                            v6total_bound_count = v4total_bound_count
                                                            v6current_bound_count = v4current_bound_count
                                                            #portbyport
                                                            port_devc_v4details[pkey][device_name]['TotalBoundCount'] = v4total_bound_count
                                                            port_devc_v4details[pkey][device_name]['CurrentBoundCount'] = v4current_bound_count

                                                            port_devc_v6details[pkey][device_name]['TotalBoundCount'] = v4total_bound_count
                                                            port_devc_v6details[pkey][device_name]['CurrentBoundCount'] = v4current_bound_count
                                                            
                                                            # v4idle_count = tgn_device._get(v4pppoeblock_result, 'CurrentIdleCount')
                                                            v4_dev_count = device_details[device_name]['DeviceCount']
                                                            v6_dev_count = device_details[device_name]['DeviceCount']
                                                            log.info("AFTER Action:TGEN: PPPOE Device: %s - total configured %s,total bound %s,current bound %s"  % (device_name,v4_dev_count,v4total_bound_count,v4current_bound_count))
                                                        except Exception as err:
                                                            log.fail("Failed to {} the session - {}".format(self.param.command_action, str(err)))
                                                            if (int(churn_iter/2)) == 2:
                                                                self.GoHereOnError(tgn_device)
                                                            #spm
                                                            # import pdb; pdb.set_trace()
                                                    elif (self.param.command_action == 'disconnect' and int(v4current_bound_count) == 0) or \
                                                       (self.param.command_action != 'disconnect' and v4_dev_count == v4current_bound_count):
                                                        remove_v4_device = True
                                                        remove_v6_device = True
                                                        # import pdb; pdb.set_trace()
                                                        # if device_name not in list_to_remove:
                                                        #     list_to_remove.append(device_name)
                                                        if (self.param.command_action == 'disconnect'):
                                                            log.info("TGEN: PPPOE Device: %s - After PPPOE %s- current bound is equal to %s"  % (device_name,self.param.command_action,v4current_bound_count))
                                                            # cumulative_port_bound_countv4 -=int(v4current_bound_count)
                                                        elif (self.param.command_action != 'disconnect'):
                                                            log.info("TGEN: PPPOE Device: %s - After PPPOE %s- configured session count %s is equal to current bound %s"  % (device_name,self.param.command_action,v4_dev_count,v4current_bound_count))
                                                            # cumulative_port_bound_countv4 +=int(v4current_bound_count)
                                                #port by port
                                                # port4_devc_name_list
                                        time.sleep(5)     


                                        # log.info("121 cd start OF v6 if")
                                        # if device_details[device_name]['v6_pppoeblock_config'] and ((self.param.filter_type == "v6") or (self.param.filter_type == "dual")):

                                        #     for v6dhcpblock_result in v6dhcpblock_results:
                                        #         if tgn_device._get(v6dhcpblock_result, 'Parent') == device_details[device_name]['v6_pppoeblock_config']:
                                        #             v6total_bound_count = tgn_device._get(v6dhcpblock_result, 'TotalBoundCount')
                                        #             v6current_bound_count = tgn_device._get(v6dhcpblock_result, 'CurrentBoundCount')
                                        #             # v6idle_count = tgn_device._get(v6dhcpblock_result, 'CurrentIdleCount')
                                        #             port_devc_v6details[pkey][device_name]['TotalBoundCount'] = v6total_bound_count
                                        #             port_devc_v6details[pkey][device_name]['CurrentBoundCount'] = v6current_bound_count
                                        #             v6_dev_count = device_details[device_name]['DeviceCount']
                                        #             log.info("TGEN:IPV6: DHCP Device: %s - total configured %s,total bound %s,current bound %s" % (device_name,v6_dev_count,v6total_bound_count,v6current_bound_count))
                                        #             if (self.param.command_action == 'release' and int(v6current_bound_count) != 0) or \
                                        #                (self.param.command_action != 'release' and v6_dev_count != v6current_bound_count):
                                        #             # if v6_dev_count != v6current_bound_count:
                                        #                 #debug @ http error
                                        #                 try:
                                        #                     log.info("Performing v6 PPPOE %s" %(self.param.command_action))
                                        #                     # if (int(churn_iter/2)) == 2:
                                        #                     #     self.GoHereOnError(tgn_device)
                                        #                     tgn_device.perform_dhcpv6_command(router_id=device_name, command_action=self.param.command_action)
                                        #                     # if stop_on_fail:
                                        #                     #     import pdb; pdb.set_trace()
                                        #                     remove_v6_device = False
                                        #                 except Exception as err:
                                        #                     log.fail("Failed to {} the session - {}".format(self.param.command_action, str(err)))
                                        #                     if (int(churn_iter/2)) == 2:
                                        #                         self.GoHereOnError(tgn_device)
                                        #                     #spm
                                        #                     # import pdb; pdb.set_trace()
                                        #             elif (self.param.command_action == 'release' and int(v6current_bound_count) == 0) or \
                                        #                (self.param.command_action != 'release' and v6_dev_count == v6current_bound_count):
                                        #                 remove_v6_device = True
                                        #                 # import pdb; pdb.set_trace()
                                        #                 # if device_name not in list_to_remove:
                                        #                 #     list_to_remove.append(device_name)
                                        #                 if (self.param.command_action == 'release'):
                                        #                     log.info("TGEN:IPV6: DHCP Device: %s - After DHCP %s - current bound is equal to %s"  % (device_name,self.param.command_action,v6current_bound_count))
                                        #                     # cumulative_port_bound_countv6 -=int(v6current_bound_count)
                                        #                 elif (self.param.command_action != 'release'):
                                        #                     log.info("TGEN:IPV6: DHCP Device: %s - After DHCP %s - configured session count %s is equal to current bound %s"  % (device_name,self.param.command_action,v6_dev_count,v6current_bound_count))
                                        #                     # cumulative_port_bound_countv6 +=int(v6current_bound_count)
                                        # time.sleep(5)
                                        if remove_v4_device and remove_v6_device:
                                            # if device_name not in list_to_remove:
                                            # log.info("#301#"*10)
                                            #mara 3
                                            # import pdb; pdb.set_trace()
                                            if device_name not in remove_port_devc_v4devices[pkey]:
                                                # list_to_remove.append(device_name)
                                                #port chk
                                                remove_port_devc_v4devices[pkey].append(device_name)
                                                
                                            if (self.param.command_action != 'disconnect'):
                                                cumulative_port_bound_countv4 +=int(v4current_bound_count)
                                                cumulative_port_bound_countv6 +=int(v6current_bound_count)
                                                total_bound_countv4 +=int(v4current_bound_count)
                                                total_bound_countv6 +=int(v6current_bound_count) 
                                                device_cntr_port += 1
                                            elif (self.param.command_action == 'disconnect'):
                                                cumulative_port_bound_countv4 -=int(v4_dev_count)
                                                cumulative_port_bound_countv6 -=int(v6_dev_count)
                                                total_bound_countv4 -=int(v4_dev_count)
                                                total_bound_countv6 -=int(v6_dev_count)
                                                device_cntr_port -= 1

                                        elif (not remove_v6_device) or (not remove_v4_device):
                                            # if device_name in list_to_remove:
                                            # log.info("#302#"*10)
                                            if device_name in remove_port_devc_v4devices[pkey]:
                                                # list_to_remove.remove(device_name)
                                                remove_port_devc_v4devices[pkey].remove(device_name)
                                        # log.info("%s DHCP Devices completed action: %s" %(len(list_to_remove),list_to_remove))  
                                        #end of if

                                        log.info("TGEN:%s PPPOE Devices completed action in port %s in this iteration %s: %s" \
                                            %(len(remove_port_devc_v4devices[pkey]),pkey, port_retry,remove_port_devc_v4devices[pkey]))
                                        if (self.param.command_action != 'disconnect'):
                                            log.info("TGEN:Total %s/%s PPPOE Devices completed action in port %s" %(device_cntr_port,len(port_devc_v4devices_org[pkey]),pkey))
                                            log.info("TGEN:PPPOE Session count of Devices completed action in port %s: %s" %(pkey,port_devc_v4count[pkey][:device_cntr_port]))
                                        #correct entries for release
                                        elif (self.param.command_action == 'disconnect'):
                                            log.info("TGEN:Total %s/%s PPPOE Devices completed action in port %s" %(device_cntr_port,len(port_devc_v4devices_org[pkey]),pkey))
                                            log.info("TGEN:PPPOE Session count of Devices completed action in port %s: %s" %(pkey,port_devc_v4count[pkey][:device_cntr_port]))
                                        # curret_port_sess_countv4 = sum(port_devc_v4count[pkey][:device_cntr_port])
                                        # curret_port_sess_countv6 = sum(port_devc_v6count[pkey][:device_cntr_port])


                                    # import pdb; pdb.set_trace() 
                                    
                                    # log.info("122 END OF iter2+ else")
                                    #else end
                                    #port by port dev count
                                #correct entries for release    
                                log.info("TGEN:Total devices in port %s completed action %s: %s, Total bound count: %s " %(pkey,self.param.command_action,device_cntr_port,cumulative_port_bound_countv4))
                                if cumulative_port_bound_countv4 != cumulative_port_bound_countv6:
                                        log.info("TGEN:Total v4 and v6 device bound count are different, v4: %s, v6 %s" %(cumulative_port_bound_countv4,cumulative_port_bound_countv6))
                                if (self.param.command_action != 'disconnect'):
                                    if (total_dev_count_portv4[pkey] == cumulative_port_bound_countv4) and \
                                       (total_dev_count_portv6[pkey] == cumulative_port_bound_countv6):
                                           if not current_port_action_complete:
                                               completed_portv4_count+=int(total_dev_count_portv4[pkey])
                                               completed_portv6_count+=int(total_dev_count_portv6[pkey])
                                           #mara to add check for v4 v6
                                           log.info("TGEN:All devices in port %s are %s, Total bound count: %s, \n \
                                            Cumulative Bound count in all ports %s" %(pkey,self.param.command_action,cumulative_port_bound_countv4,completed_portv4_count))
                                           current_port_action_complete = True
                                           check_only_router = True
                                    # if not current_port_action_complete:       
                                elif (self.param.command_action == 'disconnect'):
                                    if (cumulative_port_bound_countv4 == 0) and \
                                       (cumulative_port_bound_countv6 == 0):
                                           #mara 3
                                           # import pdb; pdb.set_trace()
                                           if not current_port_action_complete:
                                               completed_portv4_count-=int(total_dev_count_portv4[pkey])
                                               completed_portv6_count-=int(total_dev_count_portv4[pkey])
                                           log.info("TGEN:All devices in port %s are %s, Total bound count: %s, \n \
                                            Cumulative Bound count in all ports %s" %(pkey,self.param.command_action,cumulative_port_bound_countv4,completed_portv4_count))
                                           current_port_action_complete = True
                                           check_only_router = True

                            # moved inside the for loop for verifying the dual-up sessions for each device
                            log.info("123 start for ")
                            in_progress_tmr = 20
                            total_in_progress = 1
                            for wait_tmr in range(1,in_progress_tmr):
                                if current_port_action_complete and check_only_router:
                                    #mara 4
                                    # import pdb; pdb.set_trace()
                                    log.info("checking only router, All actions completed in TGEN for port %s" %pkey)
                                elif ((wait_tmr != 1) and (int(total_in_progress) == 0) or ((wait_tmr != 1) and current_port_action_complete)):
                                    break
                                elif (int(total_in_progress) != 0):
                                    log.info("Waiting for the 'in progress' sessions to be zero")
                                    # if stop_on_fail:
                                    #     import pdb; pdb.set_trace()
                                    time.sleep(30)
                                for dev_v in self.param.dut_verify:
                                #     device = self.get_device_obj(dev_v)
                                #     conn = self.get_connection(device_name=dev_v)
                                #     dev_bng_obj = Bng(device = conn.device, name='bng', mode=conn.mode)
                                #     #device.connect(self.param.dev_handle, **self.param.dev_kwargs)
                                #     expected_sub_count = dev_bng_obj.PbngSubscriberSummary(session_counts_type=l_session_count)
                                #     if self.param.cmd_filter == "dummy":
                                #         self.param.cmd_filter = None
                                #     key=["session_counts_type"]
                                #     #bng_verify = dev_bng_obj.verify_subscriber_summary(expected_sub_count, self.param.mode, self.param.cmd_filter, self.param.filter_value, self.param.filter_type, self.param.outer_vlan_id, self.param.inner_vlan_id, self.param.location,key=key)
                                #     sub_data = []
                                #     sub_data =  dev_bng_obj.get_subscriber_summary(self.param.mode, self.param.cmd_filter, self.param.filter_value, \
                                #         self.param.filter_type, self.param.outer_vlan_id, self.param.inner_vlan_id, self.param.location, self.param.output_from_file)
                                #     log.info("Total Sessions to be made up: %s" % (l_session_count))
                                #     for data_v in range(len(sub_data)):
                                #         #mara 3
                                #         # import pdb; pdb.set_trace()
                                #         if sub_data[data_v].type == "Total":
                                #             total_sub_up_1 = sub_data[data_v].ipsub_dhcp
                                #             log.info("DEVICE:Total %s/%s DHCP Subscribers are up" % (total_sub_up_1, l_session_count))
                                #             continue
                                #             # log.info(dir(sub_data[data_v]))
                                #         if sub_data[data_v].type == "dual-up":
                                #             total_sub_up_dual = sub_data[data_v].ipsub_dhcp
                                #             log.info("DEVICE:%s Dual Stack DHCP Subscribers are up" % (total_sub_up_dual))
                                #             continue
                                #         if sub_data[data_v].type == "ipv4-only":
                                #             total_sub_up_v4 = sub_data[data_v].ipsub_dhcp
                                #             log.info("DEVICE:%s IPV4 DHCP Subscribers are up" % (total_sub_up_v4))
                                #             continue
                                #         if sub_data[data_v].type == "ipv6-only":
                                #             total_sub_up_v6 = sub_data[data_v].ipsub_dhcp
                                #             log.info("DEVICE:%s IPV6 DHCP Subscribers are up" % (total_sub_up_v6))
                                #             continue
                                #         if sub_data[data_v].type == "in progress":
                                #             total_in_progress = sub_data[data_v].ipsub_dhcp
                                #             log.info("DEVICE:%s DHCP In Progress" % (total_in_progress))
                                #             continue
                                #         # log.info("124 ab end OF for datav")
                                    ##################################
                                    # if self.param.command_action != 'disconnect':
                                    #     return_dhcp_cps = self.get_dhcp_cps(dev_v,total_dev_count_portv4,pkey)
                                    return_bng_dict = self.get_pppoe_session_details(dev_v)
                                    total_sub_up_dual = return_bng_dict['total_sub_up_dual']
                                    total_sub_up_v4 = return_bng_dict['total_sub_up_v4']
                                    total_sub_up_v6 = return_bng_dict['total_sub_up_v6']
                                    total_in_progress = return_bng_dict['total_in_progress']
                                    total_sub_up_1 = return_bng_dict['total_sub_up_1']
                                    # import pdb; pdb.set_trace()


                                    ###################################end of bng subscriver summ
                                    
                                    # import pdb; pdb.set_trace()
                                    if (int(total_sub_up_1) == int(l_session_count)) or (int(total_sub_up_1) >= int(final_session_count)) \
                                    or (int(cumulative_port_bound_countv4) >= session_count_port) or (completed_portv4_count == int(total_sub_up_1)):                  
                                        total_up = True
                                        log.info("DEVICE:%s/%s Total PPPOE Subscribers are up" % (total_sub_up_1,l_session_count))
                                        #mara 3
                                        # import pdb; pdb.set_trace()
                                        if self.param.filter_type == "dual":
                                            if current_port_action_complete or (int(device_cntr_port) == int(len(port_devc_v4devices_org[pkey]))):
                                                # if total_dev_count_portv4[pkey] == int(total_sub_up_dual):
                                                if total_bound_countv4 == int(total_sub_up_dual):
                                                    log.info("DEVICE:Total bound count in Device %s completed action %s: %s " %(dev_v,self.param.command_action,total_dev_count_portv4[pkey]))
                                                    log.info("DEVICE:All %s Sessions in port %s completed action %s: %s " %(total_dev_count_portv4[pkey],pkey,self.param.command_action,device_cntr_port))
                                                else:
                                                    log.info("DEVICE:Total bound count in Device %s completed action %s: %s " %(dev_v,self.param.command_action,total_dev_count_portv4[pkey]))
                                                    log.info("DEVICE:All %s Sessions in port %s completed action %s: %s " %(total_dev_count_portv4[pkey],pkey,self.param.command_action,device_cntr_port))
                                                #port level check
                                                if int(total_sub_up_dual) == completed_portv4_count:
                                                    # import pdb; pdb.set_trace()
                                                    # if check_only_router:
                                                    log.info("DEVICE: Verify Sessions in Router Passed")
                                                    check_only_router = False
                                                    quit_port_loop = True
                                                    # if self.param.command_action == 'disconnect':
                                                    #     pppoe_sub_down = True
                                                    # else:
                                                    #     pppoe_sub_up = True
                                                    # break
                                                    #exit port loop                                                    
                                            elif (self.param.tolerance != 0) and (current_port_action_complete or (int(cumulative_port_bound_countv4) >= session_count_port)):
                                                log.info("DEVICE:Tolerance %s, Port %s Tolerance value: %s, Session count Threshold: %s" %(self.param.tolerance,pkey,tolerance_value_port,session_count_port))
                                                log.info("DEVICE:Total bound count in Device %s completed action %s: %s " %(dev_v,self.param.command_action,total_dev_count_portv4[pkey]))
                                                log.info("DEVICE:All %s Sessions in port %s completed action %s: %s " %(total_dev_count_portv4[pkey],pkey,self.param.command_action,device_cntr_port))
                                                if check_only_router:
                                                    log.info("Check only Router Passed")
                                                    check_only_router = False
                                                    quit_port_loop = True

                                        
                                            if self.param.command_action != 'disconnect':
                                                if (int(total_sub_up_1) == int(l_session_count)) and (int(total_sub_up_dual) == int(l_session_count)) \
                                                and (int(total_sub_up_v4) == 0) and (int(total_sub_up_v6) == 0 ):
                                                    # pppoe_sub_up = True
                                                    # if self.param.command_action == 'disconnect':
                                                    #     pppoe_sub_down = True
                                                    # else:
                                                    pppoe_sub_up = True
                                                    port_retry = max_retries 
                                                    log.info("DEVICE:%s/%s Total and Dual Stack PPPOE Subscribers are up, STOP iteration" % (total_sub_up_1,l_session_count))
                                                    break
                                                elif (self.param.tolerance != 0) and (int(total_sub_up_1) >= final_session_count):
                                                    # if self.param.command_action == 'disconnect':
                                                    #     pppoe_sub_down = True
                                                    # else:
                                                    pppoe_sub_up = True
                                                    port_retry = max_retries
                                                    log.info("DEVICE:Tolerance %s, Tolerance value: %s, Session count Threshold/Total Session: %s/%s" %(self.param.tolerance,tolerance_value,final_session_count,l_session_count))
                                                    break
                                            elif self.param.command_action == 'disconnect':
                                                if (int(total_sub_up_1) == int(l_session_count)) and (int(total_sub_up_dual) == int(l_session_count)) \
                                                and (int(total_sub_up_v4) == 0) and (int(total_sub_up_v6) == 0 ):
                                                    # pppoe_sub_up = True
                                                    # if self.param.command_action == 'disconnect':
                                                    pppoe_sub_down = True
                                                    # else:
                                                    #     pppoe_sub_up = True
                                                    port_retry = max_retries 
                                                    log.info("DEVICE:%s/%s Total and Dual Stack PPPOE Subscribers are up, STOP iteration" % (total_sub_up_1,l_session_count))
                                                    break
                                                elif (self.param.tolerance != 0) and (int(total_sub_up_1) <= tol_total_count):
                                                    #session count must b just tolearnce value
                                                    # if self.param.command_action == 'disconnect':
                                                    pppoe_sub_down = True
                                                    # else:
                                                    #     pppoe_sub_up = True
                                                    port_retry = max_retries
                                                    log.info("DEVICE:Tolerance %s, Tolerance value: %s, Session count Threshold/Total Session: %s/%s" %(self.param.tolerance,tolerance_value,tol_total_count,l_session_count))
                                                    break
                                        elif (self.param.filter_type == "v4"):
                                            if (int(total_sub_up_1) == int(l_session_count)) and (int(total_sub_up_v4) == int(l_session_count)) \
                                            and (int(total_sub_up_dual) == 0) and (int(total_sub_up_v6) == 0 ):
                                                log.info("DEVICE:%s/%s Total and v4 only PPPOE Subscribers are up, STOP iteration" % (total_sub_up_1,l_session_count))
                                                # pppoe_sub_up = True
                                                if self.param.command_action == 'disconnect':
                                                    pppoe_sub_down = True
                                                else:
                                                    pppoe_sub_up = True
                                                port_retry = max_retries 
                                                break
                                            # elif (self.param.tolerance != 0) and (int(cumulative_port_bound_countv4) >= session_count_port):
                                        elif (self.param.filter_type == "v6"):
                                            if (int(total_sub_up_1) == int(l_session_count)) and (int(total_sub_up_v6) == int(l_session_count)) \
                                            and (int(total_sub_up_dual) == 0) and (int(total_sub_up_v4) == 0 ):
                                                log.info("DEVICE:%s/%s Total and v6 only PPPOE Subscribers are up, STOP iteration" % (total_sub_up_1,l_session_count))
                                                
                                                if self.param.command_action == 'disconnect':
                                                    pppoe_sub_down = True
                                                else:
                                                    pppoe_sub_up = True
                                                port_retry = max_retries 
                                                break

                            
                            
                            # log.info("123 ab end OF dutverify if")
                            #mara 3
                            # import pdb; pdb.set_trace()
                            if self.param.tolerance != 0:
                                if (int(total_sub_up_1) >= int(final_session_count)):
                                    log.info("DEVICE:Tolerance %s, Tolerance value: %s, Session count Threshold/Total Session: %s/%s" %(self.param.tolerance,tolerance_value,final_session_count,l_session_count))
                                    log.info("DEVICE:%s/%s Total PPPOE Subscribers are up, checking v4 v6 Subscribers" % (total_sub_up_1,final_session_count))
                                else:
                                    log.info("DEVICE:Only %s/%s Total PPPOE Subscribers are up, continue iteration" % (total_sub_up_1,final_session_count))
                                    if self.param.filter_type == "dual":
                                        log.info("DEVICE:Only %s/%s DUAL STACK PPPOE Subscribers are up, continue iteration" % (total_sub_up_dual,l_session_count))
                                    elif (self.param.filter_type == "v4"):
                                        log.info("DEVICE:Only %s/%s v4 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v4,l_session_count))
                                    elif (self.param.filter_type == "v6"):
                                        log.info("DEVICE:Only %s/%s v6 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v6,l_session_count))
                            else:
                                if (int(total_sub_up_1) == int(l_session_count)):
                                    log.info("DEVICE:%s/%s Total PPPOE Subscribers are up, checking v4 v6 Subscribers" % (total_sub_up_1,l_session_count))
                                elif (int(total_sub_up_1) != int(l_session_count)):
                                    log.info("DEVICE:Only %s/%s Total PPPOE Subscribers are up, continue iteration" % (total_sub_up_1,l_session_count))
                                    if self.param.filter_type == "dual":
                                        log.info("DEVICE:Only %s/%s DUAL STACK PPPOE Subscribers are up, continue iteration" % (total_sub_up_dual,l_session_count))
                                    elif (self.param.filter_type == "v4"):
                                        log.info("DEVICE:Only %s/%s v4 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v4,l_session_count))
                                    elif (self.param.filter_type == "v6"):
                                        log.info("DEVICE:Only %s/%s v6 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v6,l_session_count))
                                
                            if self.param.filter_type == "dual":
                                log.info("DEVICE:Only %s/%s DUAL STACK PPPOE Subscribers are up, continue iteration" % (total_sub_up_dual,l_session_count))
                            elif (self.param.filter_type == "v4"):
                                log.info("DEVICE:Only %s/%s v4 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v4,l_session_count))
                            elif (self.param.filter_type == "v6"):
                                log.info("DEVICE:Only %s/%s v6 PPPOE Subscribers are up, continue iteration" % (total_sub_up_v6,l_session_count))

                            #current_retry += 1              # comment this line for implementing for-loop
                            time.sleep(5)
                            # log.info("124 ab end  OF dutverfy else")
                        #end of retry loop    
                        #reconnect during disconnection
                        except Exception as err:
                            log.info("Error: {}".format(str(err)))
                            if (int(churn_iter/2)) == 2:
                                self.GoHereOnError(tgn_device)
                            #spm
                            # import pdb; pdb.set_trace()
                            pass    
                        #     import pdb; pdb.set_trace()
                        #     log.info("Error: {}".format(str(err)))
                        #     # if (('timed out' in err ) or ('Lost network connection' in err)) and exception_hit_cnt != 0:
                        #     if ((re.match('.*timed out.*',str(err))) or ((re.match('.*ost network.*',str(err)))) or \
                        #         ((re.match('.*reconnect.*',str(err))))) and exception_hit_cnt != 0:
                        #         exception_hit_cnt -= 1
                        #         log.info("Timeout due to {}".format(str(err)))
                        #         log.info("Trying to reconnect after 3 minutes")
                        #         time.sleep(180)
                        #         tgn_device.connect_to_session(sid=None, skip_protocols=True)

                              
                    #end of port retry
            if ((self.param.command_action != 'disconnect') and (pppoe_sub_up == True)) or ((self.param.command_action == 'disconnect') and (pppoe_sub_down == True)):
                log.info("PASS: PPPOE action %s is success" % (self.param.command_action))
            else:
                log.fail("FAIL: PPPOE action %s Failed" % (self.param.command_action))
                return False
                #spm
                # import pdb; pdb.set_trace()
                # log.info("125 ab end  OF for dutvry")                
        except Exception as err:
            if log:
                log.fail("Failed to {} the session - {}".format(self.param.command_action, str(err)))
            #spm
            # import pdb; pdb.set_trace()
            return False
                
        Helper.sleep(self.param.wait_after_session, msg='Waiting after the session {}'.format(self.param.command_action))
        log.info("Disconnect TGEN")
        tgn_device._end_session(end_tcsession=False)
        return True                                                        


    def get_pppoe_session_details(self,dev_v):
        # import pdb; pdb.set_trace()
        try:
            l_session_count = self.param.session_count
            retrun_data_dict = AttrDict()
            # for dev_v in self.param.dut_verify:
            device = self.get_device_obj(dev_v)
            conn = self.get_connection(device_name=dev_v)
            dev_bng_obj = Bng(device = conn.device, name='bng', mode=conn.mode)
            #device.connect(self.param.dev_handle, **self.param.dev_kwargs)
            expected_sub_count = dev_bng_obj.PbngSubscriberSummary(session_counts_type=l_session_count)
            if self.param.cmd_filter == "dummy":
                self.param.cmd_filter = None
            key=["session_counts_type"]
            #bng_verify = dev_bng_obj.verify_subscriber_summary(expected_sub_count, self.param.mode, self.param.cmd_filter, self.param.filter_value, self.param.filter_type, self.param.outer_vlan_id, self.param.inner_vlan_id, self.param.location,key=key)
            sub_data = []

            sub_data =  dev_bng_obj.get_subscriber_summary(self.param.mode, self.param.cmd_filter, self.param.filter_value, \
                                            self.param.filter_type, self.param.outer_vlan_id, self.param.inner_vlan_id, self.param.location, self.param.output_from_file)
            log.info("Total Sessions to be made up: %s" % (l_session_count))
            for data_v in range(len(sub_data)):
                #mara 3
                # import pdb; pdb.set_trace()
                if sub_data[data_v].type == "Total":
                    total_sub_up_1 = sub_data[data_v].pppoe
                    log.info("DEVICE:Total %s/%s PPPOE Subscribers are up" % (total_sub_up_1, l_session_count))
                    retrun_data_dict['total_sub_up_1'] = total_sub_up_1
                    continue
                    # log.info(dir(sub_data[data_v]))
                if sub_data[data_v].type == "dual-up":
                    total_sub_up_dual = sub_data[data_v].pppoe
                    log.info("DEVICE:%s Dual Stack PPPOE Subscribers are up" % (total_sub_up_dual))
                    retrun_data_dict['total_sub_up_dual'] = total_sub_up_dual
                    continue
                if sub_data[data_v].type == "ipv4-only":
                    total_sub_up_v4 = sub_data[data_v].pppoe
                    log.info("DEVICE:%s IPV4 PPPOE Subscribers are up" % (total_sub_up_v4))
                    retrun_data_dict['total_sub_up_v4'] = total_sub_up_v4
                    continue
                if sub_data[data_v].type == "ipv6-only":
                    total_sub_up_v6 = sub_data[data_v].pppoe
                    log.info("DEVICE:%s IPV6 PPPOE Subscribers are up" % (total_sub_up_v6))
                    retrun_data_dict['total_sub_up_v6'] = total_sub_up_v6
                    continue
                if sub_data[data_v].type == "in progress":
                    total_in_progress = sub_data[data_v].pppoe
                    log.info("DEVICE:%s PPPOE In Progress" % (total_in_progress))
                    retrun_data_dict['total_in_progress'] = total_in_progress
                    continue
            # import pdb; pdb.set_trace()                    
            return retrun_data_dict
        except Exception as err:
            log.fail("Failed to fetch the PPPOE session details")
            return False