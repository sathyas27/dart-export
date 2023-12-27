function shape_tri2conn, tri

; Function that converts the connectivity array from the triangle 
; mode to the full mode (as in IDL convention).
; This simply prepends an element in the connectivity array that 
; tells IDL that each plate has 3 vertices (triangle)
;
;              Originally written by JYL
;   02/06/09   Adapted to TF format

; create a variable of size (4,ntri)
conn = lonarr(4, n_elements(tri)/3)

; set the first element to 3 for all plates
conn[0,*] = 3
conn[1:3,*] = tri[*,*]

; return the array in a single vector format
return, reform(conn, n_elements(conn))
end

