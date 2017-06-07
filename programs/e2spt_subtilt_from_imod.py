#!/usr/bin/env python
# Muyuan Chen 2016-10
# Muyuan Chen mostly rewrite 2017-03
from EMAN2 import *
import numpy as np

def main():
	
	usage="""
	This program extract particles from .ali files from IMOD reconstruction. It takes most information, including XTILT angle and boundary of trimmed volume from IMOD setting and log files. So make sure the whole IMOD project is not corrupted after the reconstruction. This program is test on IMOD 4.7.13 (10/15/2014). There is no garantee that it will work on project generated by any other IMOD versions.
	
	Extracting particles using the box locations saved in the info file corresponding to the tomogram
	[prog] --tomo <tomogram name> --edf <imod edf file> --ptclout <output 2D particle file name> [options]
	
	Extracting particles using 3D particles extracted from the tomogram
	[prog] --ptclin <3D particles> --edf <imod edf file> --ptclout <output 2D particle file name> [options]
	
	"""
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	parser.add_argument("--tomo", type=str,help="File name of reconstructed tomograms", default=None)
	parser.add_argument("--ptclin", type=str,help="File name of input 3D particles.", default=None)
	parser.add_argument("--edf", type=str,help="IMOD .edf file name", default=None)
	#parser.add_argument("--tlt", type=str,help="imod tlt file name", default=None)
	#parser.add_argument("--xtilt", type=float,help="imod xtilt value (from tomopitch.log)", default=0)
	parser.add_argument("--unbin", type=float,help="Unbin factor from input particles/tomogram to raw tilt. If unspecified, the program will calculate from the Apix of the header.", default=-1)
	parser.add_argument("--boxsz", type=int,help="Box size of extracted 2D particles.", default=64)
	parser.add_argument("--ptclout", type=str,help="File name of output 2D extracted particles.", default=None)
	parser.add_argument("--ctffile", type=str,help="estimated ctf", default=None)
	parser.add_argument("--defcol", type=int,help="which column of ctf file is the defocus", default=2)
	parser.add_argument("--weight",action="store_true",help="Weight the particles by the variance of defocus",default=False)
	(options, args) = parser.parse_args()
	logid=E2init(sys.argv)
	
	if options.tomo:
		tomoname=options.tomo
		js=js_open_dict(info_name(tomoname))
		box=np.array([[b[0],b[1],b[3]] for b in js["boxes"]])
		js=None
		origin=options.tomo
		
	elif options.ptclin:
		num=EMUtil.get_image_count(options.ptclin)
		box=[]
		for i in range(num):
			e=EMData(options.ptclin, i, True)
			box.append(e["ptcl_source_coord"])
		box=np.array(box, dtype=float)
		origin=options.ptclin
	
	#box=box[:50]
	print "Read {} particles".format(len(box))
	edfname=os.path.abspath(options.edf)
	spos=edfname.rfind('/')
	path=edfname[:spos+1]
	fname=edfname[spos+1:-4]
	
	print "Looking for trim sizes from imod..."
	
	f=open(edfname)
	lines=f.readlines()
	f.close()
	ss=[".xmin", ".xmax", ".ymin", ".ymax", ".zmin", ".zmax"]
	key="Trimvol"
	trimshp=np.zeros(len(ss))
	for l in lines:
		if key in l:
			l=l[l.find(key):-1].lower()
			
			for i, s in enumerate(ss):
				if s in l:
					eqpos=l.rfind('=')
					trimshp[i]=int(l[eqpos+1:])
	print "Trim sizes are: "
	for i,s in enumerate(ss):
		print s[1:], trimshp[i]
	trimshp=trimshp.reshape((3,2))
	
	
	raw0=EMData(path+fname+"_full.rec",0, True)
	rawshp=np.array([raw0["nx"], raw0["nz"], raw0["ny"]])
	
	print "Full size tomogram shape:", rawshp
	
	corsft=rawshp/2-np.mean(trimshp, axis=1)
	#corsft[2]=0
	print "Coordinates shift: ", corsft

	tltfile=path+fname+".tlt"
	tlts=np.loadtxt(tltfile)
	print "Read {} tilts from {} to {}.".format(len(tlts), np.min(tlts), np.max(tlts))
	
	tlogfile=path+"tilt.log"
	f=open(tlogfile)
	lines=f.readlines()
	f.close()
	
	xtilt=0
	for l in lines:
		if "XAXISTILT" in l:
			eqpos=l.rfind('=')
			xtilt=float(l[eqpos+1:])
			print "Xtilt is {}".format(xtilt)
			break
		
	
	
	ptclout=options.ptclout
	
	
	try: os.remove(ptclout)
	except: pass

	alifile=path+fname+".ali"

	sz=options.boxsz
	if options.tomo:
		e0=EMData(tomoname,0,True)
	else:
		e0=EMData(path+fname+".rec", 0, True)
	
	tomoshape=np.array([e0["nx"], e0["ny"], e0["nz"]])
	eapix=e0["apix_x"]	
	
	a0=EMData(alifile,0,True)
	aapix=a0["apix_x"]
	a_nx=a0["nx"]
	a_ny=a0["ny"]
	atoum=float(10*1000) # A to um
	
	box-=tomoshape/2
	
	if options.unbin<=0:
		print "Apix of ali is {:.2f}, Apix from tomo is {:.2f}".format(aapix, eapix)
		options.unbin=eapix/aapix
		print "Box coordinates unbinned by {} based on apix..".format(options.unbin)
	
	box*=options.unbin
	box=box-corsft
	allb=[]
	
	if options.ctffile:
		ctfsave=np.loadtxt(options.ctffile)
		defocus=ctfsave[:, options.defcol]
		print "Read defocus for {:d} tilts from file, range from {:.2f} to {:.2f}.".format(len(defocus), np.min(defocus), np.max(defocus))
		if options.weight:
			wt=ctfsave[:,options.defcol]
			print "Weight particles by the variance of esitimated defocus, from {:.2f} to {:.2f}".format(np.max(wt), np.min(wt))
			wt=1./(wt+.1)
			wt/=np.max(wt)
		
		f=open(options.ctffile,'r')
		ctf=EMAN2Ctf()
		ctf.from_dict({"defocus":0, "voltage":0, 'apix':aapix, 'bfactor':0, "cs":0})
		for l in f:
			if l.startswith("#"):
				if "Voltage" in l:
					ctf.voltage=float(l[l.find(':')+1:])
					print "Voltage: {:.1f} kV".format(ctf.voltage)
				if "Cs" in l:
					ctf.cs=float(l[l.find(':')+1:])
					print "Cs={:.1f}".format(ctf.cs)
			else:
				break
		
		
	kk=0
	print "Generating particles..."
	for bi,b in enumerate(box):
		for i,t in enumerate(tlts):
	
			tr=Transform()
			tr=Transform({"type":"xyz","xtilt":xtilt, "ytilt":-t})
			
			p=tr.transform(Vec3f(b.astype(int).tolist()))
			
			p[0]+=a_nx/2
			p[1]+=a_ny/2
			
			allb.append([p[0],p[1], "manual", i])
			#print p
			e=EMData(alifile, 0, False, Region(p[0]-sz/2,p[1]-sz/2,i,sz,sz,1))
			e.mult(-1)
			e.process_inplace("normalize.edgemean")
			e["box2d"]=[int(p[0]),int(p[1])]
			e["box3d"]=[int(b[0]),int(b[1]), int(b[2])]
			e["tltang"]=t
			e["tltid"]=i
			e["model_id"]=bi
			e["xform.projection"]=tr
			e["alifile"]=alifile
			e["source_file"]=origin 
			
			if options.ctffile:
				df=defocus[i]
				px=a_nx/2-p[0]
				ddf=aapix/atoum*np.sin(t/180.*np.pi) * px
				bz=aapix/atoum*np.cos(t/180.*np.pi) * float(b[2])
				df=df+ddf+bz
				e["defocus"]=df
				ctf.defocus=df
				e["ctf"]=ctf
				if options.weight:
					e["ptcl_repr"]=wt[i]
			
			
			
			e.write_image(ptclout,-1)
			kk+=1
	js0=js_open_dict(info_name(alifile))
	js0["boxes"]=allb
	js0=None
	
	print "Done. {:d} 2D projections written.".format(kk)
	E2end(logid)
	
def run(cmd):
	print cmd
	launch_childprocess(cmd)
	
	
if __name__ == '__main__':
	main()
	