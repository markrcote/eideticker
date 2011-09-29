#!/usr/bin/python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Eideticker.
#
# The Initial Developer of the Original Code is
# Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Mark Cote <mcote@mozilla.com>
#   William Lachance <wlachance@mozilla.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

import subprocess
import time

class CaptureSubprocessController(object):

    def __init__(self):
        self.capture_proc = None
        self.null_read = file('/dev/null', 'r')
        self.null_write = file('/dev/null', 'w')
        self.output_filename = ''

    def launch(self, output_filename):
        print 'launch requested'
        if self.capture_proc:
            print 'capture already running'
            return
        print 'launching'
        self.output_filename = output_filename
        args = ('decklink/Capture',
                '-m',
                '13',
                '-p',
                '0',
                '-f',
                self.output_filename + '.raw')
        self.capture_proc = subprocess.Popen(args, close_fds=True)

    def running(self):
        if not self.capture_proc:
            return False
        running = self.capture_proc.poll()
        if running != None:
            self.capture_proc = None
        return running == None

    def terminate(self):
        print 'terminate requested'
        if not self.capture_proc:
            print 'not running'
            return

        print 'terminating...'
        self.capture_proc.terminate()
        for i in range(0, 5):
            rc = self.capture_proc.poll()
            print 'rc: %s' % str(rc)
            if rc != None:
                print 'terminated'
                self.capture_proc.wait()  # necessary?
                self.capture_proc = None
                break
            time.sleep(1)
        if self.capture_proc:
            print 'still running!'
            # terminate failed; try forcibly killing it
            try:
                self.capture_proc.kill()
            except:
                pass
            self.capture_proc.wait()  # or poll and error out if still running?
            self.capture_proc = None

        print 'converting'
        # convert raw file
        # if this is too slow, we'll have to make this asynchronous and
        # have multiple states
        args = ('decklink/convert.sh', self.output_filename)
        subprocess.Popen(args, close_fds=True).wait()
