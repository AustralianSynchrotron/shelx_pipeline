shelx_pipeline
==============


usage: shelx_pipeline.py [-h] name CELL SPAG SAD

positional arguments:
  name        Name for this experiment?run?thing?
  CELL        A string of 6 numbers of the unit cell
  SPAG        something
  SAD         Name of the hkl file to input

optional arguments:
  -h, --help  show this help message and exit

An example is:
./shelx_pipeline.py test "58.036 58.036 151.29 90 90 90" P41212 thau-nat.hkl

Otherwise, the entry point is the run method in the Pipeline class, which takes 4 positional arguments (as above) plus any number of keyword arguments.
