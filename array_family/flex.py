from __future__ import division
from cctbx.array_family.flex import *
from dials.model import data
from dials_array_family_flex_ext import *

# Set the 'real' type to either float or double
if get_real_type() == "float":
  real = float
elif get_real_type() == "double":
  real = double
else:
  raise TypeError('unknown "real" type')


@staticmethod
def reflection_table_from_predictions(exlist):
  ''' Construct a reflection table from predictions. '''
  from dials.algorithms.integration import ReflectionPredictor
  from dials.array_family import flex
  predict = ReflectionPredictor()
  result = flex.reflection_table()
  for idx, ex in enumerate(exlist):
    rlist = predict(ex.imageset, ex.crystal)
    rtable = rlist.to_table()
    rtable['id'] = flex.size_t(len(rlist), idx)
    result.extend(rtable)
  return result

@staticmethod
def reflection_table_from_observations(datablocks, params):
  ''' Construct a reflection table from observations. '''
  from dials.algorithms.peak_finding.spotfinder_factory \
    import SpotFinderFactory

  # Ensure we have a data block
  if len(datablocks) != 1:
    raise RuntimeError('only 1 datablock can be processed at a time')

  # Get the integrator from the input parameters
  print 'Configuring spot finder from input parameters'
  find_spots = SpotFinderFactory.from_parameters(params)

  # Find the spots
  return find_spots(datablocks[0])

def reflection_table_as_pickle(self, filename):
  ''' Write the reflection table as a pickle file. '''
  import cPickle as pickle
  with open(filename, 'wb') as outfile:
    pickle.dump(self, outfile, protocol=pickle.HIGHEST_PROTOCOL)

@staticmethod
def reflection_table_from_pickle(filename):
  ''' Read the reflection table from pickle file. '''
  import cPickle as pickle
  with open(filename, 'rb') as infile:
    return pickle.load(infile)

def reflection_table_as_h5(self, filename):
  ''' Write the reflection table as a HDF5 file. '''
  from dials.util.nexus import NexusFile
  handle = NexusFile(filename, 'w')
  handle.set_reflections(self)
  handle.close()

@staticmethod
def reflection_table_from_h5(filename):
  ''' Read the reflections table from a HDF5 file. '''
  from dials.util.nexus import NexusFile
  handle = NexusFile(filename, 'r')
  self = handle.get_reflections()
  handle.close()
  return self

reflection_table.from_predictions = reflection_table_from_predictions
reflection_table.from_observations = reflection_table_from_observations
reflection_table.from_pickle = reflection_table_from_pickle
reflection_table.as_pickle = reflection_table_as_pickle
reflection_table.from_h5 = reflection_table_from_h5
reflection_table.as_h5 = reflection_table_as_h5
