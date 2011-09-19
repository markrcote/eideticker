Project Eideticker
==================

Project Eideticker is an automated test harness that captures and analyzes
browser output.

Required for capturing is a Linux system with a Blackmagic Design DeckLink card
and the appropriate drivers.  Testing has been done with the DeckLink HD
Extreme 3D; no idea if other cards would work.

Capture
-------

### Installation

Simply run `make` in the `capture/decklink/` directory to compile the C++
capture app.


### Usage

Run `./controller.py <port>` from within the `capture/` directory.  The default
port is 8888.

The capture device is controlled through a web interface.  These command paths
are support:

* `/start/`  Start recording.
* `/stop/`   Stop recording and run the conversion script on the raw output.
* `/status/` Indicates if a job is running, and, if so, the name of the capture.
* `/captures/` Returns a JSON dictionary of the currently stored captures along
               with URLs to the individual data files (raw video, avi, png
               archive).
* `/captures/<timestamp>/` Returns a JSON dictionary of the URLs to the
                           individual data files for the given capture.
* `/captures/<timestamp>/<filename>` Access the raw video, avi, or png archive 
                                     of the given capture.

### To Do

* More configuration options (command line and/or config file).
* Packaging.
* Logging.
* Verify if the Capture program has been compiled.
