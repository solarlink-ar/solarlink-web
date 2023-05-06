import numpy as np
from matplotlib import pyplot as plt
import math

list_x = [0, 0.09, 0.77, 1.14]  #voltajes en el sensor
list_y = [0, 76, 716, 1141] # potencias asociadas a los voltajes en el sensor
coeficientes = np.polyfit(list_x, list_y, 3) #coeficientes de la funcion aproximada o equivalente

print(coeficientes)
x = np.array([0, 0.09, 0.77, 1.14]) #objeto array de numpy con el eje x
y = coeficientes[0] * pow(x,3) + coeficientes[1] * pow(x,2) + coeficientes[2] * x + coeficientes[3] #la función equivalente

plt.plot(x, y)
plt.show()
plt.savefig("respuesta del sensor.png")