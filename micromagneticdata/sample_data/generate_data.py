"""This module can be used to recompute the sample data shipped with micromagneticdata.

Sample data is used for the documentation notebooks and doctests to keep the examples
and documentation more (proper physics, without having to properly fake micromagnetic
simulations). Running the simulations requires oommfc and OOMMF.

The sample_data should not be used for any unit tests in micromagneticdata.
"""

import os
import shutil

import discretisedfield as df
import micromagneticmodel as mm
import oommfc as oc


def clean(system_name):
    """Remove any previous simulation directories."""
    if os.path.exists(system_name):
        print(">>> Removing old test samples")
        shutil.rmtree(system_name)


def rectangle():
    """Simple rectangular ferromagnetic sample in external magnetic field."""
    print(">>> Running ferromagnetic rectangular cuboid")
    p1 = (-50e-9, -25e-9, 0)
    p2 = (50e-9, 25e-9, 20e-9)
    cell = (5e-9, 5e-9, 5e-9)

    region = df.Region(p1=p1, p2=p2)
    # use the region also as subregion: discretisedfield will create the additional
    # subregions json file and we can detect misalignment (translation) of the
    # region from the calculators (e.g. Mumax3 always defines pmin at the origin)
    mesh = df.Mesh(region=region, cell=cell, subregions={"total": region})

    Ms = 8e5
    A = 1.3e-11
    H = (1e6, 0.0, 2e5)
    alpha = 0.02

    system = mm.System(name="rectangle")
    system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
    system.dynamics = mm.Precession(gamma0=mm.consts.gamma0) + mm.Damping(alpha=alpha)
    system.m = df.Field(mesh, nvdim=3, value=(0.0, 0.25, 0.1), norm=Ms)

    td = oc.TimeDriver()
    td.drive(system, t=25e-12, n=25)
    td.drive(system, t=5e-10, n=250)

    # md = mc.MinDriver()
    # md.drive(system, dirname=dirname)  # drive-4

    # system.energy.zeeman.H = (0.0, 0.0, 1.0e6)

    # # OOMMF
    # td = oc.TimeDriver()
    # td.drive(system, t=5e-12, n=5, dirname=dirname)  # drive-5

    # md = oc.MinDriver()
    # md.drive(system, dirname=dirname, output_step=True)  # drive-6


def vortex():
    """Vortex dynamics after displacing with magnetic field."""
    print(">>> Running vortex dynamics")
    L = 100e-9  # sample edge length (m)
    thickness = 5e-9  # sample thickness (m)
    Ms = 8e5  # saturation magnetisation (A/m)
    A = 13e-12  # exchange energy constant (J/m)
    gamma0 = mm.consts.gamma0  # gyromagnetic ratio (m/As)
    alpha = 0.2  # Gilbert damping

    system = mm.System(name="vortex")
    system.energy = mm.Exchange(A=A) + mm.Demag()
    system.dynamics = mm.Precession(gamma0=gamma0) + mm.Damping(alpha=alpha)

    def m_init(point):
        x, y, z = point
        c = 1e9  # (1/m)
        return (-c * y, c * x, 0.1)

    region = df.Region(
        p1=(-L / 2, -L / 2, -thickness / 2), p2=(L / 2, L / 2, thickness / 2)
    )
    mesh = df.Mesh(region=region, cell=(5e-9, 5e-9, 5e-9))
    system.m = df.Field(mesh, nvdim=3, value=m_init, norm=Ms)

    md = oc.MinDriver()
    md.drive(system, comment="vortex equilibrium state")

    H = (1e4, 0, 0)  # an external magnetic field (A/m)
    system.energy += mm.Zeeman(H=H)
    md.drive(system, comment="displace vortex with external field")

    system.energy.zeeman.H = (0, 0, 0)
    td = oc.TimeDriver()
    td.drive(system, t=5e-9, n=250, comment="remove external field and relax vortex")


if __name__ == "__main__":
    clean("rectangle")
    clean("vortex")
    rectangle()
    vortex()
