#------------------------------------------------------------------------
# Duplicates a string of a's and b's and halts in accept state
#
# Main idea:
# Scan left to right, marking each 'a' as read with 'A' and 'b' as
# read with 'B', move to the first rightmost blank and write either
# '0' if 'a' was read or '1' if 'b' was read. Once input string
# is completely marked, replace 'A' with 'a', 'B' with 'b', '0' with 'a'
# and '1' with 'b'. 
#
# Y. Liow
#------------------------------------------------------------------------

q0,a,q1,A,R
q0,b,q3,B,R
q0,0,q4,0,R
q0,1,q4,1,R
q0,-,q8,-,L
q1,a,q1,a,R
q1,b,q1,b,R
q1,0,q1,0,R
q1,1,q1,1,R
q1,-,q2,0,L
q2,a,q2,a,L
q2,b,q2,b,L
q2,0,q2,0,L
q2,1,q2,1,L
q2,A,q0,A,R
q2,B,q0,B,R
q3,a,q3,a,R
q3,b,q3,b,R
q3,0,q3,0,R
q3,1,q3,1,R
q3,-,q2,1,L
q4,0,q4,0,R
q4,1,q4,1,R
q4,-,q5,-,L
q5,0,q6,-,L
q5,1,q7,-,L
q6,0,q6,a,L
q6,A,q6,a,L
q6,1,q7,a,L
q6,B,q7,a,L
q6,$,ACCEPT,a,S
q7,0,q6,b,L
q7,A,q6,b,L
q7,1,q7,b,L
q7,B,q7,b,L
q7,$,ACCEPT,b,S
q8,$,ACCEPT,-,S