import math as m #導入數學計算相關函式庫
# as m 把數學函式庫別稱為m
from math import sin,radians,cos #從數學函式庫導入sin函式和弳度函式
θ = radians(45) #角度30轉成弳度 常數
t = 1  #sec 自變量
v_0 = 30 # m/s 常數
g = 9.81 #m/s^2 常數
"""
輸入
"""
x = v_0*t*cos(θ)
y = v_0*t*sin(θ) - (0.5*g*t*t) 
"""
函數(模型)(規則
)
"""
print(x) #應變量
print(y) #應變量
"""
輸出
"""