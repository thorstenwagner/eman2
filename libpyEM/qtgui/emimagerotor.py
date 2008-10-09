#!/usr/bin/env python

#
# Author: David Woolford (sludtke@bcm.edu)
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
#
#

from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from OpenGL import GL,GLU,GLUT
from OpenGL.GL import *
from OpenGL.GLU import *

from math import tan,pi
import sys
import time
import numpy
from weakref import WeakKeyDictionary

from EMAN2 import *

from emfloatingwidgets import EMGLRotorWidget, EMGLView2D,EM3DWidget
from emimagemx import EMImageMXModule
from emimageutil import  EMEventRerouter
from emglobjects import EMOpenGLFlagsAndTools, EMImage2DGUIModule,EMOpenGLFlagsAndTools
from emapplication import EMStandAloneApplication, EMQtWidgetModule, EMGUIModule

GLUT.glutInit("")

class EMImageRotorWidget(QtOpenGL.QGLWidget,EMEventRerouter):
	"""
	"""
	allim=WeakKeyDictionary()
	def __init__(self, em_rotor_module,enable_timer=True):
		assert(isinstance(em_rotor_module,EMImageRotorModule))
		EMImageRotorWidget.allim[self]=0

		self.mmode = "drag"

		fmt=QtOpenGL.QGLFormat()
		fmt.setDoubleBuffer(True);
		fmt.setSampleBuffers(True)
		#fmt.setDepthBuffer(True)
		QtOpenGL.QGLWidget.__init__(self,fmt)
		EMEventRerouter.__init__(self)
		
		
		self.target = em_rotor_module
		self.imagefilename = None
		
		self.fov = 20
		self.aspect = 1.0
		self.z_near = 1
		self.z_far = 2000
		
		self.animatables = []
		
		if enable_timer:
			self.__init_timer()
		else: self.timer_enabled = False
		
		
	def __init_timer(self):
		self.timer = QtCore.QTimer()
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timeout)
		self.timer.start(20)
		self.timer_enabled = True
		
	def get_target(self):
		return self.target
		
	def set_data(self,data):
		self.target.set_data(data)
	
	def timeout(self):
		
		if len(self.animatables) == 0: return
		
		for i,animatable in enumerate(self.animatables):
			if not animatable.animate(time.time()):
				# this could be dangerous
				self.animatables.pop(i)
		
		self.updateGL()
		
	def register_animatable(self,animatable):
		self.animatables.append(animatable)
	
	def setImageFileName(self,name):
		#print "set image file name",name
		self.imagefilename = name
		
	def getImageFileName(self):
		return self.imagefilename
	
	def initializeGL(self):
		glClearColor(0,0,0,0)
		
		glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
		glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
		glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
		glLightfv(GL_LIGHT0, GL_POSITION, [0.1,.1,1.,0.])
	
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		
		glEnable(GL_DEPTH_TEST)
		
		glEnable(GL_NORMALIZE)
		
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glHint(GL_TEXTURE_COMPRESSION_HINT, GL_NICEST)
		
	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		if ( self.target == None ): return
		self.target.render()

	
	def resizeGL(self, width, height):
		if width <= 0 or height <= 0: return None
		GL.glViewport(0,0,width,height)
	
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		self.aspect = float(width)/float(height)
		GLU.gluPerspective(self.fov,self.aspect,self.z_near,self.z_far)
		#GL.glOrtho(0.0,width,0.0,height,-width,width)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()
		
		self.target.resize_event(width,height)
	
	
	def set_near_far(self,near,far):
		self.z_near = near
		self.z_far = far
		
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GLU.gluPerspective(self.fov,self.aspect,self.z_near,self.z_far)
		#GL.glOrtho(0.0,width,0.0,height,-width,width)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()
	
	def get_depth_for_height(self, height):
		# This function returns the width and height of the renderable 
		# area at the origin of the data volume
		depth = height/(2.0*tan(self.fov/2.0*pi/180.0))
	
		return depth
	def set_mouse_mode(self,mode):
		self.mmode = mode
		self.target.set_mouse_mode(mode)
	
	def set_shapes(self,shapes,shrink,idx=0):
		self.target.set_shapes(shapes,shrink,idx)
	
	def set_frozen(self,frozen,idx=0):
		self.target.set_frozen(frozen,idx)
	
class EMImageRotorModule(EMImage2DGUIModule):
	def get_qt_widget(self):
		if self.parent == None:
			self.parent = EMImageRotorWidget(self)
		return EMGUIModule.darwin_check(self)
	
	def __init__(self, data=None,application=None):
		EMImage2DGUIModule.__init__(self,application,ensure_gl_context=True)
		self.parent = None
		self.data=None
		try: self.parent.setAcceptDrops(True)
		except:	pass

		self.initsizeflag = True
		if data:
			self.set_data(data)
		
		self.rotor = EMGLRotorWidget(self,-25,10,40,EMGLRotorWidget.LEFT_ROTARY)
		self.widget = EM3DWidget(self,self.rotor)
		self.widget.set_draw_frame(False)
		
		self.z_near = 0
		self.z_far = 0
		
		self.hud_data = [] # a list of strings to be rendered to the heads up display (hud)
	
		self.load_font_renderer()
		
	def load_font_renderer(self):
		try:
			self.font_renderer = get_3d_font_renderer()
			self.font_renderer.set_face_size(20)
			self.font_renderer.set_depth(4)
			self.font_renderer.set_font_mode(FTGLFontMode.EXTRUDE)
			
#			self.font_renderer.set_font_file_name("/usr/share/fonts/dejavu/DejaVuSerif.ttf")
			self.font_render_mode = EMGUIModule.FTGL
		except:
			self.font_render_mode = EMGUIModule.GLUT
		
	def set_extra_hud_data(self,hud_data):
		self.hud_data = hud_data
	
	def get_optimal_size(self):
		lr = self.rotor.get_suggested_lr_bt_nf()
		width = lr[1] - lr[0]
		height = lr[3] - lr[2]
		return [width+80,height+20]
	
		#self.rotor.set_shapes([],1.01)
	def context(self):
		# asking for the OpenGL context from the parent
		return self.parent.context()
	
	def emit(self,signal,event,a=None,b=None):
		if b != None:
			self.parent.emit(signal,event,a,b)
		elif a != None:
			self.parent.emit(signal,event,a)
		else:
			self.parent.emit(signal,event)

	def set_mouse_mode(self,mode):
		self.mmode = mode
		self.rotor.set_mouse_mode(mode)

	def set_frozen(self,frozen,idx=0):
		self.rotor.set_frozen(frozen,idx)

	def set_shapes(self,shapes,shrink,idx=0):
		self.rotor.set_shapes(shapes,shrink,idx)

	def register_animatable(self,animatable):
		self.parent.register_animatable(animatable)
	
	def get_inspector(self):
		return None
	
	def width(self):
		return self.parent.width()
	
	def height(self):
		return self.parent.height()

	def getImageFileName(self):
		''' warning - could return none in some circumstances'''
		try: return self.parent.getImageFileName()
		except: return None
		
	def set_data(self,data):
		if data == None or not isinstance(data,list) or len(data)==0:
			self.data = [] 
			return
		
		self.data = data
		
		self.rotor.clear_widgets()
		for d in self.data:
			w = EMGLView2D(self,d)
			self.rotor.add_widget(w)
			
		#self.show_inspector()		# shows the correct inspector if already open
		#self.timer.start(25)
		
		# experimental for lst file writing
		for i,d in enumerate(data):
			d.set_attr("original_number",i)

	def updateGL(self):
		try: self.parent.updateGL()
		except: pass


	def render(self):
		if not self.data : return
		
		#glLoadIdentity()
		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glEnable(GL.GL_LIGHTING)
		
		lr = self.rotor.get_suggested_lr_bt_nf()
		lrt = lr
		#lr = self.widget.get_lr_bt_nf()
		
		z = self.parent.get_depth_for_height(abs(lr[3]-lr[2]))
		
		z_near = z-lrt[4]
		z_trans = 0
		z_far = z-lrt[5]
		if z_near < 0:
			z_trans = z_near
			z_near = 0.1
			z_far -= z_trans
		if z_far < 0: z_far = 0.1 # hacking alert
		if self.z_near != z_near or self.z_far != z_far:
			self.z_near = z_near
			self.z_far = z_far
			self.parent.set_near_far(self.z_near,self.z_far)

		#FTGL.print_message("hello world",36);
		
		#print self.z_near,self.z_far,-self.parent.get_depth_for_height(abs(lr[3]-lr[2]))+z_trans
		
		glPushMatrix()
		glTranslate(-(lr[1]+lr[0])/2.0,-(lr[3]+lr[2])/2.0,-z+z_trans+abs(lr[3]-lr[2]))
		glTranslate(0,-75,0) # This number is a FIXME issue
		#FTGL.print_message("hello hello",36);
		self.widget.draw()
		glPopMatrix()
		
		self.draw_hud()
	
	def dragEnterEvent(self,event):
		pass

	
	def dropEvent(self,event):
		pass


	def mousePressEvent(self, event):
		self.widget.mousePressEvent(event)
		self.updateGL()
	
	def mouseMoveEvent(self, event):
		self.widget.mouseMoveEvent(event)
		self.updateGL()
		
	def mouseReleaseEvent(self, event):
		self.widget.mouseReleaseEvent(event)
		self.updateGL()
		
	def keyPressEvent(self,event):
		pass
		
	def wheelEvent(self, event):
#		if event.delta() > 0:
#			self.set_scale( self.scale * self.mag )
#		elif event.delta() < 0:
#			self.set_scale(self.scale * self.invmag )
#		self.resizeEvent(self.parent.width(),self.parent.height())
#		# The self.scale variable is updated now, so just update with that
#		if self.inspector: self.inspector.set_scale(self.scale)
		self.widget.wheelEvent(event)
		self.updateGL()
	def leaveEvent(self):
		pass
	
	def resize_event(self, width, height):
		self.rotor.resize_event(width,height)


	def draw_hud(self):
		width = self.parent.width()
		height = self.parent.height()
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		glOrtho(0,width,0,height,-100,100)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glEnable(GL_LIGHTING)
		glEnable(GL_NORMALIZE)
		glMaterial(GL_FRONT,GL_AMBIENT,(0.2, 1.0, 0.2,1.0))
		glMaterial(GL_FRONT,GL_DIFFUSE,(0.2, 1.0, 0.9,1.0))
		glMaterial(GL_FRONT,GL_SPECULAR,(1.0	, 0.5, 0.2,1.0))
		glMaterial(GL_FRONT,GL_SHININESS,20.0)
		
		glDisable(GL_DEPTH_TEST)
		glColor(1.0,1.0,1.0)
		
		
		if self.font_render_mode == EMImageMXModule.FTGL:
			panels = len(self.rotor)
			idx = self.rotor.current_index()
			string = str(idx+1) + ' / ' + str(panels)
			bbox = self.font_renderer.bounding_box(string)
			x_offset = width-(bbox[3]-bbox[0]) - 10
			y_offset = 10
			
			glPushMatrix()
			glTranslate(x_offset,y_offset,0)
			glRotate(20,0,1,0)
			self.font_renderer.render_string(string)
			glPopMatrix()
			y_offset += bbox[4]-bbox[1]
			for s in self.hud_data:
				string = str(s)
				bbox = self.font_renderer.bounding_box(string)
				x_offset = width-(bbox[3]-bbox[0]) - 10
				y_offset += 10
				glPushMatrix()
				glTranslate(x_offset,y_offset,0)
				glRotate(20,0,1,0)
				self.font_renderer.render_string(string)
				glPopMatrix()
				y_offset += bbox[4]-bbox[1]
		else:
			pass
		
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
# This is just for testing, of course
if __name__ == '__main__':
	em_app = EMStandAloneApplication()
	window = EMImageRotorModule(application=em_app)
	window.get_qt_widget()
	if len(sys.argv)==1 :
		data = []
		for i in range(0,20):
			e = test_image(Util.get_irand(0,9))
			data.append(e)
			
		window.set_data(data) 
	else :
		a=EMData.read_images(sys.argv[1])
		window.setImageFileName(sys.argv[1])
		window.set_data(a)

	em_app.show()
	em_app.execute()

