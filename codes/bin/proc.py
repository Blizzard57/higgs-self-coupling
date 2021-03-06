'''
This code creates a text file that contains code for MadGraph.
MadGraph is then run and the data is extracted and stored.
The following is implemented :
    - Combinatorix
    - Generation Level Cuts
    - Matching
'''

from distutils.util import strtobool
import os
import subprocess
import sys
from config import *

def proc_to_gen(proc, signal = 'hh'):
    ret_val = ''
    if proc == 'hh' and signal == 'hh':

        # Original Decay
        ret_val += 'generate pb pb > h > h h, '
        ret_val += '(h > b b~), (h > w w, w > la vla)\n'

        # Combinatorics on the Decay
        ret_val += 'add process pb pb > h > h h, '
        ret_val += '(h > w w, w > la vla), (h > b b~)\n'

    elif proc == 'ttbar' and signal == 'hh':

        # Original Decay
        ret_val += 'generate pb pb > t t~, '
        ret_val += '(t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)\n'

        # Original Decay with One Jet
        ret_val += 'add process pb pb > t t~ j, '
        ret_val += '(t > w+ b, w+ > l+ vl), (t~ > w- b~, w- > l- vl~)\n'

    elif proc == 'twj' and signal == 'hh':
        
        # Decay
        ret_val += 'generate pb pb > t w, (w > la vla), (t > w b,w > la vla)\n'

        # Alternate Decay
        ret_val += 'add process pb pb > t~ w, (w > la vla), (t~ > w b~,w > la vla)\n'

        # Decay with One Jets
        ret_val += 'add process pb pb > t w j,(w > la vla), (t > w b,w > la vla)\n'

        # Alternative Decay with One Jet
        ret_val += 'add process pb pb > t~ w j, (w > la vla), (t~ > w b~,w > la vla)\n'

    elif proc == 'llbj' and signal == 'hh':
        
        # Decay
        ret_val += 'generate pb pb > la la b\n'

        # Adding the Jets
        ret_val += 'add process pb pb > la la b j\n' 

    elif proc == 'tth' and signal == 'hh':

        # Decay
        ret_val += 'generate pb pb > t t~ h, (t > b w+, w+ > l+ vl), (t~ > b~ w-, w- > l- vl~)\n'

        # Decay with One Jet
        ret_val += 'add process pb pb > t t~ h j, (t > b w+, w+ > l+ vl), (t~ > b~ w-, w- > l- vl~)\n'

    elif proc == 'taubb' and signal == 'hh':
        ret_val += 'generate pb pb > ta ta~ b b, (ta+ > w+ vl, w+ l+ vl), (ta- > w- vl~, w- > l- vl~)\n'

        ret_val += 'add process pb pb > ta ta~ b b j, (ta+ > w+ vl, w+ l+ vl), (ta- > w- vl~, w- > l- vl~)\n'

    return ret_val


def gen_cuts():
    ret_val = ''

    ret_val += 'set ptl      120 \n'
    ret_val += 'set ptj1min  120 \n'
    ret_val += 'set etaj     2   \n'

    return ret_val

def jet_matching(proc):
    # Reference : https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/IntroMatching
    ret_val = ''

    # Matching for ttbar at 1 Jet
    if proc in ['ttbar','twj']:
        ret_val += 'set xqcut 20\n'
        ret_val += 'set JetMatching:qCut 30\n'
        ret_val += 'set JetMatching:nJetMax 1\n'

    # Matching for W&Z at 2 Jets
    elif proc in ['wmp','wpwm','zwpm']:
        ret_val += 'set xqcut 10\n'
        ret_val += 'set JetMatching:qCut 15\n'
        ret_val += 'set JetMatching:nJetMax 2\n'

    ret_val += 'set use_syst False\n'

    return ret_val

def get_run_soft():
    ret_val = ''
    if RUN_PYTHIA:
        ret_val += 'shower = pythia8\n'
    else:
        ret_val += 'shower = off\n'

    if RUN_DELPHES:
        ret_val += 'detector = Delphes\n'
    else:
        ret_val += 'detector = off\n'

    if RUN_ANALYSIS:
        ret_val += 'analysis = MadAnalysis4\n'
    else:
        ret_val += 'analysis = off\n'

    return ret_val

def main(proc_name,sig_flag,gen_proc = True):
    # The loop starts at 1 as default seed (0) takes a random value of seed
    for i in range(START_SEED,NUM_RUNS+START_SEED):

        # Making File for MadGraph
        f = open(TXT_DIR + proc_name + '.txt','w')

        # Default Import and Variable Definitions
        f.write('import model heft\n')
        f.write('define pb = p b b~\n')
        f.write('define w = w+ w-\n')
        f.write('define la = l+ l-\n')
        f.write('define vla = vl vl~\n')

        # Generation for a Particular Channel
        f.write(proc_to_gen(proc_name))

        # General Output (Same for all the Channels)
        f.write('output ' + OUTPUT_DIR + proc_name + '\n')
        f.write('launch\n')
        f.write(get_run_soft())
        f.write('done\n')
        f.write('set nevents ' + str(EVENT_NUM) + '\n')
        f.write('set ebeam1 7000.0\nset ebeam2 7000.0\n')
        f.write(jet_matching(proc_name))
        f.write(gen_cuts())
        f.write('set iseed ' + str(i) + '\n')

        # True only for Background
        if not sig_flag:
            f.write('set cut_decays True\n')

        # Closing the file
        f.close()

        # Flag checking if process is to be generated
        if gen_proc:
            # madGraph Operations
            p = subprocess.Popen([MADGRAPH_DIR + 'bin/mg5_aMC',
                                 TXT_DIR + proc_name + '.txt'])
            p.wait()

            p = subprocess.Popen([CODE_DIR + 'dtset', 
                                  OUTPUT_DIR + proc_name + DELPHES_FILE,
                                  DATASET_DIR + proc_name + str(i) + '.csv'])
            
            p.wait()
            
            ## Deleting Garbage
            #os.system('rm -rf ' + OUTPUT_DIR + proc_name)
            #os.system('rm ' + TXT_DIR + proc_name + '.txt')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        proc = EVENT_NAME
        sig = SIGNAL
    
    elif len(sys.argv) == 4:
        proc = sys.argv[1]
        sig = strtobool(sys.argv[2])
        mn2 = sys.argv[3]

    else:
        raise ValueError('Incorrect arguments. Format : python program.py proc_name is_signal')

    main(gen_proc=RUN_MADGRAPH,proc_name = proc,sig_flag = sig)
