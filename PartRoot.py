# -*- coding: utf-8 -*- 
_metaclass_ = type
class Tool:
	def __init__(self,model):
		self.model = model
		self.shape = (0,0,0)
	def setModel(self,model):
		self.model = model
	def setShape(self,shape):
		self.shape = shape
	def setRP(self,RP):
		self.RP = RP
		p = self.model.parts[self.partName]
		p.ReferencePoint(point=self.RP)
		r = p.referencePoints
		refPoints=(r[2], )
		p.Set(referencePoints=refPoints, name='Set-RP')
	
	def setMaterial(self,sectName):
		from section import TOP_SURFACE
		from section import FROM_SECTION
		p = self.model.parts[self.partName]
		f = p.faces
		faces = f.getSequenceFromMask(mask=('[#ff ]', ), )
		p.Set(faces=faces, name='Set-Body')
		region = p.sets['Set-Body']
		p.SectionAssignment(region=region, sectionName=sectName, offset=0.0, 
			offsetType=TOP_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)
			
	def outerSurface(self):
		pass
	def innerSurface(self):
		pass
	def mesh(self,size):
		p = self.model.parts[self.partName]
		p.seedPart(size=size, deviationFactor=0.1, minSizeFactor=0.1)
		p.generateMesh()
	def makeIt(self,shape,RP,sectName,meshSize):
		self.setShape(shape)
		self.geometry()
		self.setRP(RP)
		self.setMaterial(sectName)
		self.outerSurface()
		self.innerSurface()
		self.mesh(meshSize)

_metaclass_ = type
class Part:
	def __init__(self,model):
		self.model = model
		self.shape = (0,0,0)
	def setShape(self,shape):
		self.shape = shape
	def geometry(self):
		pass
	def setMaterial(self,sectName):
		from section import TOP_SURFACE
		from section import FROM_SECTION
		p = self.model.parts[self.partName]
		f = p.faces
		faces = f.getSequenceFromMask(mask=('[#ff ]', ), )
		p.Set(faces=faces, name='Set-Body')
		region = p.sets['Set-Body']
		p.SectionAssignment(region=region, sectionName=sectName, offset=0.0, 
			offsetType=TOP_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)
			
	def outerSurface(self):
		pass
	def innerSurface(self):
		pass
	
	def mesh(self,size):
		p = self.model.parts[self.partName]
		p.seedPart(size=size, deviationFactor=0.1, minSizeFactor=0.1)
		p.generateMesh()
		
			
		
	def makeIt(self,shape,sectName,meshSize):
		self.setShape(shape)
		self.geometry()
		self.setMaterial(sectName)
		self.outerSurface()
		self.innerSurface()
		self.mesh(meshSize)