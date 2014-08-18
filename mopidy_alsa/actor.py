from __future__ import unicode_literals

import logging
import pykka
import alsaaudio

from mopidy import device, models
from sink import AlsaAudioSink

logger = logging.getLogger(__name__)

ALSA_SERVICE_NAME = 'alsa'


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
        self.name = ALSA_SERVICE_NAME
        self.config = config
        self.audio = audio
        self._devices = {}

    @staticmethod
    def _make_device(dev):
        caps = [device.DeviceCapability.DEVICE_AUDIO_SINK]
        return models.Device(name=dev['name'], address=dev['addr'], capabilities=caps,
                             device_type=ALSA_SERVICE_NAME)

    @staticmethod
    def _audio_sink_name(address):
        return ALSA_SERVICE_NAME + ':audio:' + address

    def on_start(self):
        logger.info('AlsaDeviceManager started')
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
            device.DeviceListener.send('device_found',
                                       device=dev)
            if (connected):
                self.connect(dev)
            idx += 1

    def on_stop(self):
        for d in self._devices.keys():
            dev = self._devices.pop(d)
            device.DeviceListener.send('device_disappeared',
                                       device=AlsaDeviceManager._make_device(dev))
        logger.info('AlsaDeviceManager stopped')

    def get_devices(self):
        return map(AlsaDeviceManager._make_device, self._devices.values())

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
