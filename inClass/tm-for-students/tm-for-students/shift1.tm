#------------------------------------------------------------------------
# Shifts input string of 0s and 1s to the right by 1, inserts a blank 
# at the first position, and accepts
#
# Main idea:
# Each state (except for the start state and accept state) represents
# the character last seen. 
#
# Y. Liow
#------------------------------------------------------------------------

0,-,ACCEPT,0,S
0,0,0,0,R
0,1,1,0,R
1,-,ACCEPT,1,S
1,0,0,1,R
1,1,1,1,R
q0,-,ACCEPT,-,S
q0,0,0,-,R
q0,1,1,-,R
