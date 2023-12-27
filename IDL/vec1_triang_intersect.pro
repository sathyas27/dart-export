pro vec1_triang_intersect,vect,tvert,inter,xyzint=xyzint,ninter=ninter,facet=facet

;  Given a single vector and multiple triangles, compute whether or not the vector
;  intersects any of the triangles
;
;  Uses an algorithm derived in TF Science notebook (March 2005 through...), page 186
;
;  Input
;    vect    real(3,2)   Two points, in cartesian coords, defining the vector
;                        First index is XYZ of the base, second index is a
;                        point in the direction of the vector
;    tvert   real(3,3,n) Three points (cart coords) defining the triangle vertices
;                        first index is XYZ, second index is each vertex,
;                        third index is for multiple triangles
;
;  Output:
;    inter   int(n)      Result
;                          -9   Triangle is degenerate (a line or point)
;                          -2   Vector is parallel to triangle plane
;                          -1   Vector is in the triangle plane
;                           0   Vector does not intersect triangle
;                           1   Vector intersects triangle at an edge or vertex
;                           2   Vector intersects triangle in a unique point
;
;  Optional output:
;    xyzint  real(3,n)   Cartesian coordinate at the point of intersection
;    ninter  int(2)      Count of unique intersections (index 0) and
;                        edge/vertex intersections (index 1)
;    facet   int(2)      index number of the facet(s) intersected or edged

if n_params() ne 3 then begin
   print, 'Calling sequence:'
   print,'    vec1_triang_intersect, vect, tvert, inter [, xyzint=xyzint]'
   return
endif

; define a small number to avoid comparisons to zero
smnum = 0.000001    ; 0.0001 seems to work well for catching the relevant points 

; determine how many triangles are being looked at
ntri = n_elements(tvert)/9

; compute vectors along two sides of the triangle
side1 = fltarr(3,ntri)
side2 = side1
side1[0:2,*] = tvert[0:2,1,*] - tvert[0:2,0,*] 
side2[0:2,*] = tvert[0:2,2,*] - tvert[0:2,0,*] 

; compute the normal to each triangle
tnorm = cross_product(side1,side2,magc=tnormmag)

; save the indices of triangles that are degenerate
tdeg = where (tnormmag eq 0)

; First, see if the vector is parallel to the triangle:

; compute the direction of the vector of interest
dir = vect[*,1] - vect[*,0] 
dirmag = sqrt(total(dir^2D))

; compute the zero point, relative to each triangle
zeropt = fltarr(3,ntri)
tvert0 = reform(tvert[*,0,*])
vect0 = replicate(1,ntri) ## reform(vect[*,0])
zeropt[0:2,*] = vect0[0:2,*] - tvert0[0:2,*]   
zeromag = sqrt(total(zeropt^2D,1))
;print,'tvert0 = ',tvert0[*,0]
;print,'vect0=   ',vect0[*,0]
;print,'zerpt=   ',zeropt[*,0]

; compute the dot product of the triangle normal and the vector base
nrmdotzer = -1.*dot_product(tnorm,zeropt);/tnormmag/zeromag
; compute the dot product of the triangle normal and the vector direction
nrmdotdir = dot_product(tnorm,dir);/tnormmag/dirmag
;print,tnorm[*,0]
;print,zeropt[*,0]
;print,dir[*,0]
;print,-1*nrmdotzer[0]
;print,nrmdotdir[0]

; check to see if the vector and triangle are parallel
abs_result = abs(nrmdotdir/tnormmag/dirmag)
tpar = where(abs_result lt smnum)
; check to see if the parallel vector is in the triangle plane
tplan = where((abs_result lt smnum) and (abs(nrmdotzer/tnormmag/zeromag) lt smnum))

; For vectors that aren't parallel, see if they cross the plane inside
; or outside of the triangle

; check to see if the array points away from the triangle
divide_result = nrmdotzer/nrmdotdir
taway = where(divide_result lt 0.)

; compute the intersection point of the vector and the plane
;print,dir[*,0]
ray0 =   dir # transpose(divide_result)
ipt =  vect0 + ray0
;print,nrmdotzer[0,*]/nrmdotdir[0,*]
;print,ray0[*,0]
;print,ipt[*,0]

; determine whether the intersection is inside, using Dan Sunday method
uu = dot_product(side1,side1)
uv = dot_product(side1,side2)
vv = dot_product(side2,side2)
w = ipt - tvert0

wu = dot_product(w,side1)
wv = dot_product(w,side2)
denom = uv*uv - uu*vv

s = (uv*wv - vv*wu)/denom
t = (uv*wu - uu*wv)/denom

; **** ROundoff error often comes from S+T getting bigger than 1 - check that
;    if there are problems (wu and wv may be very small - use them to 
;    adust smnum?)
; determine if the intersection is outside the triangle...
tout = where((s lt 0) or (t lt 0.) or (s gt 1.) or (s+t gt 1.))
; ... or on the edge or vertex of a triangle
tedge = where(((s lt smnum) or (t lt smnum) or (s+t eq 1.)) and  $
              ((s le 1.+smnum) and (t le 1.+smnum) and $
               (s gt -smnum) and (t gt -smnum)))

;ipos = 11319
;for i=-720,720,180 do print,ipos+i,s[ipos+i],t[ipos+i]
;for i=-3,3 do print,ipos+i,s[ipos+i],t[ipos+i]


;smag = s+t
;spos = where((s lt 2) and (t lt 2) and  (smag gt 0) and (smag lt 2))
;snum = n_elements(spos)
;for i=0,snum-1  do print,spos[i],s[spos[i]],t[spos[i]]
;print,n_elements(tout)

; create the intersection array to be returned
inter = intarr(ntri)*0 + 2
; set the previously calculated values to identify their character
if total(tdeg)  gt 0 then inter[tdeg]  = -9
if total(tpar)  gt 0 then inter[tpar]  = -2
if total(tplan) gt 0 then inter[tplan] = -1
if total(tedge) gt 0 then inter[tedge] =  1
if total(taway) gt 0 then inter[taway] =  0
if total(tout)  gt 0 then inter[tout]  =  0

; determine the number of triangles intersected
n1 = where(inter eq 1, ninter1)
n2 = where(inter eq 2, ninter2)
n1 = where(inter eq 1 or inter eq 2, ninter)
facet = n1

; compute the cartesian coords of each intersection point 
if ninter ne 0 then begin
  xyzint = fltarr(3,ninter)
  for i=0,ninter-1 do $
     xyzint[0:2,i] = tvert0[0:2,n1[i]] + $
        s[n1[i]] # side1[0:2,n1[i]] + $
        t[n1[i]] # side2[0:2,n1[i]] 
endif else xyzint=0.

; Record the number of unique and edge/vertex intersections for return
ninter = [ninter2,ninter1]

return
end


