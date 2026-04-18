item(1..12).
bad(I) :- item(I), I \ 2 == 0.
allowed(I) :- item(I), not bad(I).
1 { pick(I): allowed(I) } 1.
#show pick/1.
