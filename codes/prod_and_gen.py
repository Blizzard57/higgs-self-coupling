## Generate Process from MadGraph, and store in a .h5 file
import os
os.chdir("/home/blizzard/Applications/madGraph/")

from dataClass import GenDataset

os.chdir("/home/blizzard/HiggsCoupling/codes")
os.system("~/Applications/madGraph/bin/mg5_aMC ~/HiggsCoupling/codes/gen_madgraph_proc.txt")
s1 = GenDataset("~/Tests/hh_bbWW_3/Events/run_01/tag_1_delphes_events.root")
s1.createDataset("../datasets/test3Dataset.h5")