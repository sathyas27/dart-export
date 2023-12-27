pro point_inside_shape,cur_path,start_point,stop_point,output_filename,num_processes

;  Routine to accept a list of data points and determine if they are inside
;   of a given shape model or not.
;   Written by Tony.
;
;  Input (in some manner) is a 3xN vector giving the positions of the points
;  of interest, in (r,theta,phi)xN format
;
;  Returns a vector (dimension N) defining if the point is inside
;  the body (1) or outside (0)
;
; impact site  [r, theta, phi] = [2.6717 , 118, 16]
;
;========== ADAPT THIS SECTION TO INPUT THE DATA ======================
; The data should be floating point, named DATA_ARRAY
;  Need to be in a 3xN array, giving [r, theta, phi] for N data points
;  where r is the radial distance from the origin of the body (km)
;        theta is the angle from the North pole (0-180 deg)
;        phi is the East longitude (0-360 deg)


;NEED TO CHANGE THE PATH TO POINT TO WHEREEVER THE SHAPE MODEL DATA ARE SAVED
;cur_path = 'C:\Documents and Settings\Lev Nagdimunov\IDLWorkspace\Default\TONY_ROUTINES\'
shape = cur_path + 'tempel1_2012_cart.tab'
data_input_file = cur_path + 'positions_file.txt'
output_file = cur_path + output_filename

; Test data
;data_array = [[0.0,0,0],$ 
;          [1,90,0],$ 
;           [1,90,90],$ 
;           [5,0,0], $      
;           [1,0,0],$ 
;           [2,90,0],$ 
;           [2,90,90],$ 
;           [2,0,0],$ 
;           [3,90,0],$ 
;           [3,90,90],$ 
;           [3,0,0],$ 
;           [4,90,0],$ 
;           [4,90,90],$ 
;           [4,0,0],$ 
;           [5,90,0],$ 
;           [5,90,90]]

; Read data from file, delimiter is tab character
read_result = READ_ASCII(data_input_file, DELIMITER=string(9B))
data_array = read_result.FIELD1

;========================================================================

; Compile all necessary routines
RESOLVE_ROUTINE,['SHAPE_READ_MODEL', 'SHAPE_TRI2CONN', 'SHAPE_VERT2TVERT', $
	'VEC1_TRIANG_INTERSECT','CROSS_PRODUCT', 'DOT_PRODUCT'], /EITHER, /NO_RECOMPILE

; read in the shape model
shape_read_model,shape,vert,tri,conn
; convert to triangle array format
tvert = shape_vert2tvert(vert,tri)

; compute the min and max radii of the shape model to speed up the calculations
rad1 = sqrt(total(vert^2D,1))
radmax = max(rad1,min=radmin)

; figure out how many points there are and set up the return vector
sz = size(data_array)
inside1 = fltarr(sz[2])
shrad = fltarr(sz[2])

; split data_array into separate pieces and convert to r,lat,long  (radians)
;rvec1 = transpose(data_array[0,*])
theta1 = transpose(!dtor*(90. - data_array[0,*]))
phi1 = transpose(!dtor*data_array[1,*])

start_point = LONG(start_point)
stop_point = LONG(stop_point)
num_processes = UINT(num_processes)
;PRINT, 'Total points: ~' + string((stop_point-start_point)*num_processes)
vec1_counter = 0L

; use IDL WHERE function to rewrite this. First do all elements that should immediately be 1 or 0
; then use this loop to go only through elements that need the full calculation
; loop through each point of interest to see if it's inside or out
for i=start_point, stop_point-1  do begin
; if point is closer than the minimum nucleus radius, the point is inside
;  if rvec1[i] lt radmin then begin 
;    inside1[i] = 1
;    continue
;  endif
; if point is farther than the maximum nucleus radius, the point is outside
;  if rvec1[i] gt radmax then begin
;    inside1[i] = 0
;    continue
;  endif

; for intermediate points, need to do the full calculation

; convert point from spherical coords to cartesian coords  
  points = 10*[cos(theta1[i])*cos(phi1[i]),$
                     cos(theta1[i])*sin(phi1[i]),$
                     sin(theta1[i])]
; for each point of interest, set up a vector from 0,0,0 through the point
  vec1 = [[0.,0.,0.],[points[0:2]]]  

  REDO:
; check to see where the (extended) vector intersects the shape model
  vec1_triang_intersect,vec1,tvert,inter,xyzint=xyzint,ninter=ninter
  
  vec1_counter++
  if (vec1_counter mod 50000) eq 0 THEN PRINT, 'Points done: ~' + string(num_processes*vec1_counter)
  
; occasionally, roundoff error causes it to miss the intersection.  We know
; the vector intersects the model, since it starts out inside.  Tweak the
; position a tiny bit and re-run.
  if total(ninter) eq 0 then begin   
    vec1 = vec1+[[0.,0.,0.],[0.0001,0.0001,0.0001]]
    goto, REDO
  endif

; compute the surface distance in the direction of the vector
  shrad[i] = sqrt(total(xyzint[0:2]^2D))  

; if the vector is shorter than the surface distance, the point is inside (1)
; if it is longer, then the point is outside
;  if rvec1[i] lt shrad then inside1[i]=1 else inside1[i]=0
endfor

; Output results to file
OPENW, 3, output_file
for i=start_point, stop_point-1  do begin
	PRINTF, 3, shrad[i], FORMAT='(D0)'
ENDFOR
CLOSE, 3

return
end
