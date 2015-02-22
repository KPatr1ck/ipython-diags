# ipython-diags
Updated version for OSX 

(Original file https://bitbucket.org/vladf/ipython-diags)

### HOW TO INSTALL:

FIRST YOU NEED TO INSTALL actdiag, blockdiag, nwdiag, seqdiag:

http://blockdiag.com/en/index.html

sudo pip install actdiag

sudo pip install blockdiag

sudo pip install nwdiag

sudo pip install seqdiag


Then inside IPython:

%install_ext https://raw.githubusercontent.com/ricardodeazambuja/ipython-diags/master/diagmagic.py

and

%load_ext diagmagic

### Examples:
http://nbviewer.ipython.org/github/ricardodeazambuja/ipython-diags/blob/master/blockdiag_ipython.ipynb
