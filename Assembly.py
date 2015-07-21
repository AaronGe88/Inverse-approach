# -*- coding: utf-8 -*- 
INDEX = 0
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
class Assembly:
	def __init__(self,modelname):
		self.model = mdb.models[modelname]
		self.modelname = modelname
		self.tools = []
		self.innertools=[]
		self.parts = []
	def setupShapes(self,shapes):
		self.shapes = shapes
		
	def setupMaterials(self,materials):
		pass
	def addInstance(self):
		pass
	def setPositions(self,positions,args):
		pass
	
	def toolsRigid(self,args):
		for instance in self.tools:
			a = self.model.rootAssembly
			region2=a.instances[instance.partName+'-1'].sets['Set-Body']
			a = self.model.rootAssembly
			region1=a.instances[instance.partName+'-1'].sets['Set-RP']
			self.model.RigidBody(name='RIGID-'+ instance.partName, refPointRegion=region1, 
				bodyRegion=region2)
				
		for instance in self.innertools:
			a = self.model.rootAssembly
			region2=a.instances[instance.partName+'-1'].sets['Set-Body']
			a = self.model.rootAssembly
			region1=a.instances[instance.partName+'-1'].sets['Set-RP']
			self.model.RigidBody(name='RIGID-'+ instance.partName, refPointRegion=region1, 
				bodyRegion=region2)
				
	def interactions(self,inits,args):
		pass
	
	def stepSetup(self, steps,args):
		
		self.model.ExplicitDynamicsStep(name='Step-1', previous='Initial', 
			massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 1000, 0.0, None, 
			0, 0, 0.0, 0.0, 0, None), ))
		self.model.fieldOutputRequests['F-Output-1'].setValues(variables=(
			'S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A', 
			'RF', 'CSTRESS', 'EVF', 'STH', 'COORD'))
		for ii in range(2,steps+1):
			self.model.ExplicitDynamicsStep(name='Step-'+str(ii), previous='Step-'+str(ii-1))

	def setBC(self,BCs,args):
		pass
		
	def setLoads(self,loads):
		pass
		
	def submitJob(self):
		jobname = 'Job-'+self.modelname
		mdb.Job(name=jobname, model=self.modelname, description='', type=ANALYSIS, 
			atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
			memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, 
			nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
			contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
			resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=2, 
			activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=2)
		mdb.jobs[jobname].submit(consistencyChecking=OFF)
		mdb.jobs[jobname].waitForCompletion()
		
	def makeIt(self,shapes,materials,positions,inits,steps,BCs,Loads,meshSize,args):
		self.setupShapes(shapes)
		self.setupMaterials(materials)
		self.addInstance(meshSize)
		self.stepSetup(steps,args)
		self.setPositions(positions,args)
		self.toolsRigid(args)
		self.interactions(inits,args)
		self.setBC(BCs = BCs,args=args)
		self.setLoads(Loads)
		self.submitJob()
	