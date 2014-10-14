from __future__ import unicode_literals

import logging
import pykka
import alsaaudio

from mopidy import service
from sink import AlsaAudioSink

logger = logging.getLogger(__name__)

ALSA_SERVICE_NAME = 'alsa'


class AlsaDeviceManager(pykka.ThreadingActor, service.Service):
    """
    AlsaDeviceManager implements an autonomous ALSA audio device manager that
    is capable of discovering and enumerating ALSA audio devices.
    
    ..note:: Presently the available audio devices are scanned once at start-up
        only.

    The notion of 'connected' has no direct function within the device manager
    other than to set a boolean state which can be used by other extensions or
    parts of Mopidy to determine whether the audio device should be used
    for playback or not.
    """
    def __init__(self, config, core):
        super(AlsaDeviceManager, self).__init__()
        self.name = ALSA_SERVICE_NAME
        self.config = config
        self.core = core
        self._devices = {}

    @staticmethod
    def _make_device(dev):
        return { 'card': dev['name'], 'addr': dev['addr'] }

    @staticmethod
    def _audio_sink_name(address):
        return ALSA_SERVICE_NAME + ':audio:' + address

    def on_start(self):
        cards = alsaaudio.cards()
        idx = 0
        for i in cards:
            connected = self.config['alsa']['autoconnect']
            mixers = alsaaudio.mixers(idx)
            mixer = alsaaudio.Mixer(control=mixers[0], cardindex=idx)
            addr_str = mixer.cardname()
            self._devices[addr_str] = {'name':i, 'addr':addr_str,
                                       'connected': False, 'idx': idx,
                                       'mixers':mixers}
            dev = AlsaDeviceManager._make_device(self._devices[addr_str])
            service.ServiceListener.send('alsa_device_found', service=ALSA_SERVICE_NAME,
                                         device=dev)
            if (connected):
                self.connect(dev)
            idx += 1
        # Notify listeners
        self.state = service.ServiceState.SERVICE_STATE_STARTED
        service.ServiceListener.send('service_started', service=self.name)
        logger.info('AlsaDeviceManager started')

    def on_stop(self):
        for d in self._devices.keys():
            dev = self._devices.pop(d)
            service.ServiceListener.send('alsa_device_disappeared',
                                         service=ALSA_SERVICE_NAME,
                                         device=AlsaDeviceManager._make_device(dev))
        # Notify listeners
        self.state = service.ServiceState.SERVICE_STATE_STOPPED
        service.ServiceListener.send('service_stopped', service=self.name)
        logger.info('AlsaDeviceManager stopped')

    def get_devices(self):
        return map(AlsaDeviceManager._make_device, self._devices.values())

    def connect(self, dev):
        self._devices[dev['addr']]['connected'] = True
        ident = AlsaDeviceManager._audio_sink_name(dev['addr'])
        self.core.add_audio_sink(ident, AlsaAudioSink(dev['addr']))
        service.ServiceListener.send('alsa_device_connected', service=ALSA_SERVICE_NAME,
                                     device=dev)

    def disconnect(self, dev):
        self._devices[dev['addr']]['connected'] = False
        ident = AlsaDeviceManager._audio_sink_name(dev['addr'])
        self.core.remove_audio_sink(ident)
        service.ServiceListener.send('alsa_device_disconnected', service=ALSA_SERVICE_NAME,
                                     device=dev)
