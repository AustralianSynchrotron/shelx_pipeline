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
     #shelxd output lines of this format
     #Try     28, CPU 1, CC All/Weak 49.4 / 31.2, CFOM 80.7, best 80.7, PATFOM  34.1
    shelxd_stats_prefixes=re.compile("(?P<key>[a-zA-Z\/]*)\s+(?P<val>\d+\.?\d*(?:\s\/\s\d+\.?\d*)?)")
    shelxe_stats_prefixes=re.compile("(?P<key>[a-zA-Z\<\>]*)\.?\s+=?\s*(?P<val>\d+$|\d+\.\d+)")
        
    def __init__(self):
        '''
        Constructor
        '''
        self.shelxc_stats={}
        self.shelxd_stats={}
        self.shelxe_stats={"Contrast":[],"Cycle":[]}
        self.shelxei_stats={"Contrast":[],"Cycle":[]}
        
    def setOutfile(self,logfilename):
        self.logfile=open(logfilename,'w') 
     
    def read(self, pipe):
        """read 
        """
        self.outputstring=pipe
        self.logfile.write(pipe)
        
    def clean(self):
        """clean up all that stuff
        """
        self.outputstring=None
        

    def parse_shelxc_out(self):
        #search through the output string for the stats table, creates a dict with the lines and all the values
        for line in self.outputstring.split('\n'):
            m=re.match(self.shelxc_stats_prefixes,line)
            if m:
                results=[float(r) for r in line.split()[1:] if r!='Inf.']
                self.shelxc_stats[m.group('prefix')]=results
            else:
                pass
        #what else should we do with them... 
        return self.shelxc_stats
        
    def parse_shelxd_out(self):
        #search through the output string for the stats table, creates a dict with the lines and all the values
        for line in self.outputstring.split('\n'):
            m=re.match('^ Try.+',line)
            if m:
                m=re.findall(self.shelxd_stats_prefixes,line)
                if m:
                    results=dict((k,v) for k,v in m) 
                     # now fix the all/weak key and split it
                    ccallweak=results['All/Weak'].split('/')
                    ccall=ccallweak[0]
                    ccweak=ccallweak[1] #special case
                    results['CCall']=ccall
                    results['CCweak']=ccweak
                    del results['All/Weak']
                    for key,val in results.iteritems():
                        if not key in self.shelxd_stats:
                            self.shelxd_stats[key]=[float(val)]
                        else:
                            self.shelxd_stats[key].append(float(val))
                else:
                    pass
            else:

                pass
        #what else should we do with them... 
        return self.shelxd_stats
    
    def parse_shelxe_out(self,inverted):
        #search through the output string for the stats table, creates a dict with the lines and all the values
        for line in self.outputstring.split('\n'):
            m=re.findall(self.shelxe_stats_prefixes,line)
            if m and len(m)==4:
                results=dict((k,v) for k,v in m)
                for key,val in results.iteritems():
                    if inverted:
                        for key,val in results.iteritems():
                            if not key in self.shelxei_stats:
                                self.shelxei_stats[key]=[float(val)]
                            else:
                                self.shelxei_stats[key].append(float(val)) 
                    else:
                        for key,val in results.iteritems():
                            if not key in self.shelxe_stats:
                                self.shelxe_stats[key]=[float(val)]
                            else:
                                self.shelxe_stats[key].append(float(val)) 
            else:
                pass
        #what else should we do with them... 
        if not inverted:
            return self.shelxe_stats
        else:
            return self.shelxei_stats
