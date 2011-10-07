Project Eideticker
==================

Project Eideticker is an automated test harness that captures and analyzes
browser output (currently only on Fennec on Android, but support for other
platforms is planned).

### Requirements

* Linux system with zip and ffmpeg installed.

* Blackmagic Design DeckLink card and the appropriate drivers.

 * Testing has been done with the DeckLink HD Extreme 3D; no idea if other
   cards would work.


### Installation

Run `bootstrap.sh` in the root directory to set everything up.

### Usage

Eideticker is currently only tested with the Galaxy S-2 phone, running
Android 2.2 and rooted. Assuming this is your configuration, you should be
able to get Eideticker running by install SUTAgent on your phone and issuing
the following commands:

    ./bin/setup-talos.sh <ip address of phone> \
                         <address of a checkout of talos on your web server> \
                         <name of fennec application to test>

For example, my workstation is on 192.168.1.2, I've bindmounted talos's
directory to a subdirectory on my workstation, I've built a custom version
of fennec with the name org.mozilla.fennec_wlach, and my phone has an ip
address of 192.168.1.4. I'd thus run setup-talos.sh as follows:

    ./bin/setup-talos.sh 192.168.1.4 192.168.1.2/talos org.mozilla.fennec_wlach

Once you've configured talos, you can run it with a single command:

    ./bin/run-talos.sh

You should then have a bunch of capture data stored in `src/talos/captures`.
Currently we just run the ts test (not very interesting), more useful tests
planned!
