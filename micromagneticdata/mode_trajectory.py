import discretisedfield as df
import holoviews as hv
import numpy as np
import pandas as pd

hv.extension("bokeh", logo=False)


def saf_mesh():
    Lx = 64e-9
    Ly = 40e-9
    Lz = 1e-9
    cell = (1e-9, 1e-9, 1e-9)
    region = df.Region(p1=(-Lx / 2, -Ly / 2, 0), p2=(Lx / 2, Ly / 2, 3 * Lz))
    subregions = {
        "bottom": df.Region(p1=(-Lx / 2, -Ly / 2, 0), p2=(Lx / 2, Ly / 2, Lz)),
        "spacer": df.Region(p1=(-Lx / 2, -Ly / 2, Lz), p2=(Lx / 2, Ly / 2, 2 * Lz)),
        "top": df.Region(p1=(-Lx / 2, -Ly / 2, 2 * Lz), p2=(Lx / 2, Ly / 2, 3 * Lz)),
        "first_skyrmion_bottom_region": df.Region(
            p1=(-Lx / 2, -Ly / 2, 0), p2=(0, Ly / 2, Lz)
        ),
        "second_skyrmion_bottom_region": df.Region(
            p1=(0, -Ly / 2, 0), p2=(Lx / 2, Ly / 2, Lz)
        ),
        "first_skyrmion_top_region": df.Region(
            p1=(-Lx / 2, -Ly / 2, 2 * Lz), p2=(0, Ly / 2, 3 * Lz)
        ),
        "second_skyrmion_top_region": df.Region(
            p1=(0, -Ly / 2, 2 * Lz), p2=(Lx / 2, Ly / 2, 3 * Lz)
        ),
    }
    mesh = df.Mesh(region=region, cell=cell, subregions=subregions)
    return mesh


def region_colors():
    colours = {
        "first_skyrmion_top_region": "lime",
        "second_skyrmion_top_region": "lime",
        "first_skyrmion_bottom_region": "lime",
        "second_skyrmion_bottom_region": "lime",
    }
    return colours


def regions():
    subregions = [
        "first_skyrmion_top_region",
        "second_skyrmion_top_region",
        "first_skyrmion_bottom_region",
        "second_skyrmion_bottom_region",
    ]
    return subregions


class SkyrmionModeTrajectory:
    def __init__(self, mode_data, z_top=2.5e-9, z_bottom=5e-10):
        self.mode_data = mode_data
        self.mesh = saf_mesh()
        self.z_top = z_top
        self.z_bottom = z_bottom
        self.subregions = regions()
        self.colours = region_colors()
        self.fields = []
        self.vortex_centres = None

    def calculate_fields(self):
        """Calculate the field for each time step in the mode data."""
        time_steps = self.mode_data.sizes["t"]
        self.fields = [
            df.Field(self.mesh, nvdim=3, value=self.mode_data.isel(t=t).data)
            for t in range(time_steps)
        ]

    def final_visual(self):
        return self.get_top_layer() * self.get_top_core_positions(
            ["first_skyrmion_top_region", "second_skyrmion_top_region"]
        ) * self.get_top_trajectory(
            ["first_skyrmion_top_region", "second_skyrmion_top_region"]
        ) + self.get_bottom_layer() * self.get_bottom_core_positions(
            ["first_skyrmion_bottom_region", "second_skyrmion_bottom_region"]
        ) * self.get_bottom_trajectory(
            ["first_skyrmion_bottom_region", "second_skyrmion_bottom_region"]
        )

    def get_layers(self):
        return self.get_top_layer() + self.get_bottom_layer()

    def get_trajectories(self):
        return self.get_top_trajectory(
            ["first_skyrmion_top_region", "second_skyrmion_top_region"]
        ) + self.get_bottom_trajectory(
            ["first_skyrmion_bottom_region", "second_skyrmion_bottom_region"]
        )

    def compute_vortex_centres(self):
        """Compute the centre of mass for each subregion and each field."""
        vortex_data = []

        for subregion in self.subregions:
            for field in self.fields:
                r = field[subregion].sel("z").mesh.coordinate_field()
                tcd = df.tools.topological_charge_density(field[subregion].sel("z"))
                centre_of_mass = (r * tcd).integrate() / tcd.integrate()

                vortex_data.append(
                    {
                        "subregion": subregion,
                        "pos x": float(centre_of_mass[0]),
                        "pos y": float(centre_of_mass[1]),
                    }
                )

        self.vortex_centres = pd.DataFrame(vortex_data)

    def plot_core(self, t, subregion):
        """Plot the core position for a single time step and subregion."""
        if self.vortex_centres is None or self.vortex_centres.empty:
            raise ValueError(
                "vortex_centres is not computed. Run compute_vortex_centres first."
            )
        data = self.vortex_centres[self.vortex_centres["subregion"] == subregion]
        time_array = np.array(self.mode_data["t"])
        time_index = np.abs(time_array - t).argmin()
        if time_index >= len(data):
            return hv.Scatter([]).opts(
                size=0, color=self.colours.get(subregion), marker="o"
            )
        data_at_t = data.iloc[[time_index]][["pos x", "pos y"]]
        return hv.Scatter(data_at_t, kdims=["pos x"], vdims=["pos y"]).opts(
            size=5, color=self.colours.get(subregion), marker="o"
        )

    def get_core_positions(self, regions, title):
        """
        Generate dynamic core position overlays for specified regions.

        Parameters:
        - regions: List of subregions.
        - title: Title for the overlay (e.g., "Top Regions" or "Bottom Regions").

        Returns:
        - Holoviews Overlay for the specified regions.
        """
        overlays = [
            hv.DynamicMap(
                lambda t, sub=subregion: self.plot_core(t, subregion=sub), kdims=["t"]
            ).redim.values(t=self.mode_data["t"].values)
            for subregion in regions
        ]
        return hv.Overlay(overlays).collate().opts(title=title)

    def get_bottom_core_positions(self, bottom_regions):
        return self.get_core_positions(bottom_regions, "Bottom Regions")

    def get_top_core_positions(self, top_regions):
        return self.get_core_positions(top_regions, "Top Regions")

    def get_top_layer(self):
        return (
            hv.Dataset(
                self.mode_data.sel(vdims="z").sel(z=self.z_top, method="nearest")
            )
            .to(hv.Image, kdims=["x", "y"], dynamic=True)
            .opts(width=500, cmap="coolwarm", clim=(-1, 1), title="Top Layer")
        )

    def get_bottom_layer(self):
        return (
            hv.Dataset(
                self.mode_data.sel(vdims="z").sel(z=self.z_bottom, method="nearest")
            )
            .to(hv.Image, kdims=["x", "y"], dynamic=True)
            .opts(width=500, cmap="coolwarm", clim=(-1, 1), title="Bottom Layer")
        )

    def plot_trajectories(self, top_regions, bottom_regions):
        """
        Plot skyrmion trajectories for specified top and bottom regions.
        """
        top_overlay = self.get_top_trajectory(top_regions)
        bottom_overlay = self.get_bottom_trajectory(bottom_regions)
        return top_overlay.opts(title="Top Regions") + bottom_overlay.opts(
            title="Bottom Regions"
        )

    def get_top_trajectory(self, top_regions):
        return hv.NdOverlay(
            {
                subregion: hv.Curve(
                    self.vortex_centres[self.vortex_centres["subregion"] == subregion][
                        ["pos x", "pos y"]
                    ],
                    kdims=["pos x"],
                    vdims=["pos y"],
                ).opts(color=self.colours.get(subregion), width=500)
                for subregion in top_regions
            }
        ).opts(title="Top Regions", show_legend=False)

    def get_bottom_trajectory(self, bottom_regions):
        return hv.NdOverlay(
            {
                subregion: hv.Curve(
                    self.vortex_centres[self.vortex_centres["subregion"] == subregion][
                        ["pos x", "pos y"]
                    ],
                    kdims=["pos x"],
                    vdims=["pos y"],
                ).opts(color=self.colours.get(subregion), width=500)
                for subregion in bottom_regions
            }
        ).opts(title="Bottom Regions", show_legend=False)
