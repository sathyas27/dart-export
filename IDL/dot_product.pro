function dot_product,vect1,vect2

;  function to compute the dot product of two vectors
;
;   Input:
;     vect1(3,n)    real    first vector in the dot product
;     vect2(3,n)    real    second vector in the dot product
;
;   Output:
;     dotprod(n)    real     dot product of the two vectors
;
;   Optional output (Taken out because it is extremely slow)
;     angle1(n)     real     angle between the two vectors (radians)

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
  vect1a = vect1
  vect2a = vect2
endelse

vect1a = DOUBLE(vect1a)
vect2a = DOUBLE(vect2a)

dotprod = total(vect1a*vect2a,1)

;mag1 = sqrt(total(1.0*vect1a*vect1a,1))
;mag2 = sqrt(total(1.0*vect2a*vect2a,1))
;magdot = abs(dotprod)

; avoid a roundoff error causing a cos(angle)>1.0
;re = where(mag1*mag2 lt magdot,count) 
;if count ne 0 then dotprod[re] = dotprod[re]/magdot[re]*mag1[re]*mag2[re]

;angle1 = acos(dotprod/mag1/mag2)

return,dotprod
end
