# importing libraries
from scipy.optimize import curve_fit
import numpy as np

# declaring the Fitting class
# this class is used to fit the data to a linear model
class Fitting:
    # processing the data for solar time to set the angular displacement
    # starting at zero degrees
    def angular_dis_solar(self, θ):
        θr = np.radians(θ)
        disp = θr - θr[0]
        return abs(disp)

    # processing the data for sidereal time to set the angular displacement
    # starting at zero degrees
    def angular_dis_sidereal(self, θx, θy):
        xr = np.radians(θx)
        yr = np.radians(θy)
        dx = xr - xr[0]
        dy = yr - yr[0]
        disp = np.sqrt(dx*dx + dy*dy)
        return disp

    # processing the time data to set the time at zero seconds
    def process_time(self, t):
        return t - t[0]

    # declaring the linear model for the fitting
    def linear_model(self, t, a0, a1):
        return a0 + a1 * t

    # fitting the data to a linear model
    # this function fits the data to a linear model and returns the parameters
    def linear_fit(self, x, y, yerr=None):
        p0 = [0.0, 2*np.pi/(24*3600)]  # guess: 0 intercept, one rev/day
        if yerr is not None:
            popt, pcov = curve_fit(
                self.linear_model, x, y,
                sigma=yerr, absolute_sigma=True,
                p0=p0
            )
        else:
            popt, pcov = curve_fit(
                self.linear_model, x, y,
                p0=p0
            )
        perr = np.sqrt(np.diag(pcov))
        return popt, perr

    # determine the period based on the fitted parameters with 24hrs
    def calculate_t0(self, ω, δω):
        t0  = (2 * np.pi / ω) / 3600.0
        δt0 = ((2 * np.pi) / (ω**2)) * δω / 3600.0
        return t0, δt0
