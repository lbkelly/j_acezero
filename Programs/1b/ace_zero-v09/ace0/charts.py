#!/usr/env python

"""
Plotting routines for debugging and visualisation.
This module contains function for plotting the traces of aircraft using matplotlib.
"""

__author__ = 'mikepsn'

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
from mpl_toolkits.mplot3d import axes3d
import datetime
import platform
import sys
import numpy as np
import os


def draw_trajectories(trace1, trace2, vname, cname, path, viper_score, cobra_score, run_no): #

    title = vname + "(Blue" + str(viper_score) + ") VS " + cname + "(Red " + str(cobra_score) + ")" + "run " + str(run_no)

    header = "Blue: " + str(viper_score) + " VS Red: " + str(cobra_score)



    fig = plt.figure()

    ax = fig.gca(projection='3d')
    plt.grid(True)
    plt.title(header, loc='left')
    plt.axis('equal')

    ax.set_xlabel('x(object)')
    ax.set_ylabel('y(object)')
    ax.set_zlabel('z(object)')

    ta1, xa1, ya1, za1 = ([], [], [], [])
    for timeslice in trace1:
        t, x, y, z, vx, vy, vz, accel_x, accel_y, accel_z, psi, theta, phi, v, weight, fuel = timeslice
        ta1.append(t)
        xa1.append(x)
        ya1.append(y)
        za1.append(z)

    xmin = min(xa1)
    xmax = max(xa1)
    ymin = min(ya1)
    ymax = max(ya1)
    zmin = min(za1)
    zmax = max(za1)

    ta2, xa2, ya2, za2 = ([], [], [], [])
    for timeslice in trace2:
        t, x, y, z, vx, vy, vz, accel_x, accel_y, accel_z, psi, theta, phi, v, weight, fuel = timeslice
        ta2.append(t)
        xa2.append(x)
        ya2.append(y)
        za2.append(z)

    xmin = min(min(xa2), xmin)
    xmax = max(max(xa2), xmax)
    ymin = min(min(ya2), ymin)
    ymax = max(max(ya2), ymax)
    zmin = min(min(za2), zmin)
    zmax = max(max(za2), zmax)

    # Fix aspect ratio
    max_range = np.array([xmax - xmin, ymax - ymin, zmax - zmin]).max() / 2.0
    mid_x = (xmax + xmin) * 0.5
    mid_y = (ymax + ymin) * 0.5
    mid_z = (zmax + zmin) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    # Plot Trajectories
    plt.plot(xa1, ya1, za1, color='b')
    plt.plot(xa2, ya2, za2, color='r')

    # Draw t=0.0 marker for trace1
    #ax.text(xa1[0], ya1[0], za1[0]+1, "t = %2.1f" % ta1[0], color='b', alpha=0.5)
    ax.scatter(xa1[0], ya1[0], za1[0], color='b', marker='o', s=100, alpha=0.5)
    # and now trace2
    #ax.text(xa2[0], ya2[0], za2[0]+1, "t = %2.1f" % ta2[0], color='r', alpha=0.5)
    ax.scatter(xa2[0], ya2[0], za2[0], color='r', marker='o', s=100, alpha=0.5)

    # Draw t=tmax marker for trace1
    #ax.text(xa1[-1], ya1[-1], za1[-1]+1, "t = %2.1f" % ta1[-1], color='b', alpha=0.5)
    ax.scatter(xa1[-1], ya1[-1], za1[-1], color='b', marker='*', s=100, alpha=0.5)
    # and now for trace 2
    #ax.text(xa2[-1], ya2[-1], za2[-1]+1, "t = %2.1f" % ta2[-1], color='r', alpha=0.5)
    ax.scatter(xa2[-1], ya2[-1], za2[-1], color='r', marker='*', s=100, alpha=0.5)

    filename = title.replace(" ", "")

    plt.savefig(path + '/' + filename + "_frontview.png")

    ax.view_init(azim=90, elev=270)

    plt.savefig(path + '/' + filename + "_topview.png")

    ax.view_init(azim=90, elev=0)

    plt.savefig(path + '/' + filename + "_sideview.png")


def draw_platform_trace(trace, filename):
    """ Plots the trajectory of a single platform model over time."""

    title = "Platform Trajectory: (%s)\n%s\n%s)" % (datetime.datetime.now(),
                                                    platform.platform(),
                                                    sys.version)
    ta, xa, ya, za = ([], [], [], [])
    for timeslice in trace:
        t, x, y, z, psi, theta, phi, v, weight, fuel = timeslice
        #print (t, x, y, z), type(z), type(za)
        ta.append(t)
        xa.append(x)
        ya.append(y)
        za.append(z)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    plt.grid(True)
    plt.title(title, loc='left')
    plt.axis('equal')
    plt.plot(xa, ya, za)

    #ax.plot(xa, ya, zs=0.0, zdir='z', color='b', linestyle='--', alpha=0.5)
    #ax.plot(xa, za, zs=0.0, zdir='y', color='r', linestyle='--', alpha=0.5)
    #ax.plot(ya, za, zs=0.0, zdir='x', color='g', linestyle='--', alpha=0.5)

    #ax.set_xlim([0.0, 200.0])
    #ax.set_ylim([0.0, 200.0])
    #ax.set_zlim([0.0, 200.0])

    ax.text(xa[0], ya[0], za[0]+3, "t = %2.1f" % ta[0], color='b', alpha=0.3)
    ax.scatter(xa[0], ya[0], za[0], color='b', marker='o', s=100, alpha=0.3)

    ax.text(xa[-1], ya[-1], za[-1]+3, "t = %2.1f" % ta[-1], color='b', alpha=0.3)
    ax.scatter(xa[-1], ya[-1], za[-1], color='b', marker='>', s=100, alpha=0.3)

    plt.show()
    #plt.savefig('test_results/' + filename)


def multiple_run_chart_3d(traces):
    title = "1v1 WVR Air Combat: {} runs".format(len(traces))
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    plt.grid(True)
    plt.title(title, loc='left')
    plt.axis('equal')

    ax.set_xlabel('x(object)')
    ax.set_ylabel('y(object)')
    ax.set_zlabel('z(object)')

    for (trace1, trace2) in traces:
        ta1, xa1, ya1, za1 = ([], [], [], [])
        for timeslice in trace1:
            t, x, y, z, psi, theta, phi, v, weight, fuel = timeslice
            ta1.append(t)
            xa1.append(x)
            ya1.append(y)
            za1.append(z)

        # xmin = min(xa1)
        # xmax = max(xa1)
        # ymin = min(xa1)
        # ymax = max(ya1)
        # zmin = min(za1)
        # zmax = max(za1)

        ta2, xa2, ya2, za2 = ([], [], [], [])
        for timeslice in trace2:
            t, x, y, z, psi, theta, phi, v, weight, fuel = timeslice
            ta2.append(t)
            xa2.append(x)
            ya2.append(y)
            za2.append(z)

        # xmin = min(min(xa2), xmin)
        # xmax = max(max(xa2), xmax)
        # ymin = min(min(ya2), xmin)
        # ymax = max(max(ya2), ymax)
        # zmin = min(min(za2), zmin)
        # zmax = max(max(za2), zmax)


    # ax.set_xlim(xmin,xmax)
    # ax.set_ylim(ymin,ymax)
    # ax.set_zlim(zmin,zmax)
        ax.set_zlim(0,15000)

        # Plot Trajectories
        plt.plot(xa1, ya1, za1, color='b')
        plt.plot(xa2, ya2, za2, color='r')
        #
        #     # Draw t=0.0 marker for trace1
        # #ax.text(xa1[0], ya1[0], za1[0]+1, "t = %2.1f" % ta1[0], color='b', alpha=0.5)
        # ax.scatter(xa1[0], ya1[0], za1[0], color='b', marker='o', s=100, alpha=0.5)
        #     # and now trace2
        # #ax.text(xa2[0], ya2[0], za2[0]+1, "t = %2.1f" % ta2[0], color='r', alpha=0.5)
        # ax.scatter(xa2[0], ya2[0], za2[0], color='r', marker='o', s=100, alpha=0.5)
        #
        #     # Draw t=tmax marker for trace1
        # #ax.text(xa1[-1], ya1[-1], za1[-1]+1, "t = %2.1f" % ta1[-1], color='b', alpha=0.5)
        # ax.scatter(xa1[-1], ya1[-1], za1[-1], color='b', marker='*', s=100, alpha=0.5)
        #     # and now for trace 2
        # #ax.text(xa2[-1], ya2[-1], za2[-1]+1, "t = %2.1f" % ta2[-1], color='r', alpha=0.5)
        # ax.scatter(xa2[-1], ya2[-1], za2[-1], color='r', marker='*', s=100, alpha=0.5)

    plt.show()


def multiple_run_chart(traces):
    title = "1v1 WVR Air Combat: {} runs".format(len(traces))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.grid(True)
    plt.title(title, loc='left')
    plt.axis('equal')

    ax.set_xlabel('x(object)')
    ax.set_ylabel('y(object)')

    for (trace1, trace2) in traces:
        ta1, xa1, ya1 = ([], [], [])
        for timeslice in trace1:
            t, x, y, z, psi, theta, phi, v, weight, fuel = timeslice
            ta1.append(t)
            xa1.append(x)
            ya1.append(y)

        ta2, xa2, ya2 = ([], [], [])
        for timeslice in trace2:
            t, x, y, z, psi, theta, phi, v, weight, fuel = timeslice
            ta2.append(t)
            xa2.append(x)
            ya2.append(y)

        # Plot Trajectories
        plt.plot(xa1, ya1, color='b', alpha = 0.3)
        plt.plot(xa2, ya2, color='r', alpha = 0.3)

    plt.show()