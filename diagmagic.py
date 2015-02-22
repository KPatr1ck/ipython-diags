# -*- coding: utf-8 -*-
"""
https://bitbucket.org/vladf/ipython-diags

magics for using blockdiag.com modules with IPython Notebook

The module provides magics:  %%actdiag, %%blockdiag, %%nwdiag, %%seqdiag

Sample usage (in IPython cell):

    %%blockdiag
    {
       A -> B -> C;
            B -> D;
    }

Some browsers do not properly render SVG, therefore PNG image is used by default.

Use magics %setdiagsvg and %setdiagpng to set SVG or PNG mode

PNG rendered on windows with default libraries does not support antialiasing,
resulting in a poor image quality

If inkscape is installed on the machine and can be found in system path,
the diagram is created as SVG and then rendered to PNG using inkscape.

Inkscape for windows can be downloaded from (http://inkscape.org/)


FIRST YOU NEED TO INSTALL actdiag, blockdiag, nwdiag, seqdiag:
http://blockdiag.com/en/index.html
sudo pip install actdiag
sudo pip install blockdiag
sudo pip install nwdiag
sudo pip install seqdiag


Then inside IPython:
%install_ext https://raw.githubusercontent.com/ricardodeazambuja/ipython-diags/master/diagmagic.py
%load_ext diagmagic

"""
from __future__ import print_function

import imp
import io
import os
import sys
import pipes
import subprocess
import tempfile

try:
    import hashlib
except ImportError:
    import md5 as hashlib

from IPython.core.magic import Magics, magics_class, cell_magic, line_cell_magic
from IPython.core.displaypub import publish_display_data

_draw_mode = 'SVG'
_publish_mode = 'SVG'
_size = (1000,500)


_inkscape_available = None

if os.uname()[0]=='Darwin':
    _inkscape ='/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
else:
    _inkscape ='/Applications/Inkscape.app/Contents/Resources/bin/inkscape'

@magics_class
class BlockdiagMagics(Magics):
    """Magics for blockdiag and others"""

    def _import_all(self, module):
        for k, v in module.__dict__.items():
            if not k.startswith('__'):
                self.shell.push({k:v})

    def run_command(self, args):
        try:
            startupinfo = None
            if os.name == 'nt':
                # Avoid a console window in Microsoft Windows.
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.call(args, stderr=subprocess.STDOUT,
                                  startupinfo=startupinfo)
            return True

        except subprocess.CalledProcessError as e:
            print(e.output, file=sys.stderr)
            print("ERROR: command `%s` failed\n%s" %
                      ' '.join(map(pipes.quote, e.cmd)),
                      file=sys.stderr)
        except OSError as e:
            print ('Exception %s' % str(e), file=sys.stderr)
        return False

    def inkscape_available(self):
        global _inkscape_available
        if _inkscape_available is None:
            _inkscape_available = self.run_command([_inkscape, '--export-png'])
        return _inkscape_available

    def svg2png(self, filename):
        self.run_command([_inkscape, filename + '.svg',
                '--export-png=' + filename + '.png'])

    def diag(self, line, cell, command):
        """Create sequence diagram using supplied diag methods."""
        code = cell + u'\n'

        if _publish_mode == 'PNG':
            # if inkscape is available create SVG for either case
            if self.inkscape_available():
                global _draw_mode
                _draw_mode = 'SVG'

        try:

            tmpdir = tempfile.mkdtemp()
            fd, diag_name = tempfile.mkstemp(dir=tmpdir)
            f = os.fdopen(fd, "w")
            f.write(code.encode('utf-8'))
            f.close()

            format = _draw_mode.lower()
            draw_name = diag_name + '.' + format

            saved_argv = sys.argv
            sys.argv = [command, '-T', format, '--size', str(_size[0])+'x'+str(_size[1]), '-o', draw_name, diag_name]

            # if os.path.exists(fontpath):
            #    sys.argv += ['-f', fontpath]

            # do not use PIL library when rendering to SVG
            # this allows avoid problem with handling unicode in diagram
            # if _draw_mode == 'SVG':
            #     sys.argv += ['--ignore-pil']

            # command.main(sys.argv)
            return_code = subprocess.call(sys.argv)
            sys.argv = saved_argv


            if _draw_mode == 'SVG' and _publish_mode == 'PNG':
                # render SVG with inkscape
                self.svg2png(diag_name)

            file_name = diag_name + '.' + _publish_mode.lower()
            with io.open(file_name, 'rb') as f:
                data = f.read()
                f.close()

        finally:
            for file in os.listdir(tmpdir):
                os.unlink(tmpdir + "/" + file)
            os.rmdir(tmpdir)

        if _publish_mode == 'SVG':
            publish_display_data(
                u'IPython.core.displaypub.publish_svg',
                {'image/svg+xml':data}
            )
        else:
            publish_display_data(
                u'IPython.core.displaypub.publish_png',
                {'image/png':data}
            )

    @cell_magic
    def actdiag(self, line, cell):
        # import actdiag.command
        # self.diag(line, cell, actdiag.command)
        self.diag(line, cell, 'actdiag')

    @cell_magic
    def blockdiag(self, line, cell):
        # import blockdiag.command
        # self.diag(line, cell, blockdiag.command)
        self.diag(line, cell, 'blockdiag')

    @cell_magic
    def nwdiag(self, line, cell):
        # import nwdiag.command
        # self.diag(line, cell, nwdiag.command)
        self.diag(line, cell, 'nwdiag')

    @cell_magic
    def seqdiag(self, line, cell):
        # import seqdiag.command
        # self.diag(line, cell, seqdiag.command)
        self.diag(line, cell, 'seqdiag')

    @cell_magic
    def rackdiag(self, line, cell):
        self.diag(line, cell, 'rackdiag')

    @cell_magic
    def packetdiag(self, line, cell):
        self.diag(line, cell, 'packetdiag')


    @line_cell_magic
    def setdiagsize(self, line, cell=None):
        '''
        Sets the size (in pixels)
        %setdiagsize X,Y
        '''
        global _size    
        _size = (int(line[:line.find(',')]), int(line[line.find(',')+1:]))


    @line_cell_magic
    def setdiagsvg(self, line, cell=None):
        global _draw_mode, _publish_mode
        _draw_mode = _publish_mode = 'SVG'

    @line_cell_magic
    def setdiagpng(self, line, cell=None):
        global _draw_mode, _publish_mode
        _draw_mode = _publish_mode = 'PNG'


_loaded = False

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(BlockdiagMagics)
        _loaded = True


# if __name__ == '__main__':
#     pass
#     #
#     # for testing only
#     #
#     # cell = u""" {
#     #       browser  -> webserver [label = "сигнал  GET /index.html"];
#     #       browser <-- webserver;
#     #       browser  -> webserver [label = "POST /blog/comment"];
#     #                   webserver  -> database [label = "INSERT comment"];
#     #                   webserver <-- database;
#     #       browser <-- webserver;
#     #     } 
#     # """
#     # bm = BlockdiagMagics('test')
#     # bm.seqdiag('', cell)
