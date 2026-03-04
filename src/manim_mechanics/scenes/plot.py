import numpy as np
import matplotlib.pyplot as plt

SF = 1

m = 2 # kg
l = 0.2 * SF # m
k = 100 # N/m
c = 10 # Ns/m
r0 = 0.01 # m
omega = 2 # rad/s
g = 9.81 # m/s^2

x0 = 0
v0 = 1

omega_n = np.sqrt((4 * k / m - g / l) / 10)
zeta = (c / (10*m)) / (2 * omega_n)
omega_d = omega_n * np.sqrt(1 - zeta**2)

C1 = x0
C2 = (v0 + zeta * omega_n * x0) / omega_d


def phi_of_t(tt: float) -> float:
    return np.exp(- zeta * omega_n * tt) * ( C1 * np.cos(omega_d * tt) + C2 * np.sin(omega_d * tt))

t = np.linspace(0, 10, 1000)

fi = phi_of_t(t)

plt.plot(t, fi)
plt.show()