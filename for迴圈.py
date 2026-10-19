import time
from math import sin,radians,cos

v_0 = 30
θ = radians(45)
g = 9.81

for t in range(10):

    x = v_0*t*cos(θ)
    y = v_0*t*sin(θ) - (0.5*g*t*t) 
    print (f"第{t}秒 x={x:.2f}公尺 y={y:.2f}公尺")

    time.sleep(1)