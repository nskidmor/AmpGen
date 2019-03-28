[![Build Status][travis-badge]][https://travis-ci.org/GooFit/AmpGen]
[![License: LGPL v3][license-badge]](./LICENSE)

<p align="center">
  <img src="https://github.com/GooFit/AmpGen/raw/master/doc/figs/logo.png">
</p>
AmpGen is a library and set of applications for fitting and generating multi-body particle decays using the isobar model.
It developed out of the MINT project used in the fitting of three and four-body pseudoscalar decays by the CLEO-c and LHCb colloborations. The library can handle the fitting and generation of a wide variety of final states, including those involving fermions and photons, as well as polarised initial states.

Source code for the evaluation of amplitudes is dynamically generated by a custom engine, JIT compiled and dynamically linked to the user programme at runtime, which results in high flexibility and performance. 

## Table of Contents 
* [Getting Started](#getting-started)
* [Applications](#applications)
* [Examples](#examples)
* [Advanced](#advanced)
* [API documentation](https://goofit.github.io/AmpGen/)
* [Acknowledgements](#acknowledgements)

## Getting started
### Installation
#### Getting the source
Clone with git
```
git clone http://github.com/GooFit/AmpGen/ --recursive
```
There is at the time of writing only a master branch (FIXME)

##### Build requirements:
* cmake >= 3.11.0 
* C++ compiler with CXX standard >= 14 (gcc >= 4.9.3, clang ~ 5). 
  Defaults to Cxx17 (enable cxx14 with cmake flag `-DCMAKE_CXX_STANDARD=14` )
* ROOT >= 6 with MathMore
  To (re)configure root with these options, use the additional command line options `-Dcxx14 -Dmathmore=ON` when configuring the installation of ROOT. 

##### Optional:
* boost >= 1.67.0 for unit tests 
* xROOTd for network file access 
* OpenMP for multithreading
* ROOT >= 6 with MathMore and Minuit2 enabled. The external version of Minuit2 provided as an external package of GooFit is used if the ROOT version is not unavailable. 
  To (re)configure root with these options, use the additional command line options `-Dcxx14 -Dminuit2=ON -Dmathmore=ON` when configuring the installation of ROOT. 

#### Building
The configuration of the AmpGen build is performed by cmake. 
It is recommended to use a build directory to keep the source tree clean. 

```shell
mkdir build
cd build
cmake ..
make
```
This will build the shared library, several standalone test applications, and a set of unit tests. 

#### Usage with ROOT

The library can be used interactively in conjunction with the ROOT C++ interpreter by adding the following lines 
to the users root login script 

```
  gSystem->Load("path_to_ampgen/build/lib/libAmpGen.so");
  gROOT->ProcessLine(".include path_to_ampgen");
```
##### LLVM
You can also build AmpGen with LLVM. The only change you might want when using Apple LLVM
is to specifically specify the location of the build tool for AmpGen's JIT:

```shell
-DAMPGEN_CXX=$(which c++)
```

##### CentOS7

In order to build stand-alone on CentOS7, you will need a valid development environment; the following line will work:

```shell
lb-run ROOT $SHELL
```
Several examples of usages of the library are included in the apps directory and are 
built alongside the library. 
All standalone programs can accept both options files and command line arguments. 
They also support `--help` to print help for key arguments to the program. 
This will also run the program, as arguments can be defined throughout each of the programs rather than all defined at the beginning. 

### Options files and decay descriptors 

Options files will generally contain the description of one or more particle decays,
as well as other settings such as input/output locations, global flags such as 
whether complex numbers should be interpreted as cartesian or polar, and other parameters 
such as the masses and widths of particles is these differ from those given in the PDG.
 
A minimal example options file for the generator application could contain: 
```
EventType D0 K+ pi- pi- pi+
#                                           Real / Amplitude   | Imaginary / Phase 
#                                           Fix?  Value  Step  | Fix?  Value  Step
D0{K*(892)0{K+,pi-},rho(770)0{pi+,pi-}}     2     1      0       2     0      0   
```
The EventType specifies the initial and final states requested by the user. 
This gives the ordering of particles used in input data, in output code, and used in internal computations. 
This also defines how the amplitude source code must be interfaced with external packages, i.e. MC generators such as EvtGen.

The decay products of a particle are enclosed within curly braces, for example
```
K*(892)0{K+,pi-}
```
describes an excited vector kaon decaying into a charged kaon and pion. 
For more details about the API for describing particle decays, see [AmpGen::Particle](https://tevans1260.gitlab.io/AmpGen/de/dd7/class_amp_gen_1_1_particle.html).
The other numbers on the lines that describe the decays parameterise the coupling to this channel, 
either in terms of real and imaginary parts or an amplitude and a phase.
Each parameter is specified in terms of three numbers: the _fix_ flag, the initial value, and the step size. 
The possible options for the _fix_ flag are: 
* Free (fix=0) and a step size of not 0.
* Fixed (fix=2, for historical reasons)
* Compile-Time-Constant (fix=3) which indicates that the parameter should be treated as a (JIT) compile time constant, which in some cases allows for more aggressive optimisations to be performed. 

These options can be used in the Generator application, which is described below. 

Decays can either be specified fully inline, as above, or split into multiple steps, which is useful for treating the so called _cascade_ decays, an example of which is shown below.
```
D0{K(1)(1270)+,pi-}                         0     1      0.1       0     0      0.1   

K(1)(1270)+{rho(770)0{pi+,pi-},K+}          2     1      0         2     0      0
K(1)(1270)+{K*(892)0{K+,pi-},pi+}           0     1      0.1       0     0      0.1
```
The production/decay couplings of the K(1270) resonance are now defined in terms of the coupling to the rho(770),K+ channel, 
which can be useful in making comparisons between different production modes of a resonance. 
Additional care must be taken in such a case to not introduce redundant degrees of freedom. 

Configuration can be split over multiple files by the using _Import_ keyword, for example, to import the parameters for the isoscalar K-matrix, the line 
```
Import $AMPGENROOT/options/kMatrix.opt
```
can be added to options file. Multiple user configuration files can also be specified by including multiple files on the command line. 

## Applications
This section details the prebuilt command line applications that use the AmpGen library for some common functionality, such as generating Toy Monte Carlo samples 
and debugging amplitudes. 

### Table of contents
* [Generator](#generator)
* [Debugger](#debugger)
* [ConvertToSourceCode](#converttosourcecode)

### Generator

The standalone generator for models can be used as

```shell
Generator MyOpts.opt --nEvents=10000 --Output=output.root
```

Which generates 10000 events of the model described in MyOpts.opt and saves them to output.root. 
The output should include a tree (DalitzEventList) of candidates with the full four-vectors, as well as one- and two-dimensional projections, an example of which is shown below:

![s01](doc/figs/s01.png)

In particular, the tree indicates the way in which data is by default loaded into the _Event_ / _EventList_ class. 

### Debugger 

The debugger application is a tool for producing verbose information debugging for amplitudes and models. It is used on an options file as 
```
./Debugger MyOpts.opt
```
which calculates each amplitude at a randomly generated point in phase space, as well as calculating the total amplitude accounting for complex 
couplings. Also computed is the amplitude for the P conjugate event. A more useful application is the _verbose_ debugging mode which can be 
activated by 
```
./Debugger MyOpts.opt --CoherentSum::Debug
```
which produces a large number of intermediate steps in the calculation of each amplitude, which are added to the calculation using the 
ADD_DEBUG and ADD_DEBUG_TENSOR macros in the code generation. For example, in src/Lineshapes/BW.cpp. 

### ConvertToSourceCode

This produces source code to evaluate the PDF, and normalises for use with other generators such as EvtGen, i.e. P(max) < 1. This can be used as
```shell
./ConvertToSourceCode MyOpts.opt --Output=MyFile.cpp
```
This can then be a compiled to a shared library using
```shell
g++ -Ofast -shared -rdynamic --std=c++14 -fPIC MyFile.cpp -o MyFile.so
```


## Examples

### SignalOnlyFitter

An example fitter is provided in _examples/SignalOnlyFitter.cpp_, which as the name suggests only has a single signal component in the fit. 
The free parameters of the fit are specified in the same way as the Generator, 
with the additional relevant slots being _DataSample_ which specifies the signal sample to fit, 
which is presumed to already have the selection applied, and _Branches_ which takes a list of branch names, 
and defaults to the format used by the Generator etc. More details can be found with 
```
SignalOnlyFitter --help
```
For example, the fitter can be used to fit a toy MC sample generated by the generator by running:
```
Generator MyOpts.opt --nEvents 100000
SignalOnlyFitter MyOpts.opt --DataSample Generate_Output.root
```

## Advanced 

This section contains miscellaneous details on more advanced functionality, including using python bindings and alternative parameterisation of the spin factors. 

### Table of contents
* [Python Bindings](#python-bindings)
* [Particle Properties and Lineshape parameters](#particle-properties-and-lineshape-parameters)
* [Fit parameters and expressions](#fit-parameters-and-expressions)
* [Spin Formalisms](#spin-formalisms)


### Python Bindings
Models built into a shared library can be used in python using the following flags into ConvertToSourceCode:
```shell 
./ConvertToSourceCode MyOpts.opt --Output=MyFile.cpp --OutputEvents=events.csv --IncludePythonBindings
```
where normalisation events are also output for testing purposes in events.csv. 
This can then be used with the python bindings in ampgen.py:  
```python
from ampgen import FixedLib
model = FixedLib('MyModel.so')
print(model.matrix_elements[0]) # Print first matrix element

import pandas as pd
data = pd.read_csv('events.csv', nrows=100_000)
fcn1 = model.FCN_all(data)

# or, a bit slower, but just to show flexibility:
fcn2 = data.apply(model.FCN, axis=1)
```

### Particle Properties and Lineshape parameters
The particles available and their default properties can be found in *options/mass\_width.csv* using the MC format of the 2008 PDG.
Additional pseudoparticles, such as nonresonant states and terms for use in conjunction with K-matrices are defined by *options/MintDalitzSpecialParticles.csv*.
Any additional user defined particles should be added here.
For the default lineshape (the relavistic Breit-Wigner or BW), there are three parameters: The mass, the width and the Blatt-Weisskopf radius. 
These default to their PDG values, but can be overridden in the options file with parameters: *particleName*\_mass, *particleName*\_width, *particleName*\_radius. 
So if the K(1270)+ mass was allowed to vary, the line: 
```
K(1270)+_mass 0 1.270 0.01
```
could be added to the user configuration. 
Other lineshapes may define other parameters, for example channel couplings or pole masses in the case of the K-matrices, which can be set or varied in a similar manner.  

### Fit parameters and expressions

Parameters can either be specified by three parameters, in the case of a scalar parameter such as a mass or a width, or with six parameters in the case of a complex parameter such as a coupling. 
Upper and lower bounds on parameters can also be set by specifying a parameter with five parameters or ten parameters for a scalar or complex, respectively. 
For example, if we wished to vary the K(1)(1270)+ mass in the above example, but restricting the allowed values in the range \[0.0,2.0\] GeV: 
```
K(1)(1270)+_mass 0 1.27 0.01 0.0 2.0
```

(Scalar) parameters can also be related to each other via simple expressions, although the implementation of this is rather unreliable so should be used with caution. 
Suppose for example we have K(1)(1270)+ and K(1)(1270)bar- in the same fit (for example, for D-\>KKpipi) 
The properties of one can be allowed to vary, for example the K(1)(1270)+, and the other fixed to the same value, using:
```
K(1)(1270)+_mass 0 1.27 0.01 0.0 2.0 
K(1)(1270)bar-_mass = K(1)(1270)+_mass 
```
Due to the abundance of **odd** glyphs such as brackets and +/- in parameter names, parameter expressions are white space delimited and somewhat sensitive to bracket usage. 

### Spin Formalisms

AmpGen implements both the covariant tensor (or Rarita-Schwinger) and canonical helicity formalism for describing the angular momentum component of decays. 
Both formalisms refer to states of well-defined orbital angular momentum, as opposed to the helicity states, as the states with well-defined orbital angular momentum have a straightforward parity and momentum dependences. 
The default formalism is the covariant tensor formalism, but this can be switched to the canonical formalism changing the flag 
```
Particle::SpinFormalism Canonical ## default = Covariant
```
in the options file. 
The spin formalism for an individual decay chain can be specified by changing the attribute SpinFormalism in the decay descriptor. For example, 
```
D0[SpinFormalism=Canonical]{K*(892)bar0,rho(770)0}
```
selects the S-wave of the K*, rho system. The user can also specify systems of helicity couplings in the canonical formalism, using the attribute _helAmp_. 
For example, suppose the transversity amplitudes were used rather than the canonical, then the user can specify
```
D0[SpinFormalism=Canonical;helAmp=Long]{K*(892)bar0,rho(770)0}
D0[SpinFormalism=Canonical;helAmp=t1]{K*(892)bar0,rho(770)0}
D0[SpinFormalism=Canonical;helAmp=t2]{K*(892)bar0,rho(770)0}
```
For the longitudinal and two transverse amplitudes. These must then be defined by the user in terms of the helicity amplitudes in the following structure:
```
Long {
  1.0 0 0
}

t1 {
  0.707106781 +1 +1
  0.707106781 -1 -1
}

t2 {
   0.707106781 +1 +1
  -0.707106781 -1 -1
}
```
That is specified as sets of three numbers, firstly the coupling, and then the two particle helicities. So in this example, the longitudinal amplitude is the 00 helicity state, while the two transverse amplitudes and the sum and difference of the two other helicity amplitudes.


## Acknowledgements
The development of this software has been  supported by the National Science Foundation under grant PHY-1414736 and through a subcontract under Cooperative Agreement OAC-1836650.   Any opinions, findings, and conclusions or recommendations expressed in this material are those of the developers and do not necessarily reflect the views of the National Science Foundation.

<p align="center">
  <div>
  <img src="https://github.com/GooFit/AmpGen/raw/master/doc/figs/UC_ID_PrimaryBlackRed.png"> 
  <img src="https://github.com/GooFit/AmpGen/raw/master/doc/figs/Iris-hep-3-regular-complete.png"> 
  <img src="https://github.com/GooFit/AmpGen/raw/master/doc/figs/NSF_4-Color_bitmap_Logo.png">
  </div>
</p>

[travis-badge]:      https://travis-ci.org/GooFit/AmpGen.svg?branch=master
[license-badge]:     https://img.shields.io/badge/License-GPL%20v2-blue.svg

