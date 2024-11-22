from TM import *

if __name__ == '__main__':
    print("""
    *********************************************
    ***** YOU MIGHT WANT TO READ README.txt *****
    *********************************************
    """)
    xs = sys.argv[1:]
    if len(xs) >= 1:
        maxstep = MAXSTEP
        if len(xs) == 1:
            filename = xs[0]
            input_string = raw_input()
        elif len(xs) == 2:
            filename, input_string = xs
        elif len(xs) == 3:
            filename, input_string, maxstep = xs
            maxstep = int(maxstep)
        else:
            print("too many args!!!")
            sys.exit()
        tm = load(filename)
        tm.run(input_string, maxstep)
    else:
        command_line()

        
