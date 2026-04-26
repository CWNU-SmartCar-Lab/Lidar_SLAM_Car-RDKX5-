Expect_Value=200
Measure=0
r=100
b=200
wc=30
wo=110
v1=0
h=0.005
z1=0
z2=0
z3=0
fh=-r*r*(-200)
v1+=0
v2=fh*h
Beita_01=3*wo
Beita_02=3*wo*wo
Beita_03=wo*wo*wo

e=z1
z1+=(z2-Beita_01*e)*h
z2+=(z3-Beita_02*e)*h
z3+=-Beita_03*e*h

kp=wc*wc
kd=2*wc

e1=v1-z1
e2=v2-z2
u=kp*e1+kd*e2

u=(u-z3)/b

print("u=",u)
print("e1=",e1)
print("e2=",e2)


