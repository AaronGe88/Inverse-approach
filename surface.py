#from scipy.optimize import leastsq
import scipy
from Bulge import *
INDEX = 500
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
	timelist = [.12,.13,.135,.15,.16,.17,.175]
	amps = x
	midpairs = [(.05,.0416),(.06,.1264),(.07,0.2743),(.075,.2904),(.09,.3545),(.11,.4184)]
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
p0=scipy.array([196000.,.315,745.2,0.073,.251,1.26,1.28])
y = scipy.array([37.68,38.85,39.72,41.81,43.49,44.99,45.85])
x = scipy.array([.424,.4332,.4396,.4451,.4463,.447,.4504])
#plsq = leastsq(objF,p0,args=(y,x),epsfcn = 0.0000000003,factor = .1
for ii in range (730,830,10) :
	for jj in range(245,255):
		k = float (ii)
		n = float(jj)/100
		p = scipy.array([196000.,.315,k,0.073,n,1.26,1.28])
		objF(p,y,x)