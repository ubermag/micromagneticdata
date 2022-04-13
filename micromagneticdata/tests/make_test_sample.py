import os
import shutil

import discretisedfield as df
import micromagneticmodel as mm
import oommfc as mc

dirname = "./test_sample"
name = "system_name"

# Remove any previous simulation directories.
if os.path.exists(name):
    shutil.rmtree(name)

p1 = (0, 0, 0)
p2 = (100e-9, 50e-9, 20e-9)
cell = (5e-9, 5e-9, 5e-9)

region = df.Region(p1=p1, p2=p2)
mesh = df.Mesh(region=region, cell=cell)

Ms = 8e5
A = 1.3e-11
H = (1e6, 0.0, 2e5)
alpha = 0.02

system = mm.System(name=name)
system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
system.dynamics = mm.Precession(gamma0=mm.consts.gamma0) + mm.Damping(alpha=alpha)
system.m = df.Field(mesh, dim=3, value=(0.0, 0.25, 0.1), norm=Ms)

td = mc.TimeDriver()
td.drive(system, t=25e-12, n=25, dirname=dirname)  # drive-0
td.drive(system, t=15e-12, n=15, dirname=dirname)  # drive-1
td.drive(system, t=5e-12, n=10, dirname=dirname)  # drive-2

md = mc.MinDriver()
md.drive(system, dirname=dirname)  # drive-3

system.energy.zeeman.H = (0.0, 0.0, 1.0e6)
td.drive(system, t=5e-12, n=5, dirname=dirname)  # drive-4

md.drive(system, dirname=dirname, output_step=True)  # drive-5

hd = mc.HysteresisDriver()
hd.drive(system, Hmin=(0, 0, 1e6), Hmax=(0, 0, -1e6), n=21, dirname=dirname)  # drive-6
