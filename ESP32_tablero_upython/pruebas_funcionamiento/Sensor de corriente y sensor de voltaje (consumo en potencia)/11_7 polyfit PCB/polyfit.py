import numpy as np
#from matplotlib import pyplot as plt
import math

list_x = [0, 0.021]  #voltajes en el sensor
list_y = [0, 0.1818] # corrientes
coeficientes = np.polyfit(list_x, list_y, 1) #coeficientes de la funcion aproximada o equivalente
print(coeficientes)
'''
print(coeficientes)
x = np.array(list_x) #objeto array de numpy con el eje x
y = coeficientes[0] * pow(x,3) + coeficientes[1] * pow(x,2) + coeficientes[2] * x + coeficientes[3] #la función equivalente

plt.plot(x, y)
plt.show()
'''