'''
Created on 18/09/2013

@author: Lenneke Jong
'''

from subprocess import call, Popen, PIPE, STDOUT
from string import Template
import sys,traceback
import logging
import re


class OutputParser(object):
    '''
    Parses the output from the shelx programs from 
    '''
    shelxc_stats_prefixes=re.compile(" (?P<prefix>Resl\.|N\(data\)|\<I\/sig\>|\%Complete|\<d\/sig\>).+")
    
    def __init__(self):
        '''
        Constructor
        '''
        self.shelxc_stats={}

        
    def setOutfile(self,logfilename):
        self.logfile=open(logfilename,'w') 
     
    def read(self, pipe):
        """read 
        """
        self.outputstring=pipe
        self.logfile.write(pipe)
        
    def parse_shelxc_out(self):
        #search through the output string for the stats table, creates a dict with the lines and all the values
        for line in self.outputstring.split('\n'):
            m=re.match(self.shelxc_stats_prefixes,line)
            if m:
                self.shelxc_stats[m.group('prefix')]=line.split()[1:]
            else:
                pass
        print self.shelxc_stats
        #what else should we do with them... 
        
    def parse_shelxd_out(self):
        pass
    
    def parse_shelxe_out(self):
        pass