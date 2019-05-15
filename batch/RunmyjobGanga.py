import os, sys, time
import subprocess

os.system('echo $ROOTSYS')

print "ROOT environment configured"

GenInputFile = sys.argv[2]

#os.system("ldd libAmpGen.so")
#os.system("ls")
#os.system("ldd ./Generator")
#The output of the job will also be copied into a file "output_job.txt"
myenv = os.environ
myenv["LD_LIBRARY_PATH"]=os.environ["LD_LIBRARY_PATH"]+os.pathsep+"."
subprocess.Popen(["./Generator", GenInputFile,"--nEvents=10", ">", "output_job.txt"], env=myenv)
