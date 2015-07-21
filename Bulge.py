# -*- coding: utf-8 -*- 
from PartRoot import *
from Assembly import *
from FEA import *
from PostProcess import *

class Tube(Part):
	def __init__(self,model):
		Part.__init__(self,model)
		self.partName = 'Part-Tube'
	def geometry(self):
		outerR = self.shape['outDimater']/2
		thick = self.shape['thick']
		length = self.shape['length']
		s = self.model.ConstrainedSketch(name='__profile__', 
			sheetSize=200.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outerR, 0.0))
		p = self.model.Part(name=self.partName, dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = self.model.parts[self.partName]
		p.BaseShellExtrude(sketch=s, depth=length)
		s.unsetPrimaryObject()
		p = self.model.parts[self.partName]
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del self.model.sketches['__profile__']
		
		e=p.edges
		end1 = e.findAt(((0.,outerR,0.),))#.getSequenceFromMask(mask=('[#4 ]', ), )
		end2 = e.findAt(((0.,outerR,length),))
		p.Set(edges=end1, name='Set-End1')
		p.Set(edges=end2, name='Set-End2')
		
	
	def outerSurface(self):
		outerR = self.shape['outDimater']/2
		thick = self.shape['thick']
		length = self.shape['length']
		outer = (0.0,outerR,length/2)
		p = self.model.parts[self.partName]
		s = p.faces
		side1Faces = s.findAt((outer,))
		p.Surface(side1Faces=side1Faces, name='Surf-Outer')
	
	def innerSurface(self):
		outerR = self.shape['outDimater']/2
		thick = self.shape['thick']
		length = self.shape['length']
		outer = (0.0,outerR,length/2)
		p = self.model.parts[self.partName]
		s = p.faces
		side2Faces = s.findAt((outer,))
		p.Surface(side2Faces=side2Faces, name='Surf-Inner')

		
	def mesh(self,size):
		outerR = self.shape['outDimater']/2
		thick = self.shape['thick']
		length = self.shape['length']
		p = self.model.parts[self.partName]
		e = p.edges
		outer = (outerR,0.0,0.0)
		outer2 = (outerR,0.0,length)
		pickedEdges = e.findAt((outer,),(outer2,))
		p.seedEdgeByNumber(edges=pickedEdges, number=60, constraint=FINER)
		p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0)
		f = p.faces
		pickedFaces = f.findAt(((0.,outerR,length/2),))
		d = p.datums
		p.PartitionFaceByDatumPlane(datumPlane=d[8], faces=pickedFaces)
		e = p.edges
		pickedEdges = e.findAt(((0.,outerR,length/2),))
		p.seedEdgeByNumber(edges=pickedEdges, number=60, constraint=FINER)
		p.generateMesh()
		n=p.nodes
		midpos=n[36:37]
		p.Set(nodes=midpos, name='Set-Mid')
	
	def setMaterial(self,sectName):
		outerR = self.shape['outDimater']/2
		thick = self.shape['thick']
		length = self.shape['length']
		p = self.model.parts[self.partName]
		f = p.faces
		faces = f.findAt(((outerR,0.,length/2),))
		region = p.Set(faces=faces, name='Set-Body')
		p.SectionAssignment(region=region, sectionName=sectName, offset=0.0, 
			offsetType=TOP_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)
	
class BulgeAssembly(Assembly):
	def setupMaterials(self,materials):
		PDensity,PE,PPossion,K,e0,n,rth,rz = materials['part']
		listPlastic= []
		for ep in range(0,20) :
			epx = ep * 0.025
			sigma = K * ((epx + e0) ** n)
			listPlastic.append((sigma,epx))
		sigma2 = K * ((2+e0)**n)
		listPlastic.append((sigma2,2+e0))
		tuplePlastic = tuple(listPlastic)
		r22=(rz*(rth+1.0)/(rth*(rz+1.0)))**.5
		r33 = (rz*(rth+1.0)/(rth+rz)) ** .5
		
		self.model.Material(name='Material-Tube')
		self.model.materials['Material-Tube'].Density(table=((PDensity, ), ))
		self.model.materials['Material-Tube'].Elastic(table=((PE, PPossion), ))
		self.model.materials['Material-Tube'].Plastic(table=tuplePlastic)
		self.model.materials['Material-Tube'].plastic.Potential(table=(
				(1.0, r22, r33, 1.0, 1.0, 1.0), ))
		self.model.HomogeneousShellSection(name='Section-Tube', 
			preIntegrate=OFF, material='Material-Tube', thicknessType=UNIFORM, 
			thickness=self.shapes['thick'], thicknessField='', idealization=NO_IDEALIZATION, 
			poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
			useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)

	
	def addInstance(self,meshSizes):
		#首先划分管材网格	
		tube = Tube(self.model)
		tube.makeIt(self.shapes,'Section-Tube',meshSizes['tube'])
		self.parts.append(tube)
	
	def stepSetup(self,steps,args):
		timelist = args['timelist']
		tp0 = timelist[0]
		self.model.ExplicitDynamicsStep(name='Step-1', previous='Initial', timePeriod=tp0,\
			massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 10.0, 0.0, None, 
			0, 0, 0.0, 0.0, 0, None), ))
		self.model.FieldOutputRequest(name='F-Output-1', 
			createStepName='Step-1', variables=(
			'S', 'SVAVG', 'PE', 'P', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A', 
			'RF', 'CSTRESS', 'EVF', 'STH', 'COORD'))
			
		self.model.HistoryOutputRequest(name='H-Output-1', 
			createStepName='Step-1', variables=('ALLAE', 'ALLCD', 'ALLDC', 
			'ALLDMD', 'ALLFD', 'ALLIE', 'ALLKE', 'ALLPD', 'ALLSE', 'ALLVD', 
			'ALLWK', 'ALLCW', 'ALLMW', 'ALLPW', 'ETOTAL'))
		for ii in range(2,steps+1):
			tp = timelist[ii-1] - timelist[ii-2]
			self.model.ExplicitDynamicsStep(name='Step-'+str(ii), previous='Step-'+str(ii-1),timePeriod=tp)
	
	def setPositions(self,positions,args):
		a = self.model.rootAssembly
		a.DatumCsysByDefault(CARTESIAN)
		indexPositions = 0
		for instance in self.parts:
			p = self.model.parts[instance.partName]
			a.Instance(name='Part-Tube-1', part=p, dependent=ON)

			
			
	
	def setBC(self,BCs,args):
		#amp = args['amp']
		a = self.model.rootAssembly
		region1 = a.instances['Part-Tube-1'].sets['Set-End1']
		region2 = a.instances['Part-Tube-1'].sets['Set-End2']
		self.model.DisplacementBC(name='BC-End1', createStepName='Step-1', 
			region=region1, u1=0.0, u2=0.0, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
			fixed=OFF, distributionType=UNIFORM, fieldName='', 
			localCsys=None)
		self.model.DisplacementBC(name='BC-End2', createStepName='Step-1', 
			region=region2, u1=0.0, u2=0.0, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
			fixed=OFF, distributionType=UNIFORM, fieldName='', 
			localCsys=None)
	
	def setLoads(self,loads):
		timelist = loads['timelist']
		tp0 = timelist[0]
		amps = loads['amp']
		midpairs=loads['midpairs']
		a = self.model.rootAssembly
		region = a.instances['Part-Tube-1'].surfaces['Surf-Inner']
		amp01=[(0.0,0.0)]
		for i in midpairs:
			amp01.append(i)
		amp01.append((tp0,amps[0]))
		self.model.TabularAmplitude(data=amp01, name='Amp-1', smooth=0.05, timeSpan=STEP)
		self.model.Pressure(amplitude='Amp-1', createStepName='Step-1', 
				distributionType=UNIFORM, field='', magnitude=100, name='Load-1', region=region)
		for ii in range(1,len(amps)):
			an = 'Amp-' + str(ii+1)
			sn = 'Step-'+str(ii+1)
			tp = timelist[ii] - timelist[ii-1]
			self.model.TabularAmplitude(data=((0.0, amps[ii - 1]), (tp, amps[ii])), name=
				an, smooth=0.05, timeSpan=STEP) 
			self.model.loads['Load-1'].setValuesInStep(amplitude=an, 
				stepName=sn)
			
		
class TBPost(PostProcess):
	def __init__(self,modelname):
		self.part = None
		self.modelname = modelname
		self.odb=openOdb(path='Job-'+modelname+'.odb')
		self.elements ={}
		self.mids={}
	def output(self,args):
		amps = args['amp']
		coord2s=[]
		for ii in range(0,len(amps)):
			sn = 'Step-' +str(ii + 1)
			step = self.odb.steps[sn]
			try:
				lastFrame = step.frames[-1]
				coords=lastFrame.fieldOutputs['COORD']
				mids=self.part.nodeSets['SET-MID']
				u2top = coords.getSubset(region=mids)
				coord2s.append(u2top.values[0].data[1])
			except OdbError,e:
				print '%s' %str(e)
				coord2s.append(1000)
			except : 
				print 'error'
				coord2s.append(1000)
		return coord2s
		# self
		# for v in end.values:
			# self.endSection[v.nodeLabel]=[v.data[0],v.data[1],v.data[2]]
		# for v in head.values:
			# self.headSection[v.nodeLabel]=[v.data[0],v.data[1],v.data[2]]
		
		# return self.endSection,self.headSection
		
class TBFEA(FEA):
	def setParameter(self,shapes,materials,positions,inits,\
			steps,BCs,Loads,meshSize,args):	
		self.shapes = shapes#{'bendR':220.0,'outDiameter':40.0,'thick':1.0,'mandralGap':.8,'toolGap':0.1,'ballThick':10.0,}
		self.positions = positions#{'insert':(0,0,-200),'tube':(0,0,-240),'ball':(-shapes['bendR'],0,-12),'mandral':(0,0,0),'wiper':0.5}
		self.material=materials
		self.meshSize = meshSize
		self.inits=inits
		self.arg=args
		self.Load=Loads
		self.BCs=BCs
		self.steps = steps
	def setModels(self):
		self.assembly = BulgeAssembly(self.modelname)
		self.assembly.makeIt(self.shapes,self.material,self.positions,self.inits,\
			7,self.BCs,self.Load,self.meshSize,self.arg)
	def doJobs(self):
		pass
	def getResults(self):
		tp = TBPost(self.modelname)
		tp.setPart('PART-TUBE-1')
		coords = tp.output(self.arg)
		tp.close()
		return  coords
		

