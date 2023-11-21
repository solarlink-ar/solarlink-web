import numpy as np
from matplotlib import pyplot as plt

list_x = []
list_y = [-0.04875149, -0.09112779, -0.07106466, -0.002812586, 0.07012713, 0.09225282, 0.05006403, -0.02662581, -0.08569011, -0.08400256, -0.02568829, 0.05268911, 0.09169029, 0.06843959, -0.0007500229, -0.07293972, -0.0918778, -0.04781396, 0.02981341, 0.08700266]

num = 0
for i in range(20):
    list_x.append(num)
    num += 1/860

x = np.array(list_x)
y = np.array(list_y)

'''
func = np.polyfit(list_x, list_y, 2)
print(func)

'''

plt.title('Medicion de corriente')
plt.xlabel('Tiempo (segs)')
plt.ylabel('Corriente pico')
plt.plot(list_x, list_y)
plt.savefig("grafico.png")
