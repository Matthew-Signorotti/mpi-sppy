# This software is distributed under the 3-clause BSD License.
# Program to create proper bundles for aircond; DLW march 2022
# NOTE: As of 3 March 2022, you can't compare pickle bundle problems with non-pickled. See _demands_creator in aircondB.py for more discusion.
# see try_pickles.bash
# parallel version

import sys
import os
import copy
import numpy as np
import itertools
import mpisppy.tests.examples.aircondB as aircondB
from mpisppy.utils import baseparsers
from mpisppy.utils import pickle_bundle

from mpisppy import MPI

n_proc = MPI.COMM_WORLD.Get_size()
my_rank = MPI.COMM_WORLD.Get_rank()

# construct a node-scenario dictionary a priori for xhatspecific_spoke,
# according to naming convention for this problem

def _parse_args():
    parser = baseparsers._basic_multistage()
    parser = pickle_bundle.pickle_bundle_parser(parser)
    parser = aircondB.inparser_adder(parser)
    args = parser.parse_args()

    return args

def main():

    args = _parse_args()
    assert args.pickle_bundles_dir is not None
    assert args.scenarios_per_bundle is not None
    assert args.unpickle_bundles_dir is None

    BFs = args.branching_factors

    if BFs is None:
        raise RuntimeError("Branching factors must be specified")

    ScenCount = np.prod(BFs)

    sc_options = {"args": args}
    kwargs = aircondB.kw_creator(sc_options)

    bsize = int(args.scenarios_per_bundle)
    numbuns = ScenCount // bsize
    # we won't actually use all names
    all_bundle_names = [f"Bundle_{bn*bsize}_{(bn+1)*bsize-1}" for bn in range(numbuns)]

    if numbuns < n_proc:
        raise RuntimeError(
            "More MPI ranks (%d) supplied than needed given the number of bundles (%d) "
            % (n_proc, numbuns)
        )

    avg = numbuns / n_proc
    slices = [list(range(int(i * avg), int((i + 1) * avg))) for i in range(n_proc)]

    local_slice = slices[my_rank]
    local_bundle_names = [f"Bundle_{bn*bsize}_{(bn+1)*bsize-1}" for bn in local_slice]

    #print(f"{slices=}")
    #print(f"{local_bundle_names=}")
    
    for bname in local_bundle_names:
        aircondB.scenario_creator(bname, **kwargs)
    

if __name__ == "__main__":
    main()
    
