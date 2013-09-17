#! /usr/bin/env python
from subprocess import call, Popen, PIPE, STDOUT
from string import Template
import sys,traceback
import logging
import tempfile
import argparse
from sets import Set


class Pipeline:
    
    defaults = {'FIND':9,'DSUL':7,'MIND':-3.5,'NTRY':100}
    input_params=defaults
    name=''
    outfile=''
    possible_params=Set({'FIND','DSUL','MIND','NTRY','SPAG','SAD','CELL'})

    def process_args(self,cell,spag,sad,**kwargs):
        self.outfile=kwargs.get('outfile',"shelx_pipeline.out")
        self.input_params.update({'CELL':cell,'SPAG':spag,'SAD':sad})
        self.input_params.update(kwargs)
        print kwargs
        print self.input_params


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
        
            p=Popen(["shelxc",self.name],stdin=PIPE,stdout=PIPE)
            (sout,serr)=p.communicate(instring)
                # print sout
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
        infilename=self.name+'_fa'
        p=Popen(["shelxe",infilename],stdout=PIPE)
        call(["tee","-a",self.outfile],stdin=p.stdout)
    

    def run(self,name,cell,spag,sad,**kwargs):
        """ Main entry point to the pipeline. Four required positional arguments are name, cell, spag, sad
            All other options that are to be fed into shelxc can be appended as kwargs
        """
        
        try:
            logging.basicConfig(filename='shelx_pipeline.log',level=logging.INFO)
            logging.info('Starting the shelxc/d/e pipeline')
            self.name = name
            self.process_args(cell,spag,sad,**kwargs)
            self.call_shelxc(**kwargs)
            self.call_shelxd(**kwargs)
            self.call_shelxe(**kwargs)
        except:
            print "something bad happened"


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
    # you can call it like this with the 4 compulsory positional args and the extra kwargs
    pipeline.run(argsdict['name'],argsdict['CELL'],argsdict['SPAG'],argsdict['SAD'],FIND=9,DSUL=8)


    # call shelxc with t

if __name__ == "__main__":
    main()
