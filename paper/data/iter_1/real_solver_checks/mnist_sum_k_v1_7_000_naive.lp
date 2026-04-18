item(1..14).
bad(I) :- item(I), I \ 2 == 0.
1 { pick(I): item(I) } 1.
:- pick(I), bad(I).
#show pick/1.
