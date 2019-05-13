import os, sys, time
#import subprocess

os.system('echo $ROOTSYS')

print "ROOT environment configured"

GenInputFile = sys.argv[2]

os.system("ls")
#The output of the job will also be copied into a file "output_job.txt"
os.system('./Generator ' + GenInputFile + ' --nEvents=10 > output_job.txt')
