item(1..13).
bad(I) :- item(I), I \ 6 == 0.
1 { pick(I): item(I) } 1.
:- pick(I), bad(I).
#show pick/1.
