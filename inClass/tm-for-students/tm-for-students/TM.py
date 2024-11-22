"""
A simple Turing machine.Type ? for help. The rest is clear.
Yihsiang Liow
"""
R = 'R'
L = 'L'
S = 'S'
ACCEPT = 'ACCEPT'
REJECT = 'REJECT'
HALT = [ACCEPT,REJECT]
MARKER = '$'
START = 'q0'
BLANK = '-'
MAXSTEP = 100

import random; random.seed()
import sys
import glob

def chatty(mood):
    if mood == 'ANNOYED':
        return random.choice(["Trying to crash this machine??!",
                              "Are you trying to kill me?!?",
                                  ])
    elif mood == 'WARNING':
        return random.choice(["Don't be too adventurous ...",
                              "Don't you think that's kinda dangerous?!? ...",
                              "Help someone ... this fella is trying to kill me!!!",
                              "Don't do that again!!!",
                              ])
    elif mood == 'CONFUSED':
        return random.choice(["I'm totally confused ...",
                              "I'm lost ...",
                              "I'm so totally lost ...",
                              "Don't fry my CPU ...",
                              "Please don't screw around with my CPU ...",
                              "I can't correct typos ...",
                              ])
    elif mood == 'CONGRATULATORY':
        return random.choice(["Hurray!",
                              "Yippie!",
                              ])
    
class TM:
    
    def __init__(self):
        self.__Q = []
        self.__Sigma = []
        self.__Gamma = []
        self.__delta = {}
        
    def insert(self,q0,a,q1,b,D):
        self.__delta[(q0,a)] = (q1,b,D)
        
    def __repr__(self):
        items = list(self.__delta.items())
        items.sort()
        alist = []
        Q = [ACCEPT, REJECT]
        #SIGMA = []
        GAMMA = ['-']
        for k, v in self.__delta.items():
            q0, a = k
            q1, b, d = v
            if q0 not in Q: Q.append(q0)
            if q1 not in Q: Q.append(q1)
            if b not in GAMMA: GAMMA.append(b)
        Q.sort()
        Q = ', '.join(Q)
        GAMMA.sort()
        GAMMA = ', '.join(GAMMA)
        print("states = {%s}" % Q)
        #print "sigma = {%s}" % SIGMA
        print("gamma = {%s}" % GAMMA)
        print("transitions:")
        for item in items:
            alist.append( ("%s,%s," % item[0]) + "%s,%s,%s" % item[1])
        return "\n".join(alist)
    
    def run(self, input_string, maxstep=1000, verbose=True):
        """
        Returns a list of instantaneous descriptions on running "input_string"
        "maxstep" steps. if "verbose" is True, messages will be printed to
        show progress of computation.

        An ID xqy (x,y are strings and q is a state) is modeled by a three
        variables left=x, q, right=y. 
        """

        if verbose:
            print("(For readability, state is enclosed in <>).")
        if input_string == '': input_string = BLANK
        
        left, q, right = MARKER, START, input_string
        ID = "STEP %s: %s<%s>%s" % (0, left, q, right)
        if verbose: print(ID, end='')
        IDs = [ID]
        accept = False
        
        for step in range(maxstep):    
            if right == '': right = BLANK
            a = right[0] # read character
            try:
                if verbose: print(" ... about to apply delta(%s,%s) =" % (q,a), end='') 
                q,a,D = self.__delta[(q,a)]
                if verbose: print("(%s,%s,%s) ... " % (q,a,D))
                
                right = a + right[1:] # overwrite character

                # Move the read/write head
                if D == 'L':
                    left, right = left[:-1], left[-1]+right
                elif D == 'R':
                    left, right = left+right[0], right[1:]

                # Store ID in IDs
                ID = "STEP %s: %s<%s>%s" % (step + 1, left, q, right)
                if verbose: print(ID, end='')
                IDs.append(ID)

                if q == ACCEPT: accept = True
                
            except:
                if verbose: print("... oh no ... transition not found ... ", end='')
                if q == ACCEPT:
                    if verbose: print("that's ok ... you reached ACCEPT.", end='')
                    accept = True
                else:
                    # Either q == REJECT, or by default no transition
                    # *implies* q == REJECT 
                    if verbose: print("CRASH! You did not reach ACCEPT.", end='')
                break
            
            if q in HALT:
                if verbose: print("... Halting the machine ...", end='')
                break
        
        if verbose:
            print()
            print("Total number of computations:", step+1)
            print("Tape: '%s%s'" % (left,right))
            print("Final state: '%s'" % q)
            
        return IDs
            

def load(filename=None, verbose=False):
    if not filename:
        if verbose:
            print("WARNING: Transitions will be added to current TM")
            print("Here are the available TMs in the current directory/folder:")
            fs = glob.glob("*.tm")
            fs.sort()
            for f in fs: print("   ", f)
            print("Enter filename > ", end='')
        filename = input("")
        filename = filename.strip()
        if filename == '': return 
    if not filename.endswith('.tm'): filename = "%s.tm" % filename
    try:
        tm = TM()
        f = open(filename,"r")
        while 1:
            input_ = f.readline()
            if input_ == "": break
            input_ = input_[:-1]
            if verbose: print(input_)
            input_ = input_.split('#')[0]
            input_ = input_.strip()
            if input_ == '': continue
            q0,a,q1,b,D = input_.split(",")
            tm.insert(q0,a,q1,b,D)
        f.close()

        if verbose:
            print("Done! ... here's the TM:")
            print(tm)
    except:
        if verbose:
            print("Error loading/reading " + filename)
        raise
    return tm


def save(tm):
    try:
        filename = input("Enter filename (do not enter .tm, enter nothing to skip, existing file overwritten!) > ")
        filename = filename.strip()
        if filename == '': raise exception
        filename += ".tm"
        f = open(filename,"w")
        f.write(str(tm) + "\n")
        f.close()
        print("TM is saved to %s ..." % str(filename), chatty("CONGRATULATORY"))
    except:
        if filename != '':
            print("Error saving TM to file %s." % filename, chatty('CONFUSED'))


def command_line():
    help = "?: help\n" +\
           "q: quit\n" +\
           "v: plant a virus\n" +\
           "c: clear TM\n" +\
           "p: program TM\n" +\
           "s: save TM\n" +\
           "l: load TM\n" +\
           "d: display TM\n" +\
           "r: run TM\n" +\
           "(Yeah I know ... lousy interface and near-zero features)"
    print("Turbo Turing version 0.000000000001")
    print("... Use the purest programming language ever!")
    print("... Build your own Turing machine!!")
    print("... It's EVEN lower level than assembly!!! Yeah!")
    print() 
    print("To run in your shell: python TM.py [filename.tm] [input] [maxsteps]")
    print() 
    print(help)
    tm = TM()

    maxstep = MAXSTEP
    
    while 1:
        try:
            input_ = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit()
            
        if input_ in ['h','?']:
            print(help)
        elif input_=='':
            continue
        elif input_ in ['c','clear']:
            tm = TM()
        elif input_ in ['s','save']:
            save(tm)
        elif input_ in ['l','load']:
            tm = load(verbose=True)
        elif input_ in ['q','quit']:
            break
        elif input_ == 'd':
            print(tm)
        elif input_ == 'p':
            print(r"""
General:
    * You can use any string for Sigma, Gamma, States except for special
      characters mentioned below such as for instance -.
    * Do not enter quotes (single or double).
    * When you run the TM, the input tape is initialized with $ as the first
      character. The input is placed immediately on the right of the $.
      When you bootup the TM, the read/write head is pointing to the character
      immediately to the right of $ marker.
Sigma:
Gamma:
    * The space is always - (the dash).
States:
    * The initial state is always q0
    * The accept state is ACCEPT
    * The reject state is REJECT
Directions:
    * The TM understands three directions L, S, R (left, stay, right)
Transitions:
    * Enter q2,0,q3,1,R for transition delta(q2,0) = (q3,1,R).
    * Transitions not entered will land in REJECT.
Comment:
    * # is used for line comments - so don't use it as a character in your TM!
To exit:
    * When you're done writing your TM, enter an empty string.
""")
            print("Previous transitions are retained.")
            print("If you want to clear the TM, go back to main prompt and type c.")
            
            print()
            
            while 1:
                input_ = input("program > ")
                input_ = input_.strip()
                if input_=="": break
                try:
                    q0,a,q1,b,D = input_.split(",")
                    q0 = q0.strip()
                    a = a.strip()
                    q1 = q1.strip()
                    b = b.strip()
                    D = D.strip()
                    if D not in ['L','S','R']: raise exception
                    tm.insert(q0,a,q1,b,D)
                except:
                    print("Invalid transition '" + input_ + "'. " + chatty("ANNOYED"))
        elif input_ in ['r','run']:
            run(tm)
        elif input_ == 'v':
            print(chatty('WARNING'))
        else:
            print("Huh??? What's '%s'???" % input_, chatty('CONFUSED'))



def run(tm):
    try:
        print("""
The input is always initialized with a $ marker.
The input string that you type below is placed to the right of the $ marker.
Initially, your TM does NOT point to the $.
Instead, it will point to the character to the right of the $, i.e., the first character of your input below.
For instance if you enter aabb for input below, then
the input tape will have $aabb with the TM's read/write
head pointing to the first a.
""")
        input_string = input( "Enter input string: " )
        maxstep = 1000
        maxstep = int(input( "Enter maximum number of steps (default %s): " % maxstep))
    except:
        pass
    IDs = tm.run(input_string,maxstep)
    
                
if __name__ == "__main__":
    print("Run runthis.py")
