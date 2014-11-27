"""
Routines for creating plots of the Bloch Sphere
"""
# Adapted from QuTip: Qauntum Toolbox in Python
# http://qutip.org/docs/3.0.1/guide/guide-bloch.html

# All dependencies from the QuTiP package have been removed, and additional
# capabilities have been added (e.g. drawing precession circles)
#
import os

from .linalg import inner
from numpy import (ndarray, array, matrix, linspace, pi, outer, cos, sin, ones,
                   size, sqrt, real, mod, append, ceil, arange, zeros, asarray)

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d

    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)

            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)

            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)
except:
    pass

Sx = array([[0, 1], [1, 0]])
Sy = array([[0, -1j], [1j, 0]])
Sz = array([[1, 0], [0, -1]])

class Bloch():
    """Class for plotting data on the Bloch sphere.

    Attributes
    ----------

    axes : instance {None}
        User supplied Matplotlib axes for Bloch sphere animation.
    fig : instance {None}
        User supplied Matplotlib Figure instance for plotting Bloch sphere.
    font_color : str {'black'}
        Color of font used for Bloch sphere labels.
    font_size : int {20}
        Size of font used for Bloch sphere labels.
    frame_alpha : float {0.1}
        Sets transparency of Bloch sphere frame.
    frame_color : str {'gray'}
        Color of sphere wireframe.
    frame_width : int {1}
        Width of wireframe.
    wire_frame : boolean {True}
        Whether or not to plot the wireframe
    xyz_axes : int {2}
        Code for how coordinate axes should be drawn.
        xyz_axes = 1: Axes will be shown by a wireframe
        xyz_axes = 2: Axes will be shown by wireframe and axis arrows
    xyz_axis_extend: float {0.1}
        if xyz_axes=2, value by which to extend axis arrows beyond 1.0
    point_color : list {["b","r","g","#CC6600"]}
        List of colors for Bloch sphere point markers to cycle through.
        i.e. By default, points 0 and 4 will both be blue ('b').
    point_marker : list {["o","s","d","^"]}
        List of point marker shapes to cycle through.
    point_size : list {[25,32,35,45]}
        List of point marker sizes. Note, not all point markers look
        the same size when plotted!
    sphere_alpha : float {0.2}
        Transparency of Bloch sphere itself.
    sphere_color : str {'#FFDDDD'}
        Color of Bloch sphere.
    figsize : list {[7,7]}
        Figure size of Bloch sphere plot.  Best to have both numbers the same;
        otherwise you will have a Bloch sphere that looks like a football.
    vector_color : list {["g","#CC6600","b","r"]}
        List of vector colors to cycle through.
    vector_width : int {5}
        Width of displayed vectors.
    vector_style : str {'-|>', 'simple', 'fancy', ''}
        Vector arrowhead style (from matplotlib's arrow style).
    vector_mutation : int {20}
        Width of vectors arrowhead.
    precession_color : list {['gray']}
        List of colors for precession circles to cycle through
    precession_width : list {[1.0]}
        List of line widths for precession circles to cycle through
    precession_style : list {['--']}
        List of line styles for precession circles to cycle through
    view : list {[-60,30]}
        Azimuthal and Elevation viewing angles.
    xlabel : list {["$x$",""]}
        List of strings corresponding to +x and -x axes labels, respectively.
    xlpos : list {[1.1,-1.1]}
        Positions of +x and -x labels respectively.
    ylabel : list {["$y$",""]}
        List of strings corresponding to +y and -y axes labels, respectively.
    ylpos : list {[1.2,-1.2]}
        Positions of +y and -y labels respectively.
    zlabel : list {[r'$\\left|0\\right>$',r'$\\left|1\\right>$']}
        List of strings corresponding to +z and -z axes labels, respectively.
    zlpos : list {[1.2,-1.2]}
        Positions of +z and -z labels respectively.


    """
    def __init__(self, fig=None, axes=None, view=None, figsize=None,
                 background=False):

        # Figure and axes
        self.fig = fig
        self.axes = axes
        # Background axes, default = False
        self.background = background
        # The size of the figure in inches, default = [5,5].
        self.figsize = figsize if figsize else [5, 5]
        # Azimuthal and Elvation viewing angles, default = [-60,30].
        self.view = view if view else [-60, 30]
        # Color of Bloch sphere, default = #FFDDDD
        self.sphere_color = '#FFDDDD'
        # Transparency of Bloch sphere, default = 0.2
        self.sphere_alpha = 0.2
        # Color of wireframe, default = 'gray'
        self.frame_color = 'gray'
        # Width of wireframe, default = 1
        self.frame_width = 1
        # Plot wireframe?
        self.wire_frame = True
        # Transparency of wireframe, default = 0.2
        self.frame_alpha = 0.2
        # Mode in which the coordiante axes are shown
        self.xyz_axes = 2
        # If showing axis arrow, how far to extend beyond 1.0
        self.xyz_axis_extend = 0.1
        # Labels for x-axis (in LaTex)
        self.xlabel = ['$x$', '']
        # Position of x-axis labels
        self.xlpos = [1.2, -1.2]
        # Labels for y-axis (in LaTex)
        self.ylabel = ['$y$', '']
        # Position of y-axis labels
        self.ylpos = [1.2, -1.2]
        # Labels for z-axis (in LaTex),
        self.zlabel = [r'$\left|0\right>$', r'$\left|1\right>$']
        # Position of z-axis labels, default = [1.2, -1.2]
        self.zlpos = [1.2, -1.2]
        # ---font options---
        # Color of fonts, default = 'black'
        self.font_color = 'black'
        # Size of fonts, default = 20
        self.font_size = 20
        # Number of segments to use when drawing circles
        self.segments = 100

        # ---vector options---
        # List of colors for Bloch vectors, default = ['b','g','r','y']
        self.vector_color = ['g', '#CC6600', 'b', 'r']
        #: Width of Bloch vectors, default = 5
        self.vector_width = 3
        #: Style of Bloch vectors, default = '-|>' (or 'simple')
        self.vector_style = '-|>'
        #: Sets the width of the vectors arrowhead
        self.vector_mutation = 20

        # ---precessions options---
        # List of colors for precession circles
        self.precession_color = ['gray', ]
        # width of circles
        self.precession_width = [1.0, ]
        # Line style of circles
        self.precession_style = ['--']


        # ---point options---
        # List of colors for Bloch point markers, default = ['b','g','r','y']
        self.point_color = ['b', 'r', 'g', '#CC6600']
        # Size of point markers, default = 25
        self.point_size = [25, 32, 35, 45]
        # Shape of point markers, default = ['o','^','d','s']
        self.point_marker = ['o', 's', 'd', '^']

        # ---data lists---
        # Data for point markers
        self.points = []
        # Data for Bloch vectors
        self.vectors = []
        # Data for annotations
        self.annotations = []
        # Number of times sphere has been saved
        self.savenum = 0
        # Style of points, 'm' for multiple colors, 's' for single color
        self.point_style = []
        # Data for precession circles
        self.precessions = []

        # status of rendering
        self._rendered = False

    def set_label_convention(self, convention):
        """Set x, y and z labels according to one of conventions.

        Parameters
        ----------
        convention : string
            One of the following:
            - "original"
            - "xyz01"
            - "xyz"
            - "sx sy sz"
            - "01"
            - "polarization jones"
            - "polarization jones letters"
              see also: http://en.wikipedia.org/wiki/Jones_calculus
            - "polarization stokes"
              see also: http://en.wikipedia.org/wiki/Stokes_parameters
        """
        ketex = "$\\left.|%s\\right\\rangle$"
        # \left.| is on purpose, so that every ket has the same size

        if convention == "original":
            self.xlabel = ['$x$', '']
            self.ylabel = ['$y$', '']
            self.zlabel = ['$\\left|0\\right>$', '$\\left|1\\right>$']
        elif convention == "xyz01":
            self.xlabel = ['$x$', '']
            self.ylabel = ['$y$', '']
            self.zlabel = [r'$\left|0\right>$, $z$', '$\\left|1\\right>$']
        elif convention == "xyz":
            self.xlabel = ['$x$', '']
            self.ylabel = ['$y$', '']
            self.zlabel = ['$z$', '']
        elif convention == "sx sy sz":
            self.xlabel = ['$s_x$', '']
            self.ylabel = ['$s_y$', '']
            self.zlabel = ['$s_z$', '']
        elif convention == "01":
            self.xlabel = ['', '']
            self.ylabel = ['', '']
            self.zlabel = ['$\\left|0\\right>$', '$\\left|1\\right>$']
        elif convention == "polarization jones":
            self.xlabel = [ketex % "\\nearrow\\hspace{-1.46}\\swarrow",
                           ketex % "\\nwarrow\\hspace{-1.46}\\searrow"]
            self.ylabel = [ketex % "\\circlearrowleft", ketex %
                           "\\circlearrowright"]
            self.zlabel = [ketex % "\\leftrightarrow", ketex % "\\updownarrow"]
        elif convention == "polarization jones letters":
            self.xlabel = [ketex % "D", ketex % "A"]
            self.ylabel = [ketex % "L", ketex % "R"]
            self.zlabel = [ketex % "H", ketex % "V"]
        elif convention == "polarization stokes":
            self.ylabel = ["$\\nearrow\\hspace{-1.46}\\swarrow$",
                           "$\\nwarrow\\hspace{-1.46}\\searrow$"]
            self.zlabel = ["$\\circlearrowleft$", "$\\circlearrowright$"]
            self.xlabel = ["$\\leftrightarrow$", "$\\updownarrow$"]
        else:
            raise Exception("No such convention.")

    def __str__(self):
        s = ""
        s += "Bloch data:\n"
        s += "-----------\n"
        s += "Number of points:  " + str(len(self.points)) + "\n"
        s += "Number of vectors: " + str(len(self.vectors)) + "\n"
        s += "Number of precessions: " + str(len(self.precessions)) + "\n"
        s += "\n"
        s += "Bloch sphere properties:\n"
        s += "------------------------\n"
        s += "font_color:       " + str(self.font_color) + "\n"
        s += "font_size:        " + str(self.font_size) + "\n"
        s += "frame_alpha:      " + str(self.frame_alpha) + "\n"
        s += "frame_color:      " + str(self.frame_color) + "\n"
        s += "frame_width:      " + str(self.frame_width) + "\n"
        s += "wireframe:        " + str(self.wireframe) + "\n"
        s += "point_color:      " + str(self.point_color) + "\n"
        s += "point_marker:     " + str(self.point_marker) + "\n"
        s += "point_size:       " + str(self.point_size) + "\n"
        s += "sphere_alpha:     " + str(self.sphere_alpha) + "\n"
        s += "sphere_color:     " + str(self.sphere_color) + "\n"
        s += "figsize:          " + str(self.figsize) + "\n"
        s += "vector_color:     " + str(self.vector_color) + "\n"
        s += "vector_width:     " + str(self.vector_width) + "\n"
        s += "vector_style:     " + str(self.vector_style) + "\n"
        s += "vector_mutation:  " + str(self.vector_mutation) + "\n"
        s += "precession_color: " + str(self.precession_color) + "\n"
        s += "precession_width: " + str(self.precession_width) + "\n"
        s += "precession_style: " + str(self.precession_style) + "\n"
        s += "view:             " + str(self.view) + "\n"
        s += "xlabel:           " + str(self.xlabel) + "\n"
        s += "xlpos:            " + str(self.xlpos) + "\n"
        s += "ylabel:           " + str(self.ylabel) + "\n"
        s += "ylpos:            " + str(self.ylpos) + "\n"
        s += "zlabel:           " + str(self.zlabel) + "\n"
        s += "zlpos:            " + str(self.zlpos) + "\n"
        return s

    def _repr_png_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'png')
        plt.close(self.fig)
        return fig_data

    def _repr_svg_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'svg').decode('utf-8')
        plt.close(self.fig)
        return fig_data

    def clear(self):
        """Resets Bloch sphere data sets to empty.
        """
        self.points = []
        self.vectors = []
        self.point_style = []
        self.annotations = []

    def add_points(self, points, meth='s'):
        """Add a list of data points to bloch sphere.

        Parameters
        ----------
        points : array/list
            Collection of data points.

        meth : str {'s', 'm', 'l'}
            Type of points to plot, use 'm' for multicolored, 'l' for points
            connected with a line.

        """
        if not isinstance(points[0], (list, ndarray)):
            points = [[points[0]], [points[1]], [points[2]]]
        points = array(points)
        if meth == 's':
            if len(points[0]) == 1:
                pnts = array([[points[0][0]], [points[1][0]], [points[2][0]]])
                pnts = append(pnts, points, axis=1)
            else:
                pnts = points
            self.points.append(pnts)
            self.point_style.append('s')
        elif meth == 'l':
            self.points.append(points)
            self.point_style.append('l')
        else:
            self.points.append(points)
            self.point_style.append('m')

    def add_precession(self, point, axis):
        """Add a precession circle of the given point rotating around the given
        axis"""
        axis_norm = sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
        u = array(axis) / axis_norm
        self.precessions.append( (array(point), u) )

    def plot_precessions(self):
        """Draw all precession circles"""
        def rot_matrix(u, theta):
            """General rotation matrix for rotation around axis u with angle
            theta

            Source: http://en.wikipedia.org/wiki/Rotation_matrix
            """
            ux, uy, uz = array(u)
            COS = cos(theta)
            SIN = sin(theta)
            R = array([
            [COS+ux**2*(1-COS), ux*uy*(1-COS)-uz*SIN, ux*uz*(1-COS)+uy*SIN],
            [uy*ux*(1-COS)+uz*SIN, COS+uy**2*(1-COS), uy*uz*(1-COS)-ux*SIN],
            [uz*ux*(1-COS)-uy*SIN, uz*uy*(1-COS)+ux*SIN, COS+uz**2*(1-COS)]
            ])
            return R

        thetas = linspace(0, 2*pi, self.segments)

        for k in range(len(self.precessions)):

            point, u = self.precessions[k]
            xs = zeros(len(thetas))
            ys = zeros(len(thetas))
            zs = zeros(len(thetas))

            for i, theta in enumerate(thetas):
                R = rot_matrix(u, theta)
                xs[i], ys[i], zs[i] = R.dot(point)

            color = self.precession_color[mod(k, len(self.precession_color))]
            lw    = self.precession_width[mod(k, len(self.precession_width))]
            ls    = self.precession_style[mod(k, len(self.precession_style))]

            # -X and Y data are switched for plotting purposes,
            # cf.  plot_vectors
            self.axes.plot(ys, -xs, zs, zdir='z', ls='--', lw=lw,
                           color=color)

    def add_vectors(self, vectors):
        """Add a list of vectors to Bloch sphere.

        Parameters
        ----------
        vectors : array/list
            Array with vectors of unit length or smaller.

        """
        if isinstance(vectors[0], (list, ndarray)):
            for vec in vectors:
                self.vectors.append(vec)
        else:
            self.vectors.append(vectors)

    def add_annotation(self, vector, text, **kwargs):
        """Add a text or LaTeX annotation to Bloch sphere,
        parametrized by a vector.

        Parameters
        ----------
        vector :array/list/tuple
            Position for the annotaion.

        text : str/unicode
            Annotation text.
            You can use LaTeX, but remember to use raw string
            e.g. r"$\\langle x \\rangle$"
            or escape backslashes
            e.g. "$\\\\langle x \\\\rangle$".

        **kwargs :
            Options as for mplot3d.axes3d.text, including:
            fontsize, color, horizontalalignment, verticalalignment.
        """
        if isinstance(vector, (list, ndarray, tuple)) \
                and len(vector) == 3:
            vec = vector
        else:
            raise Exception("Position needs to be specified by a qubit " +
                            "state or a 3D vector.")
        self.annotations.append({'position': vec,
                                 'text': text,
                                 'opts': kwargs})

    def make_sphere(self):
        """
        Plots Bloch sphere and data sets.
        """
        self.render(self.fig, self.axes)

    def render(self, fig=None, axes=None):
        """
        Render the Bloch sphere and its data sets in on given figure and axes.
        """
        if self._rendered:
            self.axes.clear()

        self._rendered = True

        # Figure instance for Bloch sphere plot
        if not fig:
            self.fig = plt.figure(figsize=self.figsize)

        if not axes:
            self.axes = Axes3D(self.fig, azim=self.view[0], elev=self.view[1])

        if self.background:
            self.axes.clear()
            self.axes.set_xlim3d(-1.3, 1.3)
            self.axes.set_ylim3d(-1.3, 1.3)
            self.axes.set_zlim3d(-1.3, 1.3)
        else:
            self.plot_xyz_axes()
            self.axes.set_axis_off()
            self.axes.set_xlim3d(-0.7, 0.7)
            self.axes.set_ylim3d(-0.7, 0.7)
            self.axes.set_zlim3d(-0.7, 0.7)

        self.axes.grid(False)
        self.plot_back()
        self.plot_points()
        self.plot_vectors()
        self.plot_precessions()
        self.plot_front()
        self.plot_axes_labels()
        self.plot_annotations()

    def plot_back(self):
        # back half of sphere
        u = linspace(0, pi, self.segments/2)
        v = linspace(0, pi, self.segments/2)
        x = outer(cos(u), sin(v))
        y = outer(sin(u), sin(v))
        z = outer(ones(size(u)), cos(v))
        self.axes.plot_surface(x, y, z, rstride=2, cstride=2,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha)
        # wireframe
        if self.wireframe:
            self.axes.plot_wireframe(x, y, z, rstride=5, cstride=5,
                                    color=self.frame_color,
                                    alpha=self.frame_alpha)
        # equator
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='z',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='x',
                       lw=self.frame_width, color=self.frame_color)

    def plot_front(self):
        # front half of sphere
        u = linspace(-pi, 0, self.segments/2)
        v = linspace(0, pi, self.segments/2)
        x = outer(cos(u), sin(v))
        y = outer(sin(u), sin(v))
        z = outer(ones(size(u)), cos(v))
        self.axes.plot_surface(x, y, z, rstride=2, cstride=2,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha)
        # wireframe
        if self.wireframe:
            self.axes.plot_wireframe(x, y, z, rstride=5, cstride=5,
                                    color=self.frame_color,
                                    alpha=self.frame_alpha)
        # equator
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u),
                       zs=0, zdir='z', lw=self.frame_width,
                       color=self.frame_color)
        self.axes.plot(1.0 * cos(u), 1.0 * sin(u),
                       zs=0, zdir='x', lw=self.frame_width,
                       color=self.frame_color)

    def plot_xyz_axes(self):
        # axes
        if self.xyz_axes > 0:
            span = linspace(-1.0, 1.0, 2)
            self.axes.plot(span, 0 * span, zs=0, zdir='z', label='X',
                        lw=self.frame_width, color=self.frame_color)
            self.axes.plot(0 * span, span, zs=0, zdir='z', label='Y',
                        lw=self.frame_width, color=self.frame_color)
            self.axes.plot(0 * span, span, zs=0, zdir='y', label='Z',
                        lw=self.frame_width, color=self.frame_color)
        if self.xyz_axes == 2:
            arr_y = Arrow3D((0,1+self.xyz_axis_extend), (0,0), (0,0),
                    mutation_scale=self.vector_mutation,
                    lw=2*self.frame_width, arrowstyle=self.vector_style,
                    color=self.frame_color)
            self.axes.add_artist(arr_y)
            arr_x = Arrow3D((0,0), (0,-(1+self.xyz_axis_extend)), (0,0),
                    mutation_scale=self.vector_mutation,
                    lw=2*self.frame_width, arrowstyle=self.vector_style,
                    color=self.frame_color)
            self.axes.add_artist(arr_x)
            arr_z = Arrow3D((0,0), (0,0), (0,1+self.xyz_axis_extend),
                    mutation_scale=self.vector_mutation,
                    lw=2*self.frame_width, arrowstyle=self.vector_style,
                    color=self.frame_color)
            self.axes.add_artist(arr_z)

    def plot_axes_labels(self):
        # axes labels
        opts = {'fontsize': self.font_size,
                'color': self.font_color,
                'horizontalalignment': 'center',
                'verticalalignment': 'center'}
        self.axes.text(0, -self.xlpos[0], 0, self.xlabel[0], **opts)
        self.axes.text(0, -self.xlpos[1], 0, self.xlabel[1], **opts)

        self.axes.text(self.ylpos[0], 0, 0, self.ylabel[0], **opts)
        self.axes.text(self.ylpos[1], 0, 0, self.ylabel[1], **opts)

        self.axes.text(0, 0, self.zlpos[0], self.zlabel[0], **opts)
        self.axes.text(0, 0, self.zlpos[1], self.zlabel[1], **opts)

        for a in (self.axes.w_xaxis.get_ticklines() +
                  self.axes.w_xaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.w_yaxis.get_ticklines() +
                  self.axes.w_yaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.w_zaxis.get_ticklines() +
                  self.axes.w_zaxis.get_ticklabels()):
            a.set_visible(False)

    def plot_vectors(self):
        # -X and Y data are switched for plotting purposes
        for k in range(len(self.vectors)):

            xs3d = self.vectors[k][1] * array([0, 1])
            ys3d = -self.vectors[k][0] * array([0, 1])
            zs3d = self.vectors[k][2] * array([0, 1])

            color = self.vector_color[mod(k, len(self.vector_color))]

            if self.vector_style == '':
                # simple line style
                self.axes.plot(xs3d, ys3d, zs3d,
                               zs=0, zdir='z', label='Z',
                               lw=self.vector_width, color=color)
            else:
                # decorated style, with arrow heads
                a = Arrow3D(xs3d, ys3d, zs3d,
                            mutation_scale=self.vector_mutation,
                            lw=self.vector_width,
                            arrowstyle=self.vector_style,
                            color=color)

                self.axes.add_artist(a)

    def plot_points(self):
        # -X and Y data are switched for plotting purposes
        for k in range(len(self.points)):
            num = len(self.points[k][0])
            dist = [sqrt(self.points[k][0][j] ** 2 +
                         self.points[k][1][j] ** 2 +
                         self.points[k][2][j] ** 2) for j in range(num)]
            if any(abs(dist - dist[0]) / dist[0] > 1e-12):
                # combine arrays so that they can be sorted together
                zipped = list(zip(dist, range(num)))
                zipped.sort()  # sort rates from lowest to highest
                dist, indperm = zip(*zipped)
                indperm = array(indperm)
            else:
                indperm = arange(num)
            if self.point_style[k] == 's':
                self.axes.scatter(
                    real(self.points[k][1][indperm]),
                    - real(self.points[k][0][indperm]),
                    real(self.points[k][2][indperm]),
                    s=self.point_size[mod(k, len(self.point_size))],
                    alpha=1,
                    edgecolor='none',
                    zdir='z',
                    color=self.point_color[mod(k, len(self.point_color))],
                    marker=self.point_marker[mod(k, len(self.point_marker))])

            elif self.point_style[k] == 'm':
                pnt_colors = array(self.point_color *
                                   ceil(num / float(len(self.point_color))))

                pnt_colors = pnt_colors[0:num]
                pnt_colors = list(pnt_colors[indperm])
                marker = self.point_marker[mod(k, len(self.point_marker))]
                s = self.point_size[mod(k, len(self.point_size))]
                self.axes.scatter(real(self.points[k][1][indperm]),
                                  -real(self.points[k][0][indperm]),
                                  real(self.points[k][2][indperm]),
                                  s=s, alpha=1, edgecolor='none',
                                  zdir='z', color=pnt_colors,
                                  marker=marker)

            elif self.point_style[k] == 'l':
                color = self.point_color[mod(k, len(self.point_color))]
                self.axes.plot(real(self.points[k][1]),
                               -real(self.points[k][0]),
                               real(self.points[k][2]),
                               alpha=0.75, zdir='z',
                               color=color)

    def plot_annotations(self):
        # -X and Y data are switched for plotting purposes
        for annotation in self.annotations:
            vec = annotation['position']
            opts = {'fontsize': self.font_size,
                    'color': self.font_color,
                    'horizontalalignment': 'center',
                    'verticalalignment': 'center'}
            opts.update(annotation['opts'])
            self.axes.text(vec[1], -vec[0], vec[2],
                           annotation['text'], **opts)

    def show(self):
        """
        Display Bloch sphere and corresponding data sets.
        """
        self.render(self.fig, self.axes)
        if self.fig:
            plt.show(self.fig)

    def save(self, name=None, format='png', dirc=None):
        """Saves Bloch sphere to file of type ``format`` in directory ``dirc``.

        Parameters
        ----------

        name : str
            Name of saved image. Must include path and format as well.
            i.e. '/Users/Paul/Desktop/bloch.png'
            This overrides the 'format' and 'dirc' arguments.
        format : str
            Format of output image.
        dirc : str
            Directory for output images. Defaults to current working directory.

        Returns
        -------
        File containing plot of Bloch sphere.

        """
        self.render(self.fig, self.axes)
        if dirc:
            if not os.path.isdir(os.getcwd() + "/" + str(dirc)):
                os.makedirs(os.getcwd() + "/" + str(dirc))
        if name is None:
            if dirc:
                plt.savefig(os.getcwd() + "/" + str(dirc) + '/bloch_' +
                            str(self.savenum) + '.' + format)
            else:
                plt.savefig(os.getcwd() + '/bloch_' + str(self.savenum) +
                            '.' + format)
        else:
            plt.savefig(name)
        self.savenum += 1
        if self.fig:
            plt.close(self.fig)


def bloch_coordinates(state, normalize=True):
    """Given a two-level quantum state, return the coordinates x, y, z on the
    Bloch sphere

    The state can be a Hilbert space state, in which case it should be a vector
    consisting of two complex coefficients for Ket{0} and Ket{1}, or it can be
    a density (numpy) matrix.

    The `normalize` parameter is only applied to Hilbert space states.

    >>> import numpy as np
    >>> [round(v, 5) for v in bloch_coordinates((1,1))]
    [1.0, 0.0, 0.0]
    >>> [round(v, 5) for v in bloch_coordinates((1,0))]
    [0.0, 0.0, 1.0]
    >>> [round(v, 5) for v in bloch_coordinates((0,1))]
    [0.0, 0.0, -1.0]
    >>> [round(v, 5) for v in bloch_coordinates((1j,1))]
    [0.0, -1.0, 0.0]
    >>> [round(v, 5) for v in bloch_coordinates(np.array([1j,1]))]
    [0.0, -1.0, 0.0]
    >>> [round(v, 5) for v in bloch_coordinates(state=(1j,1),normalize=False)]
    [0.0, -2.0, 0.0]
    >>> [round(v, 5) for v in bloch_coordinates(np.array([[1,0.5], [0.5,1]]))]
    [1.0, 0.0, 0.0]
    >>> [round(v, 5) for v in bloch_coordinates(np.array([[1,0], [0,1]]))]
    [0.0, 0.0, 0.0]
    """
    if isinstance(state, tuple) or isinstance(state, list):
        hilbert_space = True
    elif len(state.shape) == 1:
        hilbert_space = True
    elif len(state.shape) == 2:
        hilbert_space = False
    if hilbert_space:
        a0 = state[0]
        a1 = state[1]
        if normalize:
            vec_norm = sqrt(abs(a0)**2 + abs(a1**2))
            a0 /= vec_norm
            a1 /= vec_norm
        rho = array([[a0*a0.conjugate(), a0*a1.conjugate()],
                    [a1*a0.conjugate(), a1*a1.conjugate()] ])
    else:
        rho = asarray(state)
    return inner(Sx, rho).real, inner(Sy, rho).real, inner(Sz, rho).real


def _hide_tick_lines_and_labels(axis):
    '''
    Set visible property of ticklines and ticklabels of an axis to False
    '''
    for a in axis.get_ticklines() + axis.get_ticklabels():
        a.set_visible(False)
