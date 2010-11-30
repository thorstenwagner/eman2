#!/usr/bin/env python
#
# Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
# Copyright (c) 2000-2006 Baylor College of Medicine
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston MA 02111-1307 USA


import eman_mpi_c		# these are the actual C functions. We map these selectively to the python namespace so we can enhance their functionality
import sys
from cPickle import dumps,loads
from zlib import compress,decompress
from struct import pack,unpack

# These functions don't require mapping
mpi_init=eman_mpi_c.mpi_init
mpi_comm_rank=eman_mpi_c.mpi_comm_rank
mpi_comm_size=eman_mpi_c.mpi_comm_size
mpi_barrier=eman_mpi_c.mpi_barrier
mpi_finalize=eman_mpi_c.mpi_finalize

def mpi_send(data,dest,tag):
	"""Synchronously send 'data' to 'dest' with tag 'tag'. data may be any pickleable type.
	Compression and pickling will be performed on the fly when deemed useful. Note that data duplication
	in memory may occur."""
	if isinstance(data,str):
		if len(data)>256 : eman_mpi_c.mpi_send("C"+compress(data,1),dest,tag)
		else : eman_mpi_c.mpi_send("S"+data,dest,tag)
	else :
		d2x=dumps(data,-1)
		if len(d2x>256) : eman_mpi_c.mpi_send("Z"+compress(d2x,1),dest,tag)
		else : eman_mpi_c.mpi_send("O"+d2x,dest,tag)

def mpi_recv(src,tag):
	"""Synchronously receive a message from 'src' with 'tag'. If either source or tag is negative, this implies
	any source/tag is acceptable."""
	
	msg=eman_mpi_c.mpi_Recv(src,tag)
	if msg[0]=="C" : return decompress(msg[1:])
	elif msg[0]=="S" : return msg[1:]
	elif msg[0]=="Z" : return loads(decompress(msg[1:]))
	elif msg[0]=="O" : return loads(msg[1:])
	else :
		print "ERROR: Invalid MPI message. Please contact developers. (%s)"%msg[:128]
		sys.exit(1)

	return None		# control should never reach here
	
def mpi_bcast_send(data):
	"""Unlike the C routine, in this python module, mpi_bcast is split into a send and a receive method. Send must be 
	called on exactly one core, and receive called on all of the others. This routine also coordinates transfer of
	variable length objects."""

	data=compress(dumps(data,-1),1)
	
	l=pack("I",len(data))
	eman_mpi_c.mpi_bcast(l)
	
	eman_mpi_c.mpi_bcast(data)
	
def mpi_bcast_recv(src):
	"""Unlike the C routine, in this python module, mpi_bcast is split into a send and a receive method. Send must be 
	called on exactly one core, and receive called on all of the others. This routine also coordinates transfer of
	variable length objects. src is the rank of the sender"""
	
	l=eman_mpi_c.mpi_bcast(4,src)
	
	return loads(decompress(eman_mpi_c.mpi_bcast(l,src)))
