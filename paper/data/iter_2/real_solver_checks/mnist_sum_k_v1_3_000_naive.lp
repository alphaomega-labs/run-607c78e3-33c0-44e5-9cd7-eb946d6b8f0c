item(1..12).
bad(I) :- item(I), I \ 3 == 0.
1 { pick(I): item(I) } 1.
:- pick(I), bad(I).
#show pick/1.
