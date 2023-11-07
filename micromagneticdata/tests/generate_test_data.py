import os
import shutil

import discretisedfield as df
import micromagneticmodel as mm
import oommfc as oc

try:
    import mumax3c as mc

    mc.runner.autoselect_runner()
except OSError:
    import warnings

    warnings.warn("Mumax3 is not available; using OOMMF instead")
    import oommfc as mc


dirname = "./test_sample"


def clean():
    """Remove any previous simulation directories."""
    if os.path.exists(dirname):
        print(">>> Removing old test samples")
        shutil.rmtree(dirname)


def test_sample():
    """Simple rectangular ferromagnetic sample in external magnetic field."""
    print(">>> Running test sample")
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

    system = mm.System(name="system_name")
    system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
    system.dynamics = mm.Precession(gamma0=mm.consts.gamma0) + mm.Damping(alpha=alpha)
    system.m = df.Field(mesh, nvdim=3, value=(0.0, 0.25, 0.1), norm=Ms)

    # OOMMF
    td = oc.TimeDriver()
    td.drive(system, t=25e-12, n=25, dirname=dirname)  # drive-0

    # mumax3
    td = mc.TimeDriver()
    td.drive(system, t=15e-12, n=15, dirname=dirname)  # drive-1
    td.drive(system, t=5e-10, n=250, dirname=dirname)  # drive-2

    try:
        rd = mc.RelaxDriver()
    except AttributeError:
        rd = oc.MinDriver
    rd.drive(system, dirname=dirname)  # drive-3

    md = mc.MinDriver()
    md.drive(system, dirname=dirname)  # drive-4

    system.energy.zeeman.H = (0.0, 0.0, 1.0e6)

    # OOMMF
    td = oc.TimeDriver()
    td.drive(system, t=5e-12, n=5, dirname=dirname)  # drive-5

    md = oc.MinDriver()
    md.drive(system, dirname=dirname, output_step=True)  # drive-6


def vortex():
    """Vortex dynamics after displacing with magnetic field."""
    print(">>> Running vortex dynamics")
    L = 100e-9  # sample edge length (m)
    thickness = 5e-9  # sample thickness (m)
    Ms = 8e5  # saturation magnetisation (A/m)
    A = 13e-12  # exchange energy constant (J/m)
    gamma0 = mm.consts.gamma0  # gyromagnetic ratio (m/As)
    alpha = 0.2  # Gilbert damping

    system = mm.System(name="vortex_dynamics")
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
    md.drive(system, dirname=dirname)

    H = (1e4, 0, 0)  # an external magnetic field (A/m)
    system.energy += mm.Zeeman(H=H)

    md.drive(system, dirname=dirname)
    system.energy.zeeman.H = (0, 0, 0)

    td = oc.TimeDriver()
    td.drive(system, t=5e-9, n=250, dirname=dirname)


def hysteresis():
    """Hysteresis of a magnetic sphere with excange, uniaxial anisotropy and DMI."""
    print(">>> Running hysteresis simulation")
    region = df.Region(p1=(-50e-9, -50e-9, -50e-9), p2=(50e-9, 50e-9, 50e-9))
    mesh = df.Mesh(region=region, cell=(5e-9, 5e-9, 5e-9))

    system = mm.System(name="hysteresis")
    system.energy = (
        mm.Exchange(A=1e-12)
        + mm.UniaxialAnisotropy(K=4e5, u=(0, 0, 1))
        + mm.DMI(D=1e-3, crystalclass="T")
    )

    def Ms_fun(point):
        x, y, z = point
        if x**2 + y**2 + z**2 <= 50e-9**2:
            return 1e6
        else:
            return 0

    system.m = df.Field(mesh, nvdim=3, value=(0, 0, -1), norm=Ms_fun)

    Hmin = (0, 0, -1 / mm.consts.mu0)
    Hmax = (0, 0, 1 / mm.consts.mu0)

    hd = oc.HysteresisDriver()
    hd.drive(system, Hmin=Hmin, Hmax=Hmax, n=21, dirname=dirname)


if __name__ == "__main__":
    clean()
    test_sample()
    vortex()
    hysteresis()
