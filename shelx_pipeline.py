#! /usr/bin/env python
from subprocess import call, Popen, PIPE, STDOUT
from string import Template
import sys,traceback
import logging
import tempfile
import argparse
from sets import Set
from parse_output import OutputParser

class Pipeline(object):
    

    def __init__(self):
        self.parser=OutputParser()
        self.defaults = {'FIND':9,'DSUL':7,'MIND':-3.5,'NTRY':100}
        self.input_params=self.defaults
        self.name=''
        self.outfile=''
        self.possible_params=Set({'FIND','DSUL','MIND','NTRY','SPAG','SAD','CELL'})
        self.parser=OutputParser()

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
            #self.parser.read(sout)
            p2=Popen(["tee",self.outfile],stdin=PIPE)
            p2.communicate(sout) 
        except:
            print "an error occured"
            traceback.print_exc()
            # didn't get the right parameters to make a proper input file, raise 
            # an exception
   
    def call_shelxd(self,*args,**kwargs):
        infilename=self.name+'_fa'
        p=Popen(["shelxd",infilename],stdout=PIPE)
        call(["tee","-a",self.outfile],stdin=p.stdout)
    

    def call_shelxe(self,*args,**kwargs):
        # args for shelxe given by my example here -h means heavy atoms in native data
        # -s0.5 means solvent fraction
        # -mN - N iterations of density modification per global cycle [-m20]
        infilename=self.name+'_fa'
        shelxe_flags=kwargs.get('shelxe_flags',[])
        shelxe_args=['shelxe',self.name,infilename]
        
        for a in shelxe_flags+list(args):
            shelxe_args.append(a)
        if not "-i" in shelxe_args and kwargs.get('invert',False)==True:
            shelxe_args.append("-i")
        p=Popen(shelxe_args,stdout=PIPE)
        # possible arguments are -h -s0.5 =m20 -i
        call(["tee","-a",self.outfile],stdin=p.stdout)
    

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
            self.call_shelxe("-h",*args,**kwargs)
            self.call_shelxe("-h",invert=True,*args,**kwargs)
        except:
            print "something bad happened"
            print  traceback.print_exc(file=sys.stdout)

def main():
    """Used for testing, the run method in the pipeline class is the relevant method to call from other python"""
    logging.basicConfig(filename='shelx_pipeline.log',level=logging.INFO)
    logging.info('Starting the shelxc/d/e pipeline')
    parser=argparse.ArgumentParser()
    parser.add_argument("name",help="Name for this experiment?run?thing?")
    parser.add_argument("CELL",help="A string of 6 numbers of the unit cell")
    parser.add_argument("SPAG",help="something")
    parser.add_argument("SAD", help="Name of the hkl file to input")
    argsdict=vars(parser.parse_args())
    argsdict['outfile']="pipeline_output"
    pipeline=Pipeline()
    logging.info('Starting for run '+argsdict['name'])
    shelxe_flags=["-s0.5", "-m20"]
    # you can call it like this with the 4 compulsory positional args and the extra kwargs
    pipeline.run(argsdict['name'],argsdict['CELL'],argsdict['SPAG'],argsdict['SAD'],FIND=9,DSUL=8,shelxe_flags=shelxe_flags)


    # call shelxc with t

if __name__ == "__main__":
    main()
