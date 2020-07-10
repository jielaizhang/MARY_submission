#!/usr/bin/env python3 
import os, time
import math
import sys
import glob
import argparse
import warnings
import multiprocessing
import subprocess
import astropy.io.fits as pyfits

def main():
    path = '/fred/oz100/pipes/DWF_PIPE/JSONS/'
    path_to_watch = path 
    before = dict ([(f, None) for f in os.listdir(path_to_watch)])
    print('Monitoring Directory:'+path_to_watch)
    while 1:
        after = dict ([(f, None) for f in os.listdir (path_to_watch)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]

        #if added: print("Added: ", ", ".join (added))
        #if removed: print("Removed: ", ", ".join (removed))

        for f in added:
            if f.endswith('.json'):
                print(f)
                os.system('mv '+ f + ' OLD_JSONS/.')
                os.system('python submit_mary_job.py ' + 'OLD_JSONS/'+f)
          

if __name__ == '__main__':
    main()
