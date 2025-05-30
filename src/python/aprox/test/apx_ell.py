import numpy as np
from math import pi

class apx_Ellipse :
    # for ellipse, we define
    # x- and y-radius, coordinates of center,
    # number of precision points, and precision percentage for upper approximation
    def __init__(self, x_rad, y_rad, x_center=0, y_center=0, prec_pts=20, upper_perc=2):
        self.x_center = x_center
        self.y_center = y_center
        self.x_rad = x_rad
        self.y_rad = y_rad
        self.prec = prec_pts
        self.upper_prec = upper_perc
        self.lBound = 0
        self.uBound = 2*pi

    def setPrecisionPoints(self, prec_pts):
        self.prec = prec_pts

    def setPrecPercentage(self, upper_perc):
        self.upper_prec = upper_perc

    def setBounds(self, l, u):
        self.lBound = l
        self.uBound = u

    # numPoints mean the number of points on the X-axis, not a number of sides, angles etc.
    def apx_lower(self):
        pts = []
        xa = np.linspace(self.lBound, self.uBound, self.prec)
        for x in xa :
            pt = [self.x_center + self.x_rad * np.cos(x), self.y_center + self.y_rad * np.sin(x)]
            pts.append(pt)

        return pts

    def apx_upper(self):
        pts = []
        xa = np.linspace(self.lBound, self.uBound, self.prec)
        xr = self.x_rad + float(self.x_rad) * self.upper_prec / 100.
        yr = self.y_rad + float(self.y_rad) * self.upper_prec / 100.
        for x in xa :
            pt = [self.x_center + xr * np.cos(x),  self.y_center + yr * np.sin(x)]
            pts.append(pt)

        return pts

