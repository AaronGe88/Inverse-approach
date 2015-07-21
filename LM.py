from scipy.optimize import leastsq
import scipy
from Bulge import *
INDEX = 0
def objF(p,y,x):
	global INDEX
	modelname = 'Model-'+str(INDEX)
	INDEX += 1
	E,u,K,e0,n,rth,rz= p
	parts = [7.85e-9,E,u,K,e0,n,rth,rz]		
	paramFile = open('result.txt','a+')
	paramFile.write('%s %10.6E %10.6E %10.6E %10.6E %10.6E %10.6E %10.6E '%(str(INDEX),E,u,K,e0,n,rth,rz))
	paramFile.flush()
	material = {'part':parts}
	shapes = {'outDimater':72.5,'thick':3.65,'length':145}
	mesh={'tube':100}
	timelist = [.20,.205,.21,.22,.23,.235,.24]
	amps = x
	midpairs = [(.05,.0329),(.1,.2246),(.15,.4013),(.18,.4957)]
	args={'timelist':timelist,'amp':amps,'midpairs':midpairs}
	load=args
	inits={}
	BCs={}
	positions = {}
	material={'part':parts}
	meshSize = {'pressDie':shapes['thick']*3/0.6,'tube':shapes['thick']/0.6 * 2}
	t = TBFEA(modelname)
	t.setParameter(shapes,material,positions,inits,\
			len(timelist),BCs,load,meshSize,args)
	t.setModels()
	coords = t.getResults()
	npFEA = scipy.array(coords)
	npExp = y
	print y
	print npFEA
	npres = npFEA - npExp
	mse=scipy.sum(scipy.square(npres))
	paramFile.write('%10.6E\n'%(mse))
	paramFile.close()
	return npres
paramFile = open('result.txt','w')
paramFile.close()
#7.584489E+02 8.233530E-02 2.722855E-01 1.346841E+00 1.525195E+00 5.064105E+00
p0=scipy.array([210000.,.3,906.,0.034,.155,0.98,1.23])
y = scipy.array([37.00,37.47,37.55,38.53,39.39,39.85,40.58])
x = [.5547,.5570,.576,.5824,.5957,.5974,.5982]
plsq = leastsq(objF,p0,args=(y,x),epsfcn = 0.0000000003,factor = .1)