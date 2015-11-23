"""
Figure out correct gradient expressions required for crystal unit cell
restraints

"""

# Python and cctbx imports
from __future__ import division
import sys
from math import pi
from scitbx import matrix
from libtbx.phil import parse
from libtbx.test_utils import approx_equal
from scitbx.array_family import flex

# Get modules to build models and minimiser using PHIL
from dials.test.algorithms.refinement import setup_geometry
from dials.test.algorithms.refinement import setup_minimiser

from dials.algorithms.refinement.parameterisation.crystal_parameters import \
    CrystalOrientationParameterisation, CrystalUnitCellParameterisation

# Symmetry constrained parameterisation for the unit cell
from cctbx.uctbx import unit_cell
from rstbx.symmetry.constraints.parameter_reduction import \
    symmetrize_reduce_enlarge

DEG2RAD = pi/180.0
RAD2DEG = 180.0/pi

args = sys.argv[1:]
master_phil = parse("""
    include scope dials.test.algorithms.refinement.geometry_phil
    include scope dials.test.algorithms.refinement.minimiser_phil
    """, process_includes=True)

models = setup_geometry.Extract(master_phil, cmdline_args = args)
crystal = models.crystal

print crystal

# derive finite difference gradients of various quantities wrt each param
def check_fd_gradients(parameterisation):

  mp = parameterisation
  p_vals = mp.get_param_vals()
  deltas = [1.e-7 for p in p_vals]
  assert len(deltas) == len(p_vals)
  fd_grad = []

  for i in range(len(deltas)):

    val = p_vals[i]

    p_vals[i] -= deltas[i] / 2.
    mp.set_param_vals(p_vals)
    rev_uc = mp.get_model().get_unit_cell().parameters()
    rev_vec = mp.get_model().get_real_space_vectors()

    p_vals[i] += deltas[i]
    mp.set_param_vals(p_vals)
    fwd_uc = mp.get_model().get_unit_cell().parameters()
    fwd_vec = mp.get_model().get_real_space_vectors()

    fd_uc = [(f - r) / deltas[i] for f,r in zip(fwd_uc, rev_uc)]
    fd_vec = [(f - r) / deltas[i] for f,r in zip(fwd_vec, rev_vec)]
    fd_grad.append({'da_dp':fd_uc[0],
                    'db_dp':fd_uc[1],
                    'dc_dp':fd_uc[2],
                    'daa_dp':fd_uc[3],
                    'dbb_dp':fd_uc[4],
                    'dcc_dp':fd_uc[5],
                    'davec_dp':fd_vec[0],
                    'dbvec_dp':fd_vec[1],
                    'dcvec_dp':fd_vec[2]})

    p_vals[i] = val

  # return to the initial state
  mp.set_param_vals(p_vals)

  return fd_grad

xlo_param = CrystalOrientationParameterisation(crystal)
xluc_param = CrystalUnitCellParameterisation(crystal)

from dials.algorithms.refinement.restraints.restraints import SingleUnitCellTie
uct = SingleUnitCellTie(xluc_param, [None]*6, [None]*6)

from dials.algorithms.refinement.refinement_helpers import \
      AngleDerivativeWrtVectorElts

B = crystal.get_B()
O = (B.transpose()).inverse()
a, b, c, aa, bb, cc = crystal.get_unit_cell().parameters()
aa *= DEG2RAD
bb *= DEG2RAD
cc *= DEG2RAD
avec, bvec, cvec = crystal.get_real_space_vectors()

# calculate d[B^T]/dp
dB_dp = xluc_param.get_ds_dp()
dBT_dp = [dB.transpose() for dB in dB_dp]

# calculate d[O]/dp
dO_dp = [-O * dBT * O for dBT in dBT_dp]

# d[alpha]/d[a_i] and d[alpha]/d[b_i]
dangle = AngleDerivativeWrtVectorElts(avec, bvec)

# get all FD derivatives
fd_grad = check_fd_gradients(xluc_param)

# look at each parameter
for i, dO in enumerate(dO_dp):

  # extract derivatives of each unit cell vector wrt p
  dav_dp, dbv_dp, dcv_dp = dO.as_list_of_lists()
  dav_dp = matrix.col(dav_dp)
  dbv_dp = matrix.col(dbv_dp)
  dcv_dp = matrix.col(dcv_dp)

  # check these are correct vs FD
  diff = dav_dp - fd_grad[i]['davec_dp']
  print 2 * diff.length() / (dav_dp.length() + fd_grad[i]['davec_dp'].length()) * 100
  print 'davec_dp analytical: {0} {1} {2}'.format(*dav_dp.elems)
  print 'davec_dp finite diff: {0} {1} {2}'.format(*fd_grad[i]['davec_dp'].elems)

  # only the first one seems about right. What about b?
  diff = dbv_dp - fd_grad[i]['dbvec_dp']
  print 2 * diff.length() / (dbv_dp.length() + fd_grad[i]['dbvec_dp'].length()) * 100
  print 'dbvec_dp analytical: {0} {1} {2}'.format(*dbv_dp.elems)
  print 'dbvec_dp finite diff: {0} {1} {2}'.format(*fd_grad[i]['dbvec_dp'].elems)

  # and c?
  diff = dcv_dp - fd_grad[i]['dcvec_dp']
  print 2 * diff.length() / (dcv_dp.length() + fd_grad[i]['dcvec_dp'].length()) * 100
  print 'dcvec_dp analytical: {0} {1} {2}'.format(*dcv_dp.elems)
  print 'dcvec_dp finite diff: {0} {1} {2}'.format(*fd_grad[i]['dcvec_dp'].elems)
  print

  # only gradients for the first three parameters seem to make any sense, and
  # each of these is only correct for one vector: a for the first parameter,
  # b for the second and c for the last.

  # only orthogonal changes are relevant
  ua = avec.normalize()
  if dav_dp.length() < 1e-10:
    ortho_dav_dp = matrix.col((0, 0, 0))
  else:
    v = avec.cross(dav_dp).normalize()
    u = v.cross(ua).normalize()
    ortho_dav_dp = dav_dp.dot(u) * u

  ub = bvec.normalize()
  if dbv_dp.length() < 1e-10:
    ortho_dbv_dp = matrix.col((0, 0, 0))
  else:
    v = bvec.cross(dbv_dp).normalize()
    u = v.cross(ub).normalize()
    ortho_dbv_dp = dbv_dp.dot(u) * u

  dalpha_da = matrix.col((dangle.dtheta_du_1(), dangle.dtheta_du_2(), dangle.dtheta_du_3()))
  dalpha_db = matrix.col((dangle.dtheta_dv_1(), dangle.dtheta_dv_2(), dangle.dtheta_dv_3()))
  daa_dp = ortho_dav_dp.dot(dalpha_da) + ortho_dbv_dp.dot(dalpha_db)

  #print daa_dp * RAD2DEG

# enter interactive console
from dials.util.command_line import interactive_console; interactive_console()
