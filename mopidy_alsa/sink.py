from __future__ import unicode_literals

import gobject

import pygst
pygst.require('0.10')
import gst  # noqa


class AlsaAudioSink(gst.Bin):
    def __init__(self, address):
        super(AlsaAudioSink, self).__init__()
        alsa = gst.element_factory_make('alsasink')
        alsa.set_property('device', address)
        alsa.set_property('sync', False)
        queue = gst.element_factory_make('queue')
        self.add_many(queue, alsa)
        gst.element_link_many(queue, alsa)
        pad = queue.get_pad('sink')
        ghost_pad = gst.GhostPad('sink', pad)
        self.add_pad(ghost_pad)
