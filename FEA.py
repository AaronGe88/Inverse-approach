# -*- coding: utf-8 -*- 
from part import *
from section import *
from regionToolset import *
from displayGroupMdbToolset import *
from part import *
from material import *
from assembly  import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from xyPlot import *
from connectorBehavior import *
_metaclass_ = type
class FEA:
	def __init__(self,modelname):
		self.assembly = None
		self.springback = None
		Mdb()
		self.modelname = modelname
		mdb.models.changeKey(fromName='Model-1', toName=modelname)
		self.model=mdb.models[modelname]
		self.shapes = None#{'bendR':220.0,'outDiameter':40.0,'thick':1.0,'mandralGap':.8,'toolGap':0.1,'ballThick':10.0,}
		self.positions = None#{'insert':(0,0,-200),'tube':(0,0,-240),'ball':(-shapes['bendR'],0,-12),'mandral':(0,0,0),'wiper':0.5}
		self.material=None
		self.meshSize = None
		self.inits=None
		self.arg=None
		self.Load=None
		self.BCs=None
		self.steps = None
	def setModels(self):
		pass
	
	def setParameter(self,shapes,materials,positions,inits,\
		steps,BCs,Loads,meshSize,args):
		pass
	def doJobs(self):
		pass
	def getResults(self):
		pass