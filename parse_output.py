'''
Created on 18/09/2013

@author: Lenneke Jong
'''

from subprocess import call, Popen, PIPE, STDOUT
from string import Template
import sys,traceback
import logging


class OutputParser(object):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
     
    def setOutfile(self,logfilename):
        self.logfile=open(logfilename,'w') 
     
    def read(self, pipe):
        """read 
        """
        print pipe
        self.logfile.write(pipe)