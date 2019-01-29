import matplotlib.pyplot as plt

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
