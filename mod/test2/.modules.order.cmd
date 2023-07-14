cmd_/labhome/cmi/mi/mod/test2/modules.order := {   echo /labhome/cmi/mi/mod/test2/test2.ko; :; } | awk '!x[$$0]++' - > /labhome/cmi/mi/mod/test2/modules.order
