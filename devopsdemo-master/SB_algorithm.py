import numpy as np
import scipy.io as sio
m = sio.loadmat("E:\devopsdemo-master\devopsdemo-master\mat\data.mat")
Field = np.matrix(m['Field']).getH()
Empty = np.matrix(m['Empty']).getH()
Sen = np.matrix(m['Sen']).getH()
Topo = np.matrix(m['Topo']).getH()
Coord = np.matrix(m['Coord']).getH()
F = np.empty([64, 1], dtype=float)
S = np.empty([64, 318], dtype=float)
I = np.identity(318)

for i in range(64):
    F[i, 0] = abs((Field[i, 0] - Empty[i, 0]) / Empty[i, 0])
for i in range(318):
    for j in range(64):
        S[j, i] = abs((Sen[j, i] - Empty[j, 0]) / Empty[j, 0])

# s = np.matrix(S).getH()
Ans_SB = np.empty([318, 1])
A1=S
f=F
mu=10
lamda=0.0001
err=0.01
d=np.zeros([318,1])
b=np.zeros([318,1])
u=np.zeros([318,1])
Z=np.zeros([318,1])
u=np.squeeze(u)
b=np.squeeze(b)
d=np.squeeze(d)
Z=np.squeeze(Z)
f=np.squeeze(f)
A2=A1.T
Ft=np.dot(A1.T,f)*mu
IV=(mu*(np.dot(A2,A1))+lamda*np.ones([318,318]))
C=np.linalg.pinv(IV)

up=np.ones([318,1])
# up=np.squeeze(up)
# print("up=",up)
# print(np.shape(up))
# print(type(up))
# print("u=",u)
# print(np.shape(u))
# print(type(u))
# print("b=",b)
# print(np.shape(b))
# print(type(b))
# print("A2=",A2)
# print(np.shape(A2))
# print(type(A2))
# print("Ft=",Ft)
# print(np.shape(Ft))
# print(type(Ft))
# print("IV=",IV)
# print(np.shape(IV))
# print(type(IV))
# print("C=",C)
# print(np.shape(C))
# print(type(C))



#
for i in range(20):
       up=u
       u=np.dot(C,Ft+lamda*(d-b))
       tmp=u+b
       # print("tmp=",tmp)
       # print(np.shape(tmp))
       # print(type(tmp))
       # print("u=",u)
       # print(np.shape(u))
       # print(type(u))
       # print("d=",d)
       # print(np.shape(d))
       # print(type(d))
       # print("b=",b)
       # print(np.shape(b))
       # print(type(b))
       # print("up=",up)
       # print(np.shape(up))
       # print(type(up))

       # d=(np.sign(tmp))*(np.max(Z,abs(tmp)-(1/lamda)))
       # b=tmp-d
       b=tmp



for i in range(318):
    Ans_SB[i] = (up[i] - min(up)) / (max(up) - min(up))
    Ans_SB[i]=pow(Ans_SB[i],1.5)
X = np.matrix(m['Coord'])[:, 0]
Y = np.matrix(m['Coord'])[:, 1]
Flat1 = np.concatenate((Topo, Ans_SB.T), axis=0).T
Interp1 = np.empty([681, 1])

for i in range(681):
    _e = 0
    _sum = 0
    for j in range(318):
        for k in range(3):
            if Flat1[j, k] - 1 == i:
                _e = _e + 1
                _sum = _sum + Flat1[j, 3]
        if _e == 0:
           Interp1[i, 0] = 0
        else:
            Interp1[i, 0] = _sum / _e

Num1 = np.concatenate((Coord, Interp1.T), axis=0).T
arr = []
for i in range(681):
    if Num1[i, 2] == 0:
       arr.append(i)
Num1 = np.delete(Num1, arr, axis=0)

Num2 = {}

for i in range(182):
    Num3 = {}
    Num3['x'] = str(Num1[i, 0])
    Num3['y'] = str(Num1[i, 1])
    Num3['grey'] = str(Num1[i, 2])
    Num2[i] = Num3
# with open('data.json', 'a')as f:
#     json.dump(Num2,f)
#
#      # print(Num2)
#
# print('mytable')
# Num2 = json.dumps(Num2)
print(Num2)
# return(Num2)
     # return render_template('image.html', result_json = json.dumps(Num2))



