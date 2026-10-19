from math import sin,radians,cos

θ = radians(45)
v_0 = 30 # m/s 常數
g = 9.81 #m/s^2 常數

R = v_0**2*sin(2*θ)/g
H = v_0**2*sin(θ)**2/(2*g)
T = 2*v_0*sin(θ)/g

print (f"射程 R = {R:.2f} 公尺")
print (f"最大高度 H = {H:.2f} 公尺")
print (f"飛行時間 T = {T:.2f} 秒")
