#Define base directory
basedir="/afs/cern.ch/user/n/nskidmor/work/AmpGen/"

#Specify your input text file - NEED BOTH
textFileName="DtoKKpipi_v2.opt"
textFile = basedir+"options/" + textFileName

#Specify other files required at run time 
ParticleProp = basedir + "options/"
input_mass=ParticleProp+"mass_width.csv"
input_parts=ParticleProp+"MintDalitzSpecialParticles.csv"
lib = basedir + "build/lib/libAmpGen.so"

#For configuring many subjobs
inputargs=[]
#sjInputArgs = []
#sjInputArgs.append(textFileName)
#inputargs.append(sjInputArgs)

#Define job
#############################################################################
####For the first time you run within a folder use only these two lines######
try:
    app = prepareGaudiExec('DaVinci','v44r5', myPath='./')
    app.platform='x86_64-slc6-gcc62-opt'

#####For all subsequent times within the same folder use only these 2 lines## 
except:
    app = GaudiExec()
    app.directory = "./DaVinciDev_v44r5"

print "Using ", app
##############################################################################

#Specify the executables you want to run
exe=basedir+"build/bin/Generator"
script=basedir+"batch/RunmyjobGanga.py"
app.options = [script]

#Specify backend
bckend = Dirac() 
#bckend.settings['CPUTime']=60*60*18*10*10
#bckend.settings['Destination']='LCG.CERN.cern'
print script, exe

#Now configure the subjobs
RandSeedInit = 0
subjobs = 10

i=0
inputargs = []
inputs = [lib]

#For read in of original textfile
outputlines=[]
file = open(textFile)
while 1:
     line = file.readline()# read file
     if not line:
         break
     pass
     outputlines.append(line+'\n')
file.close()

#Creating subjob textfiles
for subjob in range(0,subjobs):
    
    sjInputArgs = []
    seed = RandSeedInit+i 
    #Write Generator File
    GenFileName = "Inputfile_"+str(seed)+".opt"
    GENFILE = open(GenFileName,"w")
    GENFILE.writelines(outputlines)
    GENFILE.write("Seed     "+ str(seed) + "\n")
    GENFILE.close()

    sjInputArgs.append(GenFileName)
    
    inputargs.append(sjInputArgs)
    inputs.append(GenFileName)

    i = i + 1

inputs.extend([exe, textFile, input_mass, input_parts, script])

j=Job(name="test",
          application=app,
          backend=bckend,
          inputfiles = inputs, #Include any additional files needed
          outputfiles =['*.eps','*.pdf','*.png','*.txt','*.root', 'stdout']) #Anything you want returned need to be in here

j.splitter = ArgSplitter(args=inputargs)
j.submit()    

