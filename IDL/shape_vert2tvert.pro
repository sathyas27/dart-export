function  shape_vert2tvert,vert,tri

; Procedure to convert a shape model vertices from a list of cartesian
; coordinates into a list of cartesian coordinates for each triangle
;
;  Input 
;    vert    real(3,nvert)   list of vertices
;    tri     int(3,ntri)     connectivity of the vertices
;
;  Output  
;    tvert   real(3,3,ntri)  cart. coordinates of the three vertices per triangle
;                              First index = XYZ
;                              Second index = vertex 1,2,3
;                              Third index = triangle number


on_error,0

if n_params() ne 2 then begin
  print, 'Usage: tvert = shape_vert2tvert(vert,tri)'
  return,-1
endif

ntri = n_elements(tri)/3
tvert = fltarr(3,3,ntri)
for i=0,ntri-1 do  begin
   tvert[0:2,0,i] = vert[0:2,tri[0,i]] 
   tvert[0:2,1,i] = vert[0:2,tri[1,i]] 
   tvert[0:2,2,i] = vert[0:2,tri[2,i]] 
endfor

return,tvert
end
