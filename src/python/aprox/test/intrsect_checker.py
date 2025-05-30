import numpy as np
import shapely as shp
from shapely import Point, Polygon

class intrsect_checker :
    def __init__(self, upPoints, loPoints) :
        self.loPoints = loPoints
        self.upPoints = upPoints

    def pointIn(self, pt) :
        p = Point(pt[0], pt[1])
        u_poly = Polygon(self.upPoints)
        l_poly = Polygon(self.loPoints)
        if not shp.contains(u_poly, p) :
            return 0
        if shp.contains(l_poly, p) :
            return 1
        return -1

    def shapeIn(self, pts) :
        u_poly = Polygon(self.upPoints)
        l_poly = Polygon(self.loPoints)
        poly = Polygon(pts)

        res = poly.intersects(u_poly)
        if not res :
            return 0
        res = poly.intersects(l_poly)
        if res :
            return 1
        return -1


