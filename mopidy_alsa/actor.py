from __future__ import unicode_literals

import logging
import pykka
import alsaaudio

from mopidy import device, exceptions, models
from sink import AlsaAudioSink

logger = logging.getLogger(__name__)

ALSA_DEVICE_TYPE = 'alsa'


class AlsaDeviceManager(pykka.ThreadingActor, device.DeviceManager):
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
    def __init__(self, config, audio):
        super(AlsaDeviceManager, self).__init__()
        self.device_types = [ALSA_DEVICE_TYPE]
        self.config = config
        self.audio = audio
        self._devices = {}

    @staticmethod
    def _make_device(dev):
        caps = [device.DeviceCapability.DEVICE_AUDIO_SINK]
        return models.Device(name=dev['name'], address=dev['addr'], capabilities=caps,
                             device_type=ALSA_DEVICE_TYPE)

    @staticmethod
    def _audio_sink_name(address):
        return ALSA_DEVICE_TYPE + ':audio:' + address

    def on_start(self):
        cards = alsaaudio.cards()
        addr = 0
        for i in cards:
            connected = self.config['alsa']['autoconnect']
            addr_str = 'hw:' + str(addr)
            self._devices[addr_str] = {'name':i, 'addr':addr_str, 'connected': connected}
            device.DeviceListener.send('device_found',
                                       device=AlsaDeviceManager._make_device(self._devices[addr_str]))
            addr += 1
        logger.info('AlsaDeviceManager started')

    def on_stop(self):
        for d in self._devices.keys():
            dev = self._devices.pop(d)
            device.DeviceListener.send('device_disappeared',
                                       device=AlsaDeviceManager._make_device(dev))
        logger.info('AlsaDeviceManager stopped')

    def get_devices(self):
        return map(AlsaDeviceManager._make_device, self._devices.values())

    def enable(self):
        pass

    def disable(self):
        pass

    def connect(self, dev):
        self._devices[dev.address]['connected'] = True
        ident = AlsaDeviceManager._audio_sink_name(dev.address)
        self.audio.add_sink(ident, AlsaAudioSink(dev.address))
        device.DeviceListener.send('device_connected', device=dev)

    def disconnect(self, dev):
        self._devices[dev.address]['connected'] = False
        ident = AlsaDeviceManager._audio_sink_name(dev.address)
        self.audio.remove_sink(ident)
        device.DeviceListener.send('device_disconnected', device=dev)

    def pair(self, dev):
        raise exceptions.ExtensionError('Pairing not supported')

    def remove(self, dev):
        raise exceptions.ExtensionError('Pairing not supported')

    def is_connected(self, dev):
        return self._devices[dev.address]['connected']

    def is_paired(self, dev):
        raise exceptions.ExtensionError('Pairing not supported')

    def set_property(self, dev, name, value):
        raise exceptions.ExtensionError('Properties not supported')

    def get_property(self, dev, name=None):
        raise exceptions.ExtensionError('Properties not supported')

    def has_property(self, dev, name):
        raise exceptions.ExtensionError('Properties not supported')
