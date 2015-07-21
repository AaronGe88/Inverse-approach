# -*- coding: utf-8 -*- 
from odbAccess import *
from abaqus import *
from abaqusConstants import *
_metaclass_ = type
class PostProcess:
	def __init__(self,modelname):
		self.part = None
		self.modelname = modelname
		self.odb=openOdb(path='Job-'+modelname+'.odb')
		self.step=self.odb.steps.values[-1]
		self.frame=self.step.frame[-1] 
	def setPart(self,partname):
		self.part=self.odb.rootAssembly.instances[partname]
	def output(self,args):
		pass
	def close(self):
		self.odb.close()
		del self.odb
	
		
		