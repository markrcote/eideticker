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

import BaseHTTPServer
import datetime
import json
import os
import re
import subprocess
import time

CAPTURE_DIR = 'captures'

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


class CaptureControllerHTTPServer(BaseHTTPServer.HTTPServer):

    def __init__(self, server_address, request_handler_class):
        BaseHTTPServer.HTTPServer.__init__(self, server_address,
                                           request_handler_class)
        self.pcontroller = CaptureSubprocessController()

    def get_filename(self):
        return os.path.join(CAPTURE_DIR, datetime.datetime.now().isoformat())

    def start(self):
        if self.pcontroller.running():
            return {'error': 'busy'}
        output_filename = self.get_filename()
        self.pcontroller.launch(output_filename)
        return self.status()

    def stop(self):
        if self.pcontroller.running():
            self.pcontroller.terminate()
        return self.status()

    def status(self):
        if self.pcontroller.running():
            return { 'status': 'running',
                     'output': self.pcontroller.output_filename }
        return { 'status': 'idle' }


class CaptureControllerRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    path_handlers = { '/test/': 'test',
                      '/start/': 'start',
                      '/stop/': 'stop',
                      '/status/': 'status',
                      '/captures/': 'captures' }
    
    def do_GET(self):
        code = 404
        data = None
        for path_prefix, func_name in self.path_handlers.iteritems():
            if self.path.startswith(path_prefix):
                response = getattr(self, func_name)()
                break
        if not response:
            print 'no response'
            return
        code, data = response
        self.send_response(code)
        if data != None:
            json_data = json.dumps(data)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(json_data))
            self.end_headers()
            self.wfile.write(json_data)

    def test(self):
        return (200, {'test': True})

    def start(self):
        return (200, self.server.start())

    def stop(self):
        return (200, self.server.stop())

    def status(self):
        return (200, self.server.status())

    def write_file(self, content_type, path):
        self.send_response(200)
        f = file(path, 'rb')
        self.send_header('Content-Type', '%s; name="%s"' %
                         (content_type, os.path.basename(path)))
        self.send_header('Content-Length', str(os.fstat(f.fileno()).st_size))
        self.end_headers()
        while True:
            buf = f.read(64*1024)
            if not buf:
                break
            self.wfile.write(buf)

    def capture_data(self, capture_name):
            raw_url = avi_url = imgs_url = ''
            raw_path = os.path.join(CAPTURE_DIR, capture_name + '.raw')
            if os.path.exists(raw_path):
                raw_url = '/captures/%s' % os.path.basename(raw_path)
            avi_path = os.path.join(CAPTURE_DIR, capture_name + '.avi')
            if os.path.exists(avi_path):
                avi_url = '/captures/%s' % os.path.basename(avi_path)
            imgs_path = os.path.join(CAPTURE_DIR, capture_name + '-pngs.zip')
            if os.path.exists(imgs_path):
                imgs_url = '/captures/%s' % os.path.basename(imgs_path)
            return { 'imgs': imgs_url,
                     'raw': raw_url,
                     'avi': avi_url }

    def captures(self):
        if self.path[-1] == '/':
            capture_data = {}
            if self.path == '/captures/':
                r = '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}'
                for f in os.listdir(CAPTURE_DIR):
                    m = re.match(r, f)
                    if m:
                        capture_data[m.group(0)] = self.capture_data(m.group(0))
            else:
                comps = filter(lambda x: x, self.path.split('/'))
                capture_data = self.capture_data(comps[1])
            return (200, capture_data)
        filename = os.path.basename(self.path)
        filepath = os.path.join(CAPTURE_DIR, filename)
        if not os.path.exists(filepath):
            return (404, {})
        if filename.endswith('.raw'):
            self.write_file('video/x-raw-yuv; format=UYVY', filepath)
        elif filename.endswith('.avi'):
            self.write_file('video/x-msvideo', filepath)
        elif filename.endswith('.zip'):
            self.write_file('application/zip', filepath)
        else:
            return (404, {})


def main(port):
    server = CaptureControllerHTTPServer(('', port),
                                         CaptureControllerRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    import sys
    port = 8888
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    main(port)
