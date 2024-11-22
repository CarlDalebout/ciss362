# TM to recognize strings of the form ww where Sigma = {a, b}.
#
# The main idea:
#
# STAGE 1:
# First we find the middle of the string by inserting ! into the input string.
# This is done by scanning left and right, matching leftmost to rightmost
# unmatched character. The leftmost and rightmost unmatched character is 
# converted to the uppercase. For instance if the input is
#
#     $aaabbb
#
# it becomes
# 
#     $AaabbB
#
# Just before the matching process is completed we would have
#
#     $AAAbBB
#
# with the read/write heading about to read the b. Once b is replaced by B,
# the read/write head move left.
#
#     $AAABBB
#        ^
# The TM then goes into stage 2. Note that if there is an odd number of
# characters, the TM will not find a lowercase letter on scanning left; the
# TM goes into REJECT in this case.
#
# STAGE 2:
# If the character read is uppercase, this tells the TM that the matching is
# done and the midpoint is just to the right. The TM then shifts BBB to the
# right by one, inserting a ! to give:
#
#     $AAA!BBB
#
# STAGE 3:
# Next, the TM matches, character by character, the substring to the left of 
# the ! with the substring on the right of the TM. This is done by replacing
# the uppercase character by lowercase in order to indicate that the character
# is processed. For instance if the TM is about to read the 3rd character 
# from the left (not counting $):
#
#     $aa...|aa...
#        ^
# 
# If the character is B:
#
#     $aaB..|aa...
#        ^
# 
# it will overwrite the B with b:
#
#     $aab..|aa...
#         ^
#
# and remember that (states), move left the uppercase until it's past
# the ! in which case it will move passed lower case until the first upper-
# case. If the first uppercase is B:
#
#     $aab..|aaB..
#              ^
# If will then replace B with b and move past lower case until it's past !
# after which it will move past uppercase until it sees a lowercase.
# If on the other hand the first uppercase is A:
#
#     $aab..|aaA..
#              ^
#
# then we know the string is not of the form ww. 
#
# If there is a successful match, after the matching character is replaced
# by the lowercase, the read/write head moves left to look for the leftmost
# unmatched (uppercase) character in the left substring. 
# Note that on passing the ! character, if the first character is a lowercase,
# it means that the left substring is completely matched. At that point,
# we know that the string must be of the form ww.

q0,-,ACCEPT,-,S
q0,a,q1,A,R
q0,b,q1,B,R
q0,A,q4,!,R
q0,B,q5,!,R
q1,a,q1,a,R
q1,b,q1,b,R
q1,-,q2,-,L
q1,A,q2,A,L
q1,B,q2,B,L
q2,a,q3,A,L
q2,b,q3,B,L
q2,A,REJECT,A,S
q2,B,REJECT,B,S
q3,a,q3,a,L
q3,b,q3,b,L
q3,A,q0,A,R
q3,B,q0,B,R
q4,A,q4,A,R
q4,B,q5,A,R
q4,-,q6,A,S
q5,A,q4,B,R
q5,B,q5,B,R
q5,-,q6,B,S
q6,!,q6,!,L
q6,A,q6,A,L
q6,B,q6,B,L
q6,$,q7,$,R
q6,a,q7,a,R
q6,b,q7,b,R
q7,A,q8,a,R
q7,B,q9,b,R
q8,A,q8,A,R
q8,B,q8,B,R
q8,!,q10,!,R
q9,A,q9,A,R
q9,B,q9,B,R
q9,!,q11,!,R
q10,a,q10,a,R
q10,b,q10,b,R
q10,A,q12,a,L
q10,B,REJECT,B,S
q11,a,q11,a,R
q11,b,q11,b,R
q11,A,REJECT,A,S
q11,B,q12,b,L
q12,a,q12,a,L
q12,b,q12,b,L
q12,A,q12,A,L
q12,B,q12,B,L
q12,!,q13,!,L
q13,A,q6,A,L
q13,B,q6,B,L
q13,a,ACCEPT,a,S
q13,b,ACCEPT,b,S
