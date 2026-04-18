item(1..14).
bad(I) :- item(I), I \ 5 == 0.
allowed(I) :- item(I), not bad(I).
1 { pick(I): allowed(I) } 1.
#show pick/1.
