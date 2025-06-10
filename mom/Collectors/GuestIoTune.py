
import copy
from mom.Collectors.Collector import *

class GuestIoTune(Collector):
    """
    This Collector uses hypervisor interface to collect guest IO tune info
    """

    class IoTune:
        class IoTuneVals:
            def __init__(self, vals):
                self.vals = vals

            def __getattr__(self, item):
                try:
                    return self.vals[item]
                except KeyError as k:
                    raise AttributeError from k


        def __init__(self, name, path, guaranteed, maximum, current):
            self.name = name
            self.path = path
            self.guaranteed = self.IoTuneVals(guaranteed)
            self.maximum = self.IoTuneVals(maximum)
            self.current = self.IoTuneVals(current)

        def ioTune(self):
            return {'name': self.name, 'path':self.path, 'ioTune':self.current.vals}

        def setTotalBytesSec(self, val):
            self.current.vals['total_bytes_sec'] = int_or_none(val)

        def setReadBytesSec(self, val):
            self.current.vals['read_bytes_sec'] = int_or_none(val)

        def setWriteBytesSec(self, val):
            self.current.vals['write_bytes_sec'] = int_or_none(val)

        def setTotalIopsSec(self, val):
            self.current.vals['total_iops_sec'] = int_or_none(val)

        def setReadIopsSec(self, val):
            self.current.vals['read_iops_sec'] = int_or_none(val)

        def setWriteIopsSec(self, val):
            self.current.vals['write_iops_sec'] = int_or_none(val)


    def __init__(self, properties):
        self.hypervisor_iface = properties['hypervisor_iface']
        self.uuid = properties['uuid']
        self.logger = logging.getLogger('mom.Collectors.IoTuneInfo')
        self.info_available = True

    def getFields(self):
        return {'io_tune', 'io_tune_current'}

    def stats_error(self, msg):
        if self.info_available:
            self.logger.debug(msg)
        self.info_available = False

    def collect(self):
        policy_list = self.hypervisor_iface.getVmIoTunePolicy(self.uuid)
        if not policy_list:
            self.stats_error('getVmIoTunePolicy() is not ready')
            return None

        # Ignore IoTune when the current status list is empty
        state_list = self.hypervisor_iface.getVmIoTune(self.uuid)
        if not state_list:
            self.stats_error('getVmIoTune() is not ready')
            return None

        self.info_available = True

        current_list = []
        res_list = []

        def findState(name, path):
            for state in state_list:
                s_path = state.get('path')
                if path == s_path:
                    return state

                if (path is None or s_path is None) and (name == state.get('name')):
                    return state

            return None

        for policy_limits in policy_list:
            name = policy_limits.get('name')
            path = policy_limits.get('path')
            state = findState(name, path)

            # Ignore policy if device does not exist
            if state is None:
                continue

            res_list.append(self.IoTune(
                state['name'],
                state['path'],
                policy_limits['guaranteed'],
                policy_limits['maximum'],
                state['ioTune']))

            current_list.append(copy.deepcopy(state))

        return {'io_tune': res_list, 'io_tune_current': current_list}


def int_or_none(val):
    """
    Casts a value to an integer if it is not None, otherwise returns None.
    """
    return int(val) if val is not None else None
