import numpy as np
import shapely as shp

from matplotlib import pyplot as plt
from math import pi

from apx_ell import *
from intrsect_checker import *

u=1.     #x-position of the center
v=0.5    #y-position of the center
a=5.     #radius on the x-axis
b=1.5    #radius on th

ell = apx_Ellipse(a,b,u,v)
t = np.linspace(0, 2*pi, 200)
plt.plot( u+a*np.cos(t) , v+b*np.sin(t), color='black' )

apx_up = ell.apx_upper()
apx_lo = ell.apx_lower()

u_poly = shp.Polygon(apx_up)
x,y=u_poly.exterior.xy
plt.plot(x,y, color='blue')

l_poly = shp.Polygon(apx_lo)
x,y=l_poly.exterior.xy
plt.plot(x,y, color='green')

plt.show()

chk = intrsect_checker(apx_up, apx_lo)
pt = [1.1,1.9]
match chk.pointIn(pt) :
    case 0 :
        print( f"Point {pt} not in the shape" )
    case 1 :
        print(f"Point {pt} in the shape")
    case _ :
        print(f"Point {pt} somewhere there")

pt = [1.1,2.]
match chk.pointIn(pt) :
    case 0 :
        print( f"Point {pt} not in the shape" )
    case 1 :
        print(f"Point {pt} in the shape")
    case _ :
        print(f"Point {pt} somewhere there")

pt = [1.1,2.2]
match chk.pointIn(pt) :
    case 0 :
        print( f"Point {pt} not in the shape" )
    case 1 :
        print(f"Point {pt} in the shape")
    case _ :
        print(f"Point {pt} somewhere there")
