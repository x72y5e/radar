# radar
Display flight tracks on the UnicornHatHD module for Raspberry Pi.

This will run without the UnicornHatHD module, but will simply print information to the console.

Dependencies: numpy, requests (UnicornHatHD and associated python module).

Not tested for python 2.

Run the tracker.py module. This will load data from config.json, which by default is configured to the area around London Heathrow. Alternative coordinates for the map, tracking range, and any fixed points you wish to display can be specified in config.json.

Acknowledgments: the Kalman Filter code is not currently used but is included in the module for future reference and in case anyone wants to get it working properly. The present code is adapted from the examples at http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
