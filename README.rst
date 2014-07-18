****************************
Mopidy-Alsa
****************************

.. image:: https://pypip.in/version/Mopidy-Alsa/badge.png?latest
    :target: https://pypi.python.org/pypi/Mopidy-Alsa/
    :alt: Latest PyPI version

.. image:: https://pypip.in/download/Mopidy-Alsa/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Alsa/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/liamw9534/mopidy-Alsa.png?branch=master
    :target: https://travis-ci.org/liamw9534/mopidy-Alsa
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/liamw9534/mopidy-Alsa/badge.png?branch=master
   :target: https://coveralls.io/r/liamw9534/mopidy-Alsa?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for ALSA audio device management.

Installation
============

Install by running::

    pip install Mopidy-Alsa

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Extension
---------

Add the following section to your Mopidy configuration file following installation:

	[alsa]
	enabled = true
	autoconnect = true

The 'autoconnect' setting will automatically connect detected audio sinks to mopidy if set true.
Otherwise, the connection is left for the user to establish via mopidy HTTP device API.


Project resources
=================

- `Source code <https://github.com/liamw9534/mopidy-Alsa>`_
- `Issue tracker <https://github.com/liamw9534/mopidy-Alsa/issues>`_
- `Download development snapshot <https://github.com/liamw9534/mopidy-Alsa/archive/master.tar.gz#egg=mopidy-evtdev-dev>`_


Changelog
=========


v0.1.0
----------------------------------------

- Initial release.
