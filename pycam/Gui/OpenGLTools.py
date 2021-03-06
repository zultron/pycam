# -*- coding: utf-8 -*-
"""
$Id$

Copyright 2010-2011 Lars Kruse <devel@sumpfralle.de>

This file is part of PyCAM.

PyCAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCAM.  If not, see <http://www.gnu.org/licenses/>.
"""

from pycam.Geometry.PointUtils import *
from pycam.Geometry.utils import sqrt

# careful import
try:
    import OpenGL.GL as GL
    import OpenGL.GLUT as GLUT
except (ImportError, RuntimeError):
    pass

import math


def keep_gl_mode(func):
    def keep_gl_mode_wrapper(*args, **kwargs):
        prev_mode = GL.glGetIntegerv(GL.GL_MATRIX_MODE)
        result = func(*args, **kwargs)
        GL.glMatrixMode(prev_mode)
        return result
    return keep_gl_mode_wrapper

def keep_matrix(func):
    def keep_matrix_wrapper(*args, **kwargs):
        pushed_matrix_mode = GL.glGetIntegerv(GL.GL_MATRIX_MODE)
        GL.glPushMatrix()
        result = func(*args, **kwargs)
        final_matrix_mode = GL.glGetIntegerv(GL.GL_MATRIX_MODE)
        GL.glMatrixMode(pushed_matrix_mode)
        GL.glPopMatrix()
        GL.glMatrixMode(final_matrix_mode)
        return result
    return keep_matrix_wrapper

@keep_matrix
def draw_direction_cone(p1, p2, position=0.5, precision=12, size=0.1):
    distance = psub(p2, p1)
    length = pnorm(distance)
    direction = pnormalized(distance)
    if direction is None:
        # zero-length line
        return
    cone_length = length * size
    cone_radius = cone_length / 3.0
    # move the cone to the middle of the line
    GL.glTranslatef((p1[0] + p2[0]) * position,
            (p1[1] + p2[1]) * position, (p1[2] + p2[2]) * position)
    # rotate the cone according to the line direction
    # The cross product is a good rotation axis.
    cross = pcross(direction, (0, 0, -1))
    if pnorm(cross) != 0:
        # The line direction is not in line with the z axis.
        try:
            angle = math.asin(sqrt(direction[0] ** 2 + direction[1] ** 2))
        except ValueError:
            # invalid angle - just ignore this cone
            return
        # convert from radians to degree
        angle = angle / math.pi * 180
        if direction[2] < 0:
            angle = 180 - angle
        GL.glRotatef(angle, cross[0], cross[1], cross[2])
    elif direction[2] == -1:
        # The line goes down the z axis - turn it around.
        GL.glRotatef(180, 1, 0, 0)
    else:
        # The line goes up the z axis - nothing to be done.
        pass
    # center the cone
    GL.glTranslatef(0, 0, -cone_length * position)
    # draw the cone
    GLUT.glutSolidCone(cone_radius, cone_length, precision, 1)

@keep_gl_mode
@keep_matrix
def draw_complete_model_view(settings):
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    # draw the drill
    if settings.get("show_drill"):
        cutter = settings.get("cutter")
        if not cutter is None:
            color = settings.get("color_cutter")
            GL.glColor4f(color["red"], color["green"], color["blue"], color["alpha"])
            GL.glFinish()
            cutter.to_OpenGL()
    if settings.get("show_drill_progress") \
            and settings.get("toolpath_in_progress"):
        # show the toolpath that is currently being calculated
        toolpath_in_progress = settings.get("toolpath_in_progress")
        # do a quick conversion from a list of Paths to a list of points
        moves = []
        for path in toolpath_in_progress:
            for point in path.points:
                moves.append((point, False))
        if not toolpath_in_progress is None:
            draw_toolpath(moves, settings.get("color_toolpath_cut"),
                    settings.get("color_toolpath_return"),
                    show_directions=settings.get("show_directions"),
                    lighting=settings.get("view_light"))

