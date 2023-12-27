args = command_line_args()
;print, n_elements(args)

PREF_SET, 'IDL_PATH', args[0]+':<IDL_DEFAULT>', /COMMIT

RESOLVE_ROUTINE,['point_inside_shape']
point_inside_shape, args[0], args[1], args[2], args[3], args[4]

EXIT
END