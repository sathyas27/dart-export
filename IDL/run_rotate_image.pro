args = command_line_args()
;print, n_elements(args)

PREF_SET, 'IDL_PATH', '<IDL_DEFAULT>:'+args[0]+':'+args[0]+'IDL_Astro_Library', /COMMIT
RESOLVE_ROUTINE,['HROT','READFITS','WRITEFITS'], /EITHER

image = READFITS('images.fits.gz', header, /NOSCALE)
output_image = image
modified_header = header
modified_header(6) = 'NAXIS4  =                   1'

; Loop over each image in cube and rotate it
FOR i=0, N_ELEMENTS(image(0,0,0,*))-1 DO BEGIN &$
        HROT, image(*,*,*,i), modified_header, new_image, new_header, 107, -1, -1, 0, MISSING=0 &$	

	; Convert from MJy/sr into W/(M^2*sr*micron), using lambda*nu=c with wavelength = 650nm
	output_image(*,*,*,i) = new_image*7.096D-6 &$
	;output_image(*,*,*,i) = SMOOTH(new_image, 5, /EDGE_TRUNCATE)*7.096D-6 &$
ENDFOR

WRITEFITS, 'images.fits.gz', output_image, header, /COMPRESS

EXIT
END
