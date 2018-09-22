import sys, os
import ast
import re

import pathlib2

def if_regex(regex):
	if regex:
		print("    {} : {}".format(i+1, line))
		var  = regex.group(1)
		print("{}".format(var))
		
		return var
	else:
		return False

cur = pathlib2.Path('.')

# re_import = re.compile(r'from .* import (QtCore|QtGui)')
re_core_import = re.compile(r'from .* import .*(QtCore)')
re_gui_import  = re.compile(r'from .* import .*(QtGui)')
re_core_usage = re.compile(r'QtCore\.(\w+)')
re_gui_usage  = re.compile(r'QtGui\.(\w+)')

files = [
		 'libpyEM/qtgui/empmwidgets.py',
		 'libpyEM/qtgui/embrowser.py',
		 ]

for p in (pathlib2.Path(f) for f in files):
# for p in (p for p in cur.glob('**/*.py') if \
# 		  not str(p).startswith('sparx') \
# 		  and p.parent != pathlib2.Path(__file__).parent):
	with p.open() as fin:
		lines = fin.readlines()
	print(p)
	modulesCore = set()
	modulesGui  = set()
	for i in range(len(lines)):
		line = lines[i].strip()
		if len(line)>0 and line[0] == '#':
			continue
		gs_core_import = re_core_import.search(line)
		gs_gui_import = re_gui_import.search(line)
		gs_core_usage = re_core_usage.search(line)
		gs_gui_usage = re_gui_usage.search(line)
		
		if if_regex(gs_core_import):
			line_core = i
		if if_regex(gs_gui_import):
			line_gui = i
		
		module = if_regex(gs_core_usage)
		if module:
			modulesCore.add(module)
		
		module = if_regex(gs_gui_usage)
		if module:
			modulesGui.add(module)

			# modulesCore
		# if gs:
		# 	# line_num[] = 
		# 	print("    {} : {}".format(i+1, line))
		# 	var  = gs.groups()
		# 	# args = gs.group(2)
		# 	print("{}".format(var))
		# 	# # print("{} | {}".format(var, args))
		# 	# args = [s.strip() for s in args.split(',')]
		# 	# # if any([False for s in args if s == 'QString']):
		# 	# # 	signals[var] = args
		# 	# signals["{}.{}".format(cur_class, var)] = args
	
	print("modulesCore: {}".format(modulesCore))
	print("modulesGui: {}".format(modulesGui))
	# print(line[line_core])
	# print(line[line_gui])
	print(lines[line_core])
	print(lines[line_gui])

	lines[line_core] = lines[line_core].replace('QtCore', ", ".join(modulesCore))
	print(lines[line_core])

	lines[line_gui]	 = lines[line_gui].replace('QtGui',  ", ".join(modulesGui))
	print(lines[line_gui])
