TM
(for python2)
Y Liow

Email me (yliow@ccis.edu) if you see bugs, have suggestions for improvements,  or wish to donate (in multiples of $1M) to Liow's Free Software Foundation.

There are several examples. They all end with ".tm". For instance:
- duplicate.tm
- moveright.tm
- shift1.tm
- ww.tm

To run in command line:

> python runthis.py ww              You have to enter the input
> python runthis.py ww abab         
> python runthis.py ww abab 100     The maxstep is set to 100

For convenience, you need not specify all transitions although technically TMs
are deterministic. If the TM attempts to use a transition that is not specified,
the output will tell you that the TM "crashes". When you see such a message, 
you can then interpret that as going into the REJECT state.

Also, you only specify transitions: for your convenience, 
you do not specify Sigma. 
You just have to be careful that you do not put invalid characters on the
input tape. If you do, the TM will report it crashes.

The space is -.

Use ACCEPT for the accept state and REJECT for the reject state.

q0 will always be the start state.
