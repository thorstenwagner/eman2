#!/usr/bin/env python

#
# Author: Steven Ludtke, 01/03/07 (sludtke@bcm.edu)
# Copyright (c) 2000-2007 Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#

# e2stacksort.py  01/03/07  Steven Ludtke
# This program will sort a stack of images based on some similarity criterion


from EMAN2 import *
from optparse import OptionParser
from math import *
import os
import sys


def main():
	progname = os.path.basename(sys.argv[0])
	usage = """%prog [options]
	
This program performs functions based on the idea of tracing particle orientations as they change/move around during the process of iterative Single Particle Reconstruction. It will use this information to do bad particle culling based on average total movement (in one dimensional degrees). NOT YET FULLY FUNCTIONAL.
 
Currently only works for eman1data that is generated by ptcltrace
"""

	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--eman1data",type="string",help="The name of file(s) containing eman1 output as generated by ptcltrace", default=None)
	parser.add_option("--reduce",action="store_true",default=False,help="Reduces orientations to the default asymmetric unit")
	parser.add_option("--sym",type="string",help="The symmetry to be used to nearness testing and, if it is specified, reduction", default="c1")
	
	parser.add_option("--outfilead",type="string",help="The angular deviations data file to write out, in ascii format",default=None)
	parser.add_option("--outfilead_reduce",type="string",help="The angular deviations data file to write out, in ascii format",default=None)
	parser.add_option("--bad",type="float",help="The average angular deviation defining a bad particle",default=None)
	parser.add_option("--equatorial",action="store_true",help="The average angular deviation defining a bad particle",default=False)
	
	
	(options, args) = parser.parse_args()
	
	if options.eman1data != None:
		done = False
		s = str(options.eman1data)
		filenames = []
		while not done:
			idx =  s.find(',')
			if idx == -1:
				filenames.append(s)
				done = True
			else:
				filenames.append(s[0:idx])
				s = s[(idx+1):]
				#exit(1)		
		
		print "parsing data"
		orienttracedata = []
		classtracedata = []
		for filename in filenames:
			parsedata(filename,orienttracedata,classtracedata)
			#print orienttracedata,classtracedata
			
		print "angular deviation calculation"
		angledeviationdata = calc_angular_deviation(orienttracedata)
		
		print "writing out file"
		if options.outfilead != None:
			f=open(options.outfilead,'w')
			for d in angledeviationdata:
				f.write(str(d)+"\n")
			f.close()
		
		if options.sym != "c1":
			sym = Symmetries.get(options.sym)
			print "reducing"
			reduce(orienttracedata,sym)
			print "calculation deviations again"
			angledeviationdata2 = calc_angular_deviation(orienttracedata)
			
			print "writing out again"
			if options.outfilead_reduce != None:
				f=open(options.outfilead_reduce,'w')
				for d in angledeviationdata:
					f.write(str(d)+"\n")
				f.close()
		
			good=open('good.lst','w')
			good.write("#LST\n")
			bad=open('bad.lst','w')
			bad.write("#LST\n")
			equatorial=open('equatorial.lst','w')
			equatorial.write("#LST\n")
			# now figure out which things to 
			for i in range(0,len(angledeviationdata2)):
				if angledeviationdata2[i] > options.bad:
					bad.write(str(i) + "\tstart.hed\n")
				elif angledeviationdata[i] > options.bad:
					equatorial.write(str(i) + "\tstart.hed\n")
				else:
					good.write(str(i) + "\tstart.hed\n")
					
			good.close()
			bad.close()
			equatorial.close()
	
	E2n=E2init(sys.argv)
	E2end(E2n)


def angular_deviation(t1,t2):

	v1 = Vec3f([0,0,1]*t1)
	v2 = Vec3f([0,0,1]*t2)
	t = v2.dot(v1)
	#print t
	if t > 1: 
		if t > 1.1:
			print "error, the precision is a problem, are things normalized?"
			exit(1)
		t = 1
	if t < -1:
		if t < -1.1:
			print "error, the precision is a problem, are things normalized?"
			exit(1)
		t = -1
				
	angle = acos(t)*180/pi
	
	return angle

def reduce(orienttracedata,sym):
	for particle in orienttracedata:
		for orient in particle:
			t = Transform3D(orient[1],orient[0],0.0)
			t = sym.reduce(t,0)
			d = t.get_rotation()
			orient[1] = d["az"]
			orient[0] = d["alt"]
			orient[2] = d["phi"]
	
	touching = sym.get_touching_au_transforms(False)
	
	for particle in orienttracedata:
		n = len(particle)
		for i in range(1,n):
			o1 = particle[i-1]
			o2 = particle[i]
			t1 = Transform3D(o1[1],o1[0],o1[2])
			t2 = Transform3D(o2[1],o2[0],o2[2])
		
			angle = angular_deviation(t1,t2)
			
			for t in touching:
				t2 = Transform3D(o2[1],o2[0],o2[2])*t
				
				tmp = angular_deviation(t1,t2)
				
				if tmp < angle:
					angle = tmp
					
					d = t2.get_rotation()
					particle[i][1] = d["az"]
					particle[i][0] = d["alt"]
					particle[i][2] = d["phi"]
	
				
def calc_angular_deviation(orienttracedata):
	
	data = []
	
	for particle in orienttracedata:
		n = len(particle)
		if n <= 1:
			data.append(0)
			continue
		angle = 0
		for i in range(0,n-1):
			o1 = particle[i]
			o2 = particle[i+1]
			t1 = Transform3D(o1[1],o1[0],o1[2])
			t2 = Transform3D(o2[1],o2[0],o2[2])
			angle += angular_deviation(t1,t2)

		angle /= (n-1)
		data.append(angle)

	return data

def parsedata(filename,orienttracedata,classtracedata):
	try:
		f=file(filename,'r')
	except:
		print 'couldnt read',filename
		return 0
	lines=f.readlines()

	for line in lines:
		s = str.split(str.strip(line))
		if s[1] == '********':
			fs_idx = s[0].find('.') # fullstop idx
			if fs_idx == -1:
				print "error, the format of the input file is unexpected, couldn't find a number followed by a fullstop in",s[0]
			else:
				idx = s[0][0:fs_idx]
				n = int(idx)+1
				if len(orienttracedata) < n:
					for i in range(len(orienttracedata),n):
						orienttracedata.append([])
				if len(classtracedata) < n:
					for i in range(len(classtracedata),n):
						classtracedata.append([])
		elif s[1] == '->':
			idx = str.find(s[3],',')
			alt = float(s[3][1:idx])
			az = float(s[3][idx+1:len(s[3])-1])
			orienttracedata[n-1].append([alt,az,0])
			cls = int(s[2])
			it = int(s[0])
			classtracedata[n-1].append([it,cls])
					

	
if __name__ == "__main__":
    main()
