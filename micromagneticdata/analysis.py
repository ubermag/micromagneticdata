import k3d
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import discretisedfield as df

import ipywidgets as widgets
from IPython.display import display


class PlotFig:
    def __init__(self, data):
        self.data = data.dt
        self.time_slider = widgets.IntRangeSlider(
            description='Time: ',
            value=(0, len(self.data.index)),
            min=0, max=len(self.data.index),
            continuous_update=False,
            layout=widgets.Layout(width='99%')
        )
        self.columns = widgets.SelectMultiple(
            options=self.data.columns,
            value=['mx', 'my'],
            rows=len(self.data.columns),
            disabled=False,
            layout=widgets.Layout(width='200px')
        )
        self.out = widgets.Output()

        self.time_slider.observe(self.update)
        self.columns.observe(self.update)
        self.update(None)

    def update(self, val):
        self.out.clear_output(wait=True)
        left, right = self.time_slider.value
        values = self.columns.value

        plt.figure(figsize=(8, 5))

        # process ['mx', 'my', 'mz'] if exist, left axis always
        left_axis = False
        m = ['mx', 'my', 'mz']
        for value in m:
            if value in values:
                left_axis = True
                ax = plt.plot(
                    self.data['tm'].iloc[left:right+1],
                    self.data[value].iloc[left:right+1],
                    label=value
                )
                plt.xlabel('Time')
                plt.ylabel('m')
                plt.legend()
        values = list(set(values) - set(m))

        # left axis for first value, if ['mx', 'my', 'mz'] not exist
        if not left_axis and values:
            left_axis = True
            value = values[0]
            values = values[1:]
            ax = plt.plot(
                    self.data['tm'].iloc[left:right+1],
                    self.data[value].iloc[left:right+1],
                    label=value
            )
            plt.xlabel('Time')
            plt.ylabel(value)
            plt.legend()

        # right axis, if additional vale exist
        if values:
            ax2 = plt.twinx()
            value = values[0]
            plt.plot(
                self.data['tm'].iloc[left:right+1],
                self.data[value].iloc[left:right+1],
                label=value,
                color='black',
            )
            plt.ylabel(value)
            plt.legend()

        with self.out:
            display(plt.gcf())
        plt.close()

    def _ipython_display_(self):

        box1 = widgets.VBox([self.time_slider])
        box2 = widgets.VBox([box1, self.out])
        box3 = widgets.HBox([self.columns, box2])
        display(box3)


class Plot3D:
    def __init__(self, data):
        self.data = data
        self.time_slider = widgets.IntSlider(
            description='Time: ',
            value=0,
            min=0,
            max=max(self.data.dt.index),
            # continuous_update=False,
            layout=widgets.Layout(width='99%')
        )

        self.vectors = self.vectors_plot

        self.out = widgets.Output()

        self.time_slider.observe(self.update)
        self.update(None)

    def get_coord_and_vect(self, dt):
        # Plot arrows only with norm > 0.
        data = [(i, dt(i)) for i in dt.mesh.coordinates
                if dt.norm(i) > 0]
        coordinates, vectors = zip(*data)
        coordinates, vectors = np.array(coordinates), np.array(vectors)

        # Middle of the arrow at the cell centre.
        coordinates -= 0.5 * vectors

        # To avoid the warning
        coordinates = coordinates.astype(np.float32)
        vectors = vectors.astype(np.float32)

        return coordinates, vectors

    def get_colors(self, vectors, colormap='viridis'):
        cmap = matplotlib.cm.get_cmap(colormap, 256)

        vc = vectors[..., 0]
        vc = np.interp(vc, (vc.min(), vc.max()), (0, 1))
        colors = cmap(vc)
        colors = [int('0x{}'.format(matplotlib.colors.to_hex(rgb)[1:]), 16)
                  for rgb in colors]
        colors = list(zip(colors, colors))

        return colors

    @property
    def vectors_plot(self):
        plot = k3d.plot()
        plot.camera_auto_fit = False
        plot.grid_auto_fit = False

        field = self.get_field
        coord, vect = self.get_coord_and_vect(field)
        colors = self.get_colors(vect)

        vectors = k3d.vectors(coord, vect, colors=colors)
        plot += vectors
        plot.display()

        return vectors

    @property
    def omf_files(self):
        files = []
        for drive in self.data.iterate('step_filenames'):
            files.extend(list(drive))
        return files

    @property
    def get_field(self):
        filename = self.omf_files[self.time_slider.value]
        return df.read(filename)

    def update(self, val):
        self.out.clear_output(wait=True)

        field = self.get_field
        coor, vect = self.get_coord_and_vect(field)
        self.vectors.vectors = vect

    def _ipython_display_(self):
        box1 = widgets.VBox([self.time_slider])
        box2 = widgets.VBox([box1, self.out])
        display(box2)


class PlotPlane:
    def __init__(self, data):
        self.data = data.m0
        self.coord_select = widgets.ToggleButtons(
            options=['x', 'y', 'z'],
            description='Coordinate:',
            disabled=False
        )
        self.min, self.max, self.cell, self.value = self.coord_min_max
        self.coord_slider = widgets.FloatSlider(
            description='Value',
            value=self.value,
            min=self.min,
            max=self.max,
            step=self.cell,
            disabled=False,
            continuous_update=False,
            readout=True,
            readout_format='.2f',
            layout=widgets.Layout(width='35%')
        )
        self.output = widgets.Output()
        self.coord_select.observe(self.update)
        self.coord_slider.observe(self.update)
        self.update(None)

    @property
    def coord_min_max(self):
        coord = {'x': 0, 'y': 1, 'z': 2}
        coord = {0: 'x', 1: 'y', 2: 'z'}
        for i in range(3):
            if self.coord_select.value == coord[i]:
                # min = min of mesh + 1/2 cell size for this component
                # max = max of mesh - 1/2 cell size for this component
                # value = middle of mesh + 1/2 cell size
                data = {}
                data['cell'] = self.data.mesh.l[i] / self.data.mesh.n[i]
                data['min'] = self.data.mesh.pmin[i] + data['cell'] / 2.0
                data['max'] = self.data.mesh.pmax[i] - data['cell'] / 2.0
                data['value'] = data['min'] + (data['max'] - data['min']) / 2.0 + data['cell'] / 2.0
                return data['min'], data['max'], data['cell'], data['value']

    def update(self, val):
        self.output.clear_output(wait=True)
        coord = self.coord_select.value
        value = self.coord_slider.value

        self.coord_slider.min, self.coord_slider.max, self.coord_slider.cell, _ = self.coord_min_max

        x, y, z = None, None, None
        if coord == 'x': x = value;
        if coord == 'y': y = value;
        if coord == 'z': z = value;

        self.data.plot_plane(x=x, y=y, z=z)

        with self.output:
            display(plt.gcf())
        plt.close()

    def _ipython_display_(self):

        box1 = widgets.VBox([self.coord_select])
        box2 = widgets.VBox([box1, self.coord_slider])
        box3 = widgets.VBox([box2, self.output])
        display(box3)
