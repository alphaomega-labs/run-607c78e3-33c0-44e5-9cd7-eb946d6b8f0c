item(1..20).
bad(I) :- item(I), I \ 4 == 0.
1 { pick(I): item(I) } 1.
:- pick(I), bad(I).
#show pick/1.
