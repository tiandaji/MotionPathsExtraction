import configparser
import os, sys
import subprocess
import multiprocessing
from tkinter import messagebox

import detect_and_track


class BulkProcessor(object):

    def __init__(self):
        
        num_nvidia_gpus = str(subprocess.check_output(["nvidia-smi", "-L"])).count('UUID')
        
        config = configparser.ConfigParser()
        config.sections()
        config.read('bulk_config.ini')
        
        self.gpu_ids = config.items( "Gpus" )
        self.configs = config.items( "Configs" )
        self.inputs = config.items( "Input" )
        self.outputs = config.items( "Output" )
        
        if len(self.gpu_ids) < 1 or len(self.gpu_ids) > num_nvidia_gpus:
        	sys.exit('Number of processors to use must be greater than 0 and smaller than gpus available')
        
        if len(self.gpu_ids) != len(self.configs) != len(self.inputs) != len(self.outputs):
        	sys.exit('len(self.gpu_ids) != len(self.configs) != len(self.inputs) != len(self.outputs)')
        
    def process(self, i):
        
        print("Starting process on GPU %d" % int(self.gpu_ids[i][1]))    
        
        try:
            
            process = detect_and_track.App(True, int(self.gpu_ids[i][1]), str(self.configs[i][1]), str(self.inputs[i][1]), str(self.outputs[i][1]))
            process.start_bulk_process()

            print("Process on GPU %d stopped" % int(self.gpu_ids[i][1]))
        
        except Exception:
    
                e = sys.exc_info()[0] + '' + sys.exc_info()[1]
                print("Error: " + str(e))
                raise       
           
if __name__ == '__main__':

    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass
    
    procs = []
    bulk = BulkProcessor()    
    num_gpus = len(bulk.gpu_ids)
       
        
    print("using %d processors and gpus..." % num_gpus)    
    
    for i in range(num_gpus):        
        p = multiprocessing.Process(target=bulk.process, args=[i, ])
        procs.append(p)
        p.start()
            
    for proc in procs:
        proc.join()