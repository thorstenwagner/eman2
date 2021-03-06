#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
# Muyuan Chen 12/2014
# Fit beta sheets using pathwalker results

from past.utils import old_div
from builtins import range
import EMAN2
from EMAN2 import *
import random
import math
import numpy as np

def read_pdb(filename):
	
	points = {}
	atomnumber=np.array([])
	pdbfile = open(filename, "r")
	lines = pdbfile.readlines()
	pdbfile.close()

	chainnum=1
	for line in (i for i in lines if i.startswith("ATOM  ")):
		lchain=line[21].strip() or None
		break
	
	
	
	count = 0
	for line in (i for i in lines if i.startswith("ATOM  ")):
		#latomtype = line[12:15].strip()
		nchain = line[21].strip() or None			
		if nchain != lchain:
			chainnum+=1
			pos=[-1,-1,-1]
			points[count]=(pos)
			count+=1
			atomnumber=np.append(atomnumber,0)
		
		atomnumber=np.append(atomnumber,int(line[22:27]))
		pos = [float(line[30:38].strip()), float(line[38:46].strip()), float(line[46:54].strip())]
		points[count] = (pos)
		count += 1
		lchain=nchain
		
	pts=np.empty((count,3),float)
	for i in range(count):
		pts[i,:]=points[i]
	
	header=[i for i in lines if i.startswith("HELIX  ")]
	return pts,count,atomnumber,header

def write_pdb(filename,ncent,color,atomnumber,sheets,header):
	shp=ncent.shape
	if color==None:
		color=np.zeros(shp[0],float)
	out = open(filename,"w")
	for i in header:
		out.write(i)
		
	nchn=65
	chain = chr(nchn)
	for i in sheets:
		sht=sheets[i]
		out.write("SHEET %4d   A 1 ALA A%4d  ALA A%4d  0\n"%(i+1,sht[0],sht[1]))
		
	count=0
	for atom in range(shp[0]):
		if (ncent[atom,0]<0):
			out.write("""TER  %6d      ALA %s%4d\n"""%(count, chain, atom))
			nchn+=1
			chain=chr(nchn)
			continue
		out.write(
			"ATOM %6d  CA  ALA %s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f     S_00  0\n"
			%(atomnumber[atom], chain,atomnumber[atom] ,ncent[atom,0], ncent[atom,1], ncent[atom,2], 1, color[atom]) 
			)
		count+=1
	out.write("""TER  %6d      ALA %s%4d\n"""%(shp[0], chain, atom))
	out.write("END")
	out.close()
	
def filter1d(pts, fun):
	shp=pts.shape
	n=shp[0]
	d=shp[1]
	m=len(fun)
	npt=np.zeros((n,d),float)
	for i in range(n):
		for j in range(m):
			nj=j-old_div((m-1),2)
			if i+nj<0 or i+nj>=n:
				continue
			else:
				for k in range(d):
					npt[i,k]=npt[i,k]+pts[i+nj,k]*fun[j];
	print(npt)				
	return npt

		
def gaussianpdf(x,sig):
	return (old_div(1.0,(sig*sqrt(2.0*pi))))*exp(old_div(-(x*x),(2.0*sig*sig)))


def main():
	
	usage = """ e2pwsheetfit.py --pdbin <input file> --output <output file> [options]
	Fit beta sheets on a backbone model generated by e2pathwalker.py
	"""
	parser = EMAN2.EMArgumentParser(usage=usage,version=EMAN2.EMANVERSION)
	parser.add_argument("--output", type=str,help="Output pdb file")
	parser.add_argument("--pdbin", type=str,help="pdb file for input",default=None)
	parser.add_argument("--nsht", type=int,help="max number of beta sheet strains",default=5)
	parser.add_argument("--minlen", type=int,help="minimum length of a beta sheet strain",default=5)
	parser.add_argument("--cutoff", type=float,help="cutoff threshold for sheet score. program will stop when the next highest score is lower than cutoff*std+mean",default=1)
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-1)
	(options, args) = parser.parse_args()
	logid=E2init(sys.argv)
	
	pts,na,atomnumber,header=read_pdb(options.pdbin)
	
	
	#calculate angle between bond pairs
	ang=np.zeros((na,na),float)
	for i in range(1,na-1):
		for j in range(1,na-1):
			p1=pts[i-1,:]
			p2=pts[i+1,:]
			q1=pts[j-1,:]
			q2=pts[j+1,:]
			l1=p2-p1
			l2=q2-q1
			ang[i,j]=abs(old_div(np.dot(l1,l2),(np.linalg.norm(l1)*np.linalg.norm(l2))))
	
	#calculate score based on the angle between neighbor bonds
	score=np.zeros(na,float)
	dist=np.empty(na,float)
	nnb=10 # number of neighbors considered
	for i in range(na):
		for j in range(na):
			dist[j]=np.linalg.norm(pts[i,:]-pts[j,:])
		srti=np.argsort(dist)
		for j in range(nnb):
			d=dist[srti[j]]
			wt=gaussianpdf(d,5)
			score[i]+=ang[i,srti[j]]*wt
	#print score
	maxsheet=options.nsht # max number of sheet chains
	sheets={}
	insht=np.zeros(na,int)
	for nsheet in range(maxsheet):
		nonsht=np.where(insht==0)
		nonsht=nonsht[0]
		topi=np.where(score>np.average(score[nonsht])+np.std(score[nonsht]))
		topi=topi[0]
		topi=np.sort(topi)
		maxlen=len(topi)
		nl=0
		maxnl=0
		maxstart=-1
		
		for i in range(maxlen-1):
			if(topi[i+1]-topi[i]>1):
				if(maxnl<nl):
					maxnl=nl
					maxstart=i-nl
				nl=0
			else:
				nl+=1
		shtstart=topi[maxstart]+1
		shtend=topi[maxstart]+maxnl

		sht=np.array(list(range(shtstart,shtend)))
		print(shtstart,shtend,np.average(score[sht]),np.average(score[nonsht])+np.std(score[nonsht])*options.cutoff)
		
		if maxnl<options.minlen:
			break
		if np.average(score[sht])<np.average(score[nonsht])+np.std(score[nonsht])*options.cutoff:	#stop criteria ...
			break			
		#enlong the chain
		for i in range(maxnl-2):
			ni=shtstart+i
			nj=shtstart+i+2
			#print ni,ang[ni,nj]
			if(ang[ni,nj]<.5):
				break
		shtend=ni+1
		for term in [-1,1]:
			if term<0:
				t=shtstart
			else:
				t=shtend
			for i in range(20):
				ni=t+term*(i-2)
				nj=t+term*(i+1)
				#print ni,ang[ni,nj]
				if(ang[ni,nj]<.7):
					break
			if term<0:
				shtstart-=i
			else:
				shtend+=i
		
		sheets[nsheet]=[shtstart,shtend]
		sht=np.array(list(range(shtstart,shtend)))
		insht[sht]=1
		#recalc the score
		
		score=np.zeros(na,float)
		dist=np.empty(na,float)
		nnb=10 # number of neighbors considered
		for i in range(na):
			if insht[i]==1:
				continue
			for j in range(na):
				dist[j]=np.linalg.norm(pts[i,:]-pts[j,:])
			srti=np.argsort(dist)
			for j in range(nnb):
				d=dist[srti[j]]
				wt=gaussianpdf(d,5)
				if insht[srti[j]]==1:
					wt*=2
				score[i]+=ang[i,srti[j]]*wt
		
		
	
	print(sheets)
	write_pdb(options.output,pts,score,atomnumber,sheets,header)
			
	E2end(logid)
			
		
	
			


















    
if __name__ == '__main__':
    main()
	
