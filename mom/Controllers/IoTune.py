
import logging

class IoTune:
    """
    Controller that uses the hypervisor interface to manipulate
    the IO tuning parameters
    """

    def __init__(self, properties):
        self.hypervisor_iface = properties['hypervisor_iface']
        self.logger = logging.getLogger('mom.Controllers.IoTune')

    def process_guest(self, guest):
        io_tune = guest.io_tune
        io_tune_prev = guest.io_tune_current

        if not io_tune or not io_tune_prev:
            return

        changed_list = []
        for i, io_t in enumerate(io_tune):
            tune = io_t.ioTune()
            tune_prev = io_tune_prev[i]

            # nothing changed
            if tune['ioTune'] == tune_prev['ioTune']:
                continue

            changed_list.append(tune)

        uuid = guest.Prop('uuid')
        name = guest.Prop('name')
        if changed_list:
            self.hypervisor_iface.setVmIoTune(uuid, changed_list)

    def process(self, host, guests):
        for guest in guests:
            self.process_guest(guest)
