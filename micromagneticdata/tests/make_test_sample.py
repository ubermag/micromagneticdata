import os
import shutil
import oommfc as oc
import discretisedfield as df

name = "test_sample"

# Remove any previous simulation directories.
if os.path.exists(name):
    shutil.rmtree(name)

L = 30e-9   # (m)
cellsize = (10e-9, 15e-9, 5e-9)  # (m)
mesh = oc.Mesh((0, 0, 0), (L, L, L), cellsize)

system = oc.System(name=name)

A = 1.3e-11  # (J/m)
H = (1e6, 0.0, 2e5)
system.hamiltonian = oc.Exchange(A=A) + oc.Zeeman(H=H)

gamma = 2.211e5  # (m/As)
alpha = 0.02
system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)

Ms = 8e5  # (A/m)
system.m = df.Field(mesh, value=(0.0, 0.25, 0.1), norm=Ms)

td = oc.TimeDriver()
td.drive(system, t=25e-12, n=25)  # updates system.m in-place
td.drive(system, t=15e-12, n=15)
td.drive(system, t=5e-12, n=10)

md = oc.MinDriver()
md.drive(system)

system.hamiltonian.zeeman.H = (0.0, 0.0, 1.0e6)
td.drive(system, t=5e-12, n=5)
md.drive(system)
