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

s = np.matrix(S).getH()## s是S逆矩阵
# LBP = s * F
# Tik = (s * S + 0.01 * I).I*(s * F)
lp=(s * S + 0.1 * I).I*(s * F)
m=S.shape[0]## S的行数
n=S.shape[1]## S的列数
Ans_LP = np.empty([318, 1])
A=np.zeros([64,1])
B=np.zeros([318,1])
B=np.squeeze(np.array(B))
A=np.squeeze(np.array(A))
for i in range(2):
    alfa=1e-8
    beta=1e-8
    q=1
    p=2
    lamda=1e-3
    for j in range(m):
        A[j]=((F[j]-np.dot(S[j,:],lp))**2+alfa)**(q-2)/2
        # np.append(A[j],((F[j]-np.dot(S[j,:],lp))**2+alfa)**(q-2)/2)
    a=q*(np.diag(A))


    # s=np.squeeze(np.array(s))
    lp=np.squeeze(np.array(lp))
    # S=np.squeeze(np.array(S))
    a=np.squeeze(np.array(a))
    # # b=np.squeeze(np.asarray(b))
    F=np.squeeze(np.array(F))

    # A=np.array(A)
    # B=np.array(B)
    # F=np.array(F)
    # a=np.array(a)
    S=np.array(S)
    # lp=np.array(lp)
    s=np.array(s)
    # print(np.shape(s))
    # print(np.shape(a))
    # print(np.shape(S))
    # print(np.shape(lp))
    # print(np.shape(F))
    # print(np.shape(A))
    # print(np.shape(B))


    for k in range(0,n):
        # B = np.concatenate(B, axis=0)
        # lp= np.concatenate(lp, axis=0)
        # print(B)
        # print(lp)
        # print(B[0])
        # print(lp[0])
        B[k]=(lp[k]**2+beta)**(p-2)/2
        # np.append(B[k],(lp[k]**2+beta)**(p-2)/2)

        b=p*np.diag(B)
        # print("lp=",lp)
        # print(np.shape(lp))
        # print(np.shape(b))
        # print("F=",F)
        # print(np.shape(F))
        # print("B=",B)
        # print(np.shape(B))
        c=np.dot(S,lp)-F
        # print("c=",c)
        # print(np.shape(c))
        d=np.dot(a,c)
        # print("d=",d)
        # print(np.shape(d))
        e=np.dot(b,lp)
        # print("e=",e)
        # print(np.shape(e))
        f1=np.squeeze(np.array(np.dot(s,d)+lamda*e))
        # print("f1=",f1)
        # print(np.shape(f1))

        f2=np.squeeze(np.array(np.dot(s,(np.dot(a,S)))+lamda*b))
        # print("f2=",f2)
        # print(np.shape(f2))

        f=np.linalg.pinv(f2)
        # print("f=",f)
        # print(np.shape(f))
        # print("f*f1=",f*f1)
        # print(np.shape(f*f1))
        lp=lp-np.dot(f,f1)
        # print("lp=",lp)
        # print(np.shape(lp))




for i in range(318):
    Ans_LP[i] = (lp[i] - min(lp)) / (max(lp) - min(lp))
    Ans_LP[i]=pow(Ans_LP[i],3)
X = Coord[:, 0]
Y = Coord[:, 1]
Flat1 = np.concatenate((Topo, Ans_LP.T), axis=0).T
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



