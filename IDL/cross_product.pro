function cross_product,vect1,vect2,angle=angle1,unit=unit,magc=magc

;  function to compute the cross product of two vectors
;
;   Input:
;     vect1(3,n)     real    first vector in the cross product
;     vect2(3,n)     real    second vector in the cross product
;
;   Output:
;     crossprod(3,n) real    cross product of the two vectors
;
;   Optional output
;     angle          real    angle between the two vectors (radians)
;     unit           flag    if set, then return a unit vector
;     magc           real    magnitude of the resulting vector

on_error,2

if n_elements(vect1) mod 3 ne 0 then return, -1
if n_elements(vect2) mod 3 ne 0 then return, -2

; check the size of the arrays; if one is a vector, make it into an array
if n_elements(vect1) gt n_elements(vect2) then begin
  vect1a = vect1
  nvect = n_elements(vect1)/3
  vect2a = replicate(1,nvect) ## reform(vect2[0:2])
endif else if n_elements(vect2) gt n_elements(vect1) then begin
  vect2a = vect2
  nvect = n_elements(vect2)/3
  vect1a = replicate(1,nvect) ## reform(vect1[0:2])
endif else begin
  nvect = n_elements(vect2)/3
  vect1a = vect1
  vect2a = vect2
endelse

crossprod=dblarr(3,nvect)

crossprod(0,*) = vect1a(1,*)*vect2a(2,*)- vect1a(2,*)*vect2a(1,*)
crossprod(1,*) = vect1a(2,*)*vect2a(0,*)- vect1a(0,*)*vect2a(2,*)
crossprod(2,*) = vect1a(0,*)*vect2a(1,*)- vect1a(1,*)*vect2a(0,*)

magc = sqrt(total(1.0*crossprod*crossprod,1))
magc = magc*(magc ne 0.) + 1.*(magc eq 0.)
dp = dot_product(vect1a,vect2a)

if keyword_set(unit) then begin 
  crossprod[0,*] = crossprod[0,*]/magc
  crossprod[1,*] = crossprod[1,*]/magc
  crossprod[2,*] = crossprod[2,*]/magc
endif

return,crossprod
end
