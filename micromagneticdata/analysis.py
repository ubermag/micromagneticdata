import k3d
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


class VectorField:
    def __init__(self, data):
        self.data = data
        self.time_slider = widgets.IntSlider(
            description='Time: ',
            value=0,
            min=0,
            max=max(self.data.dt.index),
            continuous_update=False,
            layout=widgets.Layout(width='99%')
        )
        self.vectors = self.vectors_plot
        self.out = widgets.Output()
        self.time_slider.observe(self.update)
        self.update(None)

    @property
    def get_field(self):
        filename = self.omf_files[self.time_slider.value]
        return df.read(filename)

    @property
    def omf_files(self):
        files = []
        for drive in self.data.iterate('step_filenames'):
            files.extend(list(drive))
        return files

    @property
    def vectors_plot(self):
        plot = k3d.plot()
        plot.camera_auto_fit = False
        plot.grid_auto_fit = False

        field = self.get_field
        coord, vect = field.get_coord_and_vect(field.mesh.coordinates)
        colors = df.plot3d.get_colors(vect)

        vectors = k3d.vectors(coord, vect, colors=colors)
        plot += vectors
        plot.display()

        return vectors

    def update(self, val):
        self.out.clear_output(wait=True)

        field = self.get_field
        coor, vect = field.get_coord_and_vect(field.mesh.coordinates)
        self.vectors.vectors = vect

    def _ipython_display_(self):
        box1 = widgets.VBox([self.time_slider])
        box2 = widgets.VBox([box1, self.out])
        display(box2)


class VectorFieldSlice:
    @property
    def get_field(self):
        filename = self.omf_files[self.time_slider.value]
        return df.read(filename)

    @property
    def omf_files(self):
        files = []
        for drive in self.data.iterate('step_filenames'):
            files.extend(list(drive))
        return files

    def coord_min_max(self, field):
        coord = {0: 'x', 1: 'y', 2: 'z'}
        for i in range(3):
            if self.coord_select.value == coord[i]:
                # min = min of mesh + 1/2 cell size for this component
                # max = max of mesh - 1/2 cell size for this component
                # value = middle of mesh + 1/2 cell size
                data = dict()
                data['cell'] = field.mesh.l[i] / field.mesh.n[i]
                data['min'] = field.mesh.pmin[i] + data['cell'] / 2.0
                data['max'] = field.mesh.pmax[i] - data['cell'] / 2.0
                data['value'] = data['min'] + \
                    (data['max'] - data['min']) / 2.0 + data['cell'] / 2.0
                return data['min'], data['max'], data['cell'], data['value']

    def __init__(self, data):
        self.data = data
        self.coord_select = widgets.ToggleButtons(
            options=['x', 'y', 'z'],
            description='Coordinate:',
            disabled=False
        )
        self.min, self.max, self.cell, self.value = 0, 10, 0.1, 0.0
        self.coord_slider = widgets.FloatSlider(
            description='Value',
            min=self.min,
            max=self.max,
            step=self.cell,
            value=self.value,
            disabled=False,
            continuous_update=False,
            readout=True,
            readout_format='.2f',
            layout=widgets.Layout(width='35%')
        )
        self.time_slider = widgets.IntSlider(
            description='Time: ',
            value=0,
            min=0,
            max=max(self.data.dt.index),
            continuous_update=False,
            layout=widgets.Layout(width='99%')
        )
        self.vectors = False
        self.plot = k3d.plot()
        self.plot.camera_auto_fit = False
        self.plot.grid_auto_fit = False
        self.plot.display()

        self.out = widgets.Output()
        self.coord_select.observe(self.update, names='value')
        self.coord_slider.observe(self.update, names='value')
        self.time_slider.observe(self.update)
        self.update(None)

    def update(self, val):
        self.out.clear_output(wait=True)

        plot = self.plot
        if self.vectors is not False:
            plot -= self.vectors

        coord = self.coord_select.value
        value = self.coord_slider.value

        x, y, z = None, None, None
        if coord == 'x': x = value;
        if coord == 'y': y = value;
        if coord == 'z': z = value;

        field = self.get_field
        self.coord_slider.min, \
        self.coord_slider.max, \
        self.coord_slider.step, \
        _ = self.coord_min_max(field)
        coor, vect = field.get_coord_and_vect(field.mesh.plane(x=x, y=y, z=z))
        colors = df.plot3d.get_colors(vect)

        self.vectors = k3d.vectors(coor, vect, colors=colors)
        plot += self.vectors

    def _ipython_display_(self):
        box0 = widgets.VBox([self.coord_select])
        box1 = widgets.VBox([box0, self.coord_slider])
        box2 = widgets.VBox([box1, self.time_slider])
        box3 = widgets.VBox([box2, self.out])
        display(box3)


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
        self.coord_slider.observe(self.update, names='value')
        self.update(None)

    @property
    def coord_min_max(self):
        coord = {0: 'x', 1: 'y', 2: 'z'}
        for i in range(3):
            if self.coord_select.value == coord[i]:
                # min = min of mesh + 1/2 cell size for this component
                # max = max of mesh - 1/2 cell size for this component
                # value = middle of mesh + 1/2 cell size
                data = dict()
                data['cell'] = self.data.mesh.l[i] / self.data.mesh.n[i]
                data['min'] = self.data.mesh.pmin[i] + data['cell'] / 2.0
                data['max'] = self.data.mesh.pmax[i] - data['cell'] / 2.0
                data['value'] = data['min'] + \
                    (data['max'] - data['min']) / 2.0 + data['cell'] / 2.0
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
