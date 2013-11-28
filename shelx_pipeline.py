#! /usr/bin/env python
from subprocess import call, Popen, PIPE, STDOUT
#from beamline import variables as mxvariables
from string import Template
import sys,traceback
import logging
import tempfile
import argparse
from sets import Set
from parse_output import OutputParser
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class AutoShelx(object):
    # these defaults
    defaults={'NTRY':1000} 
    possible_params=Set({'FIND','DSUL','MIND','NTRY','SPAG','SAD','CELL'})

    def __init__(self):
        self.parser=OutputParser()
        self.input_params=self.defaults
        self.name=''
        self.outfile=''
        self.results={}

    def update_defaults(self,default_dict):
        self.defaults.update(default_dict)


    def process_args(self,cell,spag,sad,**kwargs):
        self.outfile=kwargs.get('outfile',"shelx_pipeline.out")
        self.parser.setOutfile(self.outfile)
        self.input_params.update({'CELL':cell,'SPAG':spag,'SAD':sad})
        self.input_params.update(kwargs)
        print kwargs
        print self.input_params

    def determine_heavy_atom(self):
        """Contains the logic to determine the value of SFAC"""
        pass

    def call_shelxc(self,*args,**kwargs):
        print "calling shelxc"
        # This is going to pass all the extra kwargs in as the string, so we
        # maybe need a dictionary of the possibly values and check the param is in there
        templatestring='''$key $value \n'''
        
        try:
            instring=""
            for key,value in self.input_params.iteritems():
                if key in self.possible_params:
                    instring=instring+Template(templatestring).substitute(key=key, value=value)
        
            #do more processing here with the input args, some logic checking etc
        
            p=Popen(["shelxc",self.name],stdin=PIPE,stdout=PIPE,stderr=PIPE)
            (sout,serr)=p.communicate(instring)
                # print sout
            # at the moment we're just printing out the output, but we want to capture it and parse it
            self.parser.read(sout)
            self.results['shelxc'] = self.parser.parse_shelxc_out()
        except:
            print "an error occured"
            traceback.print_exc()
            # didn't get the right parameters to make a proper input file, raise 
            # an exception
   
    def call_shelxd(self,*args,**kwargs):
        print "calling shelxd"
        infilename=self.name+'_fa'
        p=Popen(["shelxd",infilename],stdout=PIPE,stderr=PIPE)
        (sout,serr)=p.communicate()
        #call(["tee","-a",self.outfile],stdin=p.stdout)
        self.parser.read(sout)
        self.results['shelxd']=self.parser.parse_shelxd_out()

    def call_shelxe(self,*args,**kwargs):
        infilename=self.name+'_fa'
        shelxe_flags=kwargs.get('shelxe_flags',[])
        shelxe_args=['shelxe',self.name,infilename]
        inverted=False
        for a in shelxe_flags+list(args):
            shelxe_args.append(a)
        if not "-i" in shelxe_args and kwargs.get('invert',False)==True:
            shelxe_args.append("-i")
            inverted=True
        print "starting shelxe inverted="+str(inverted)
        p=Popen(shelxe_args,stdout=PIPE)
        (sout,serr)=p.communicate()
        # possible arguments are -h -s0.5 =m20 -i
       # call(["tee","-a",self.outfile],stdin=p.stdout)
        self.parser.read(sout)
        if inverted:
            self.results['shelxe_inverted']= self.parser.parse_shelxe_out(inverted)
        else:
            self.results['shelxe']= self.parser.parse_shelxe_out(inverted)

    def run(self,name,cell,spag,sad,*args,**kwargs):
        """ Main entry point to the pipeline. Four required positional arguments are name, cell, spag, sad
            All other options that are to be fed into shelxc can be appended as kwargs
        """
        
        try:
            logging.basicConfig(filename='shelx_pipeline.log',level=logging.INFO)
            logging.info('Starting the shelxc/d/e pipeline')
            self.name = name
            self.process_args(cell,spag,sad,**kwargs)
            self.call_shelxc(*args,**kwargs)
            self.call_shelxd(*args,**kwargs)
            self.call_shelxe(*args,**kwargs)
            self.call_shelxe(invert=True,*args,**kwargs)
        except:
            print "something bad happened"
            print  traceback.print_exc(file=sys.stdout)

def test_1():
    """Test to compare with known dataset"""
    logging.basicConfig(filename='shelx_pipeline_test1.log',level=logging.INFO)
    logging.info('Starting the shelxc/d/e pipeline')
    pipeline=AutoShelx()
    cell="42.215 42.719 70.371 90.0 90.0 90.0"
    spag="P212121"
    name="known_data_test"
    sad="aimless_hsymm.sca"
    logging.info('Starting for run '+name)
    shelxe_flags=["-h","-s0.27", "-m20"]
    # you can call it like this with the 4 compulsory positional args and the extra kwargs
    pipeline.run(name,cell,spag,sad,FIND=4,shelxe_flags=shelxe_flags,outfile='pipeline_test.out')
    
    fig,axes=plt.subplots(nrows=3,ncols=1)
    fig.tight_layout()
    plt.subplot(311)
    xs=np.array(pipeline.results['shelxc']['Resl.'])
    ys=np.array(pipeline.results['shelxc']['<I/sig>'])
    plt.plot(xs,ys,'bo')
    plt.axis([np.amax(xs)+1,np.amin(xs)-1,np.amin(ys)-1,np.amax(ys)+1])
    plt.xlabel(r'Resolution [$\AA$]')
    plt.ylabel('<I/sig>')
    plt.title('Resolution vs <I/sig>')
    
    plt.subplot(312)
    plt.plot(pipeline.results['shelxd']['CCweak'],pipeline.results['shelxd']['CCall'],'bo')
    plt.xlabel('CCweak')
    plt.ylabel('CCall')
    plt.title('CCall vs CCweak')

    plt.subplot(313)
    plt.plot(pipeline.results['shelxe']['cycle'],pipeline.results['shelxe']['Contrast'],'ro',
                  pipeline.results['shelxe_inverted']['cycle'],pipeline.results['shelxe_inverted']['Contrast'],'bo')
    plt.xlabel('Cycle')
    plt.ylabel('Contrast')
    plt.title('Constrast vs Cycle')

    plt.savefig('test_1_plots.png')
    #plt.show()

def main():
    logging.basicConfig(filename='shelx_pipeline.log',level=logging.INFO)
    logging.info('Starting the shelxc/d/e pipeline')
    parser=argparse.ArgumentParser()
    parser.add_argument("name",help="Name for this run")
    parser.add_argument("CELL",help="A string of 6 numbers of the unit cell")
    parser.add_argument("SPAG",help="something")
    parser.add_argument("SAD", help="Name of the hkl file to input")
    argsdict=vars(parser.parse_args())
    argsdict['outfile']="pipeline_output"
    pipeline=AutoShelx()
    logging.info('Starting for run '+argsdict['name'])
    shelxe_flags=["-h","-s0.5", "-m20"]
    # you can call it like this with the 4 compulsory positional args and the extra kwargs
    pipeline.run(argsdict['name'],argsdict['CELL'],argsdict['SPAG'],argsdict['SAD'],FIND=9,DSUL=8,shelxe_flags=shelxe_flags)
    

if __name__ == "__main__":
    test_1()
