pro shape_read_model, filename, vert, tri, conn, skipline=skipline

; Read triangular plate model data file into named variables
;
; input:
;   filename: the data file which contains the triangular plate
;             model of the DPS standard format
; output:
;   vert(3,nvert)     float   array of vertex coordinates 
;   tri(3,ntri)       ulong   array of connections for triangular plates
;   conn(3*ntri)      ulong   vector containing connectivity in IDL format
;   skipline          int     number of header lines to skip  
;
;  Revisions:
;                Original written by J-Y Li
;     02/06/09   Adapted to TF standards 
;

if n_params() ne 4 then begin
  print, 'Usage: shape_read_model, filename, vert, tri, conn [, skipline=skipline]'
  return
endif

; check to get the number of header lines to skip
if size(skipline,/type) eq 0 then skipline=0

; set default values for variables
str = ''
nvert = 0ul  &  ntri = 0ul
x = 0.  &  y = x  &  z = x
i1 = 0ul  &  i2 = i1  &  i3 = i1

; open the shape model data file and read in the header
openr, infile, filename, /get_lun
for i=0,skipline do readf, infile, str
while (strtrim(str,2) eq '') or (strmid(str,0,1) eq '#') do readf, infile, str

; read the number of vertices and plates from the string
reads, str, nvert, ntri
vert = fltarr(3, nvert)
tri  = ulonarr(3, ntri)

; read in the vertex values into the vertices array
for i=0ul, nvert-1 do begin
  readf, infile, str
  if (strtrim(str,2) ne '') and (strmid(str,0,1) ne '#') then begin
    reads, str, x, y, z
    vert[0,i] = x
    vert[1,i] = y
    vert[2,i] = z
  endif
endfor

; read in the plate values into the triangles array
for i=0ul, ntri-1 do begin
  readf, infile, str
  if (strtrim(str,2) ne '') and (strmid(str,0,1) ne '#') then begin
    reads, str, i1, i2, i3
    tri[0,i] = i1
    tri[1,i] = i2
    tri[2,i] = i3
  endif
endfor

; check to see if the triangles are zero based?
if min(tri) ge 1 then tri = tri-1

conn = shape_tri2conn(tri)

close, infile
free_lun, infile

end
