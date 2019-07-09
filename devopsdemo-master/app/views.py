
from flask import Flask,render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
from app.models import User
import pymysql
pymysql.install_as_MySQLdb()
import scipy.io as sio
import numpy as np
import json
import time





@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [{ 'author': { 'nickname': '' },
               'body': '欢迎来到EMT在线实验平台，现在开始你的实验之旅吧' }]
    return render_template('index.html',posts=posts)


@app.route('/status')
@login_required
def status():
    from app.utils.operations import local
    from decimal import Decimal
    
    os_fqdn = local('hostname --fqdn')

    os_release = local('cat /etc/*-release |head -n 1 |cut -d= -f2 |sed s/\\"//g')

    mem_kb = local("""grep -w "MemTotal" /proc/meminfo |awk '{print $2}'""")
    # mem_mb = Decimal(mem_kb)/Decimal(1024)
    # os_memory = round(mem_mb,2)

    cpu_type = local("""grep 'model name' /proc/cpuinfo |uniq |awk -F : '{print $2}' |sed 's/^[ \t]*//g' |sed 's/ \+/ /g'""")
    cpu_cores = local("""grep 'processor' /proc/cpuinfo |sort |uniq |wc -l""")

    nics = local("""/sbin/ifconfig |grep "Link encap" |awk '{print $1}' |grep -wv 'lo' |xargs""")
    nics_list = nics.split()
    t_nic_info = ""
    for i in nics_list:
        ipaddr = local("""/sbin/ifconfig %s |grep -w "inet addr" |cut -d: -f2 | awk '{print $1}'""" % (i))
        if ipaddr:
            t_nic_info = t_nic_info + i + ":" + ipaddr + ", "

    disk_usage = local("""df -hP |grep -Ev 'Filesystem|tmpfs' |awk '{print $3"/"$2" "$5" "$6", "}' |xargs""")

    top_info = local('top -b1 -n1 |head -n 5')
    top_info_list = top_info.split('\n')

    return render_template('status.html',
                            os_fqdn=os_fqdn,
                            os_release=os_release,
                            # os_memory=os_memory,
                            cpu_type=cpu_type,
                            cpu_cores=cpu_cores,
                            os_network=t_nic_info,
                            disk_usage=disk_usage,
                            top_info_list=top_info_list)


# @app.route('/operations', methods=['GET', 'POST'])
# @login_required
# def operations():
#     import paramiko
#     from app.utils.operations import remote
#     from config import basedir
#     from app.forms import OperationsForm
#
#     def isup(hostname):
#         import socket
#
#         conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         conn.settimeout(2)
#         try:
#             conn.connect((hostname,22))
#             conn.close()
#         except:
#             return False
#         return True
#
#     form = OperationsForm()
#     if form.validate_on_submit():
#         username = 'dong'
#         pkey = basedir + '/sshkeys/id_rsa'
#
#         hostname = form.hostname.data
#         cmd = form.cmd.data
#
#         if not isup(hostname):
#             return render_template('operations.html',form=form,failed_host=hostname)
#
#         blacklist = ['reboot', 'shutdown', 'poweroff',
#                      'rm', 'mv', '-delete', 'source', 'sudo',
#                      '<', '<<', '>>', '>']
#         for item in blacklist:
#             if item in cmd.split():
#                 return render_template('operations.html',form=form,blacklisted_word=item)
#
#         try:
#             out = remote(cmd,hostname=hostname,username=username,pkey=pkey)
#         except paramiko.AuthenticationException:
#             return render_template('operations.html',form=form,hostname=hostname,failed_auth=True)
#
#         failed_cmd = out.failed
#         succeeded_cmd = out.succeeded
#
#         return render_template('operations.html',
#                                 form=form,
#                                 cmd=cmd,
#                                 hostname=hostname,
#                                 out=out,
#                                 failed_cmd=failed_cmd,
#                                 succeeded_cmd=succeeded_cmd)
#
#     return render_template('operations.html',form=form)
#
#
# @app.route('/racktables', methods=['GET', 'POST'])
# @login_required
# def racktables():
#     from app.utils.operations import local
#     from config import basedir
#     from app.forms import RacktablesForm
#
#     form = RacktablesForm()
#     if form.validate_on_submit():
#         param_do = form.do_action.data
#         objectname = form.objectname.data
#         objecttype = form.objecttype.data
#         param_s = form.rackspace.data
#         param_p = form.rackposition.data
#
#         script = basedir + "/scripts/racktables.py"
#
#         if param_do == 'help':
#             cmd = "{0} -h".format(script)
#
#         if param_do == 'get':
#             cmd = "{0}".format(script)
#             if objectname:
#                 cmd = "{0} {1}".format(script,objectname)
#
#         if param_do == 'list':
#             cmd = "{0} {1} -l".format(script,objectname)
#
#         if param_do == 'read':
#             cmd = "{0} {1} -r".format(script,objectname)
#             if objecttype == 'offline_mode':
#                 cmd = cmd + " -o"
#             if objecttype == 'patch_panel':
#                 cmd = cmd + " -b"
#             if objecttype == 'network_switch':
#                 cmd = cmd + " -n"
#             if objecttype == 'network_security':
#                 cmd = cmd + " -f"
#             if objecttype == 'pdu':
#                 cmd = cmd + " -u"
#
#         if param_do == 'write':
#             cmd = "{0} {1} -w".format(script,objectname)
#             if param_s:
#                 cmd = cmd + " -s {0}".format(param_s)
#             if param_p != 'none':
#                 cmd = cmd + " -p {0}".format(param_p)
#             if objecttype == 'offline_mode':
#                 cmd = cmd + " -o"
#             if objecttype == 'patch_panel':
#                 cmd = cmd + " -b"
#             if objecttype == 'network_switch':
#                 cmd = cmd + " -n"
#             if objecttype == 'network_security':
#                 cmd = cmd + " -f"
#             if objecttype == 'pdu':
#                 cmd = cmd + " -u"
#
#         if param_do == 'delete':
#             cmd = "{0} {1} -d".format(script,objectname)
#
#         out = local(cmd)
#
#         failed_cmd = out.failed
#         succeeded_cmd = out.succeeded
#
#         return render_template('racktables.html',
#                                 form=form,
#                                 cmd=cmd,
#                                 out=out,
#                                 failed_cmd=failed_cmd,
#                                 succeeded_cmd=succeeded_cmd)
#
#     return render_template('racktables.html',form=form)
#
#
# @app.route('/hadoop', methods=['GET', 'POST'])
# @login_required
# def hadoop():
#     import paramiko
#     from app.utils.operations import remote
#     from config import basedir
#     from app.forms import HadoopForm
#
#     def isup(hostname):
#         import socket
#
#         conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         conn.settimeout(2)
#         try:
#             conn.connect((hostname,22))
#             conn.close()
#         except:
#             return False
#         return True
#
#     form = HadoopForm()
#     if form.validate_on_submit():
#         username = 'dong'
#         pkey = basedir + '/sshkeys/id_rsa'
#
#         param_do = form.do_action.data
#         slave_hostname = form.slave_hostname.data
#         master_hostname = form.master_hostname.data
#
#         if master_hostname == 'none':
#             return render_template('hadoop.html',form=form,none_host=True)
#
#         if master_hostname in ['idc1-hnn1', 'idc2-hnn1']:
#             script = '/root/bin/excludedn'
#
#         if master_hostname in ['idc1-hrm1', 'idc2-hrm1']:
#             script = '/root/bin/excludeyn'
#
#         if param_do == 'exclude':
#             cmd = "sudo {0} {1}".format(script,slave_hostname)
#
#         if param_do == 'recover':
#             cmd = "sudo {0} -r {1}".format(script,slave_hostname)
#
#         if not isup(master_hostname):
#             return render_template('hadoop.html',form=form,failed_host=master_hostname)
#
#         try:
#             out = remote(cmd,hostname=master_hostname,username=username,pkey=pkey)
#         except paramiko.AuthenticationException:
#             return render_template('hadoop.html',form=form,master_hostname=master_hostname,failed_auth=True)
#
#         failed_cmd = out.failed
#         succeeded_cmd = out.succeeded
#
#         return render_template('hadoop.html',
#                                 form=form,
#                                 cmd=cmd,
#                                 master_hostname=master_hostname,
#                                 out=out,
#                                 failed_cmd=failed_cmd,
#                                 succeeded_cmd=succeeded_cmd)
#
#     return render_template('hadoop.html',form=form)


@app.route('/Feedback', methods=['GET', 'POST'])
@login_required
def Feedback():
    import os
    import time
    from hashlib import md5
    from app.utils.operations import local
    from app.forms import EditorForm

    form = EditorForm()
    if form.validate_on_submit():
        param_do = form.do_action.data
        file_path = form.file_path.data

        if param_do == 'read':
            file_access = os.access(file_path, os.W_OK)
            if not file_access:
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_access=file_access)

            with open(file_path, 'rb') as f:
                file_data = f.read()
            f.closed
            form.file_data.data=file_data
            return render_template('editor.html',
                                    form=form,
                                    file_path=file_path,
                                    file_access=file_access)

        if param_do == 'save':
            file_access = os.access(file_path, os.W_OK)
            if not file_access:
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_access=file_access)

            file_md5sum = md5(open(file_path, 'rb').read()).hexdigest()
            form_md5sum = md5(form.file_data.data.replace('\r\n','\n')).hexdigest()
            if file_md5sum == form_md5sum:
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_access=file_access,
                                        file_no_change=True)


            postfix = time.strftime("%Y%m%d%H%M%S")
            file_backup = file_path + "." + postfix

            backup_out = local("cp -p {0} {1}".format(file_path,file_backup))
            succeeded_backup = backup_out.succeeded
            failed_backup = backup_out.failed

            file = open(file_path, 'wb')
            file.write(form.file_data.data.replace('\r\n','\n'))
            file.close()
    
        return render_template('editor.html',
                                form=form,
                                file_path=file_path,
                                file_access=file_access,
                                postfix=postfix,
                                backup_out=backup_out,
                                failed_backup=failed_backup,
                                succeeded_backup=succeeded_backup)

    return render_template('editor.html',form=form)



@app.route('/upload/', methods=['POST', 'GET'])
@login_required
def upload():
    # 实例化表单
    from app.forms import UploadForm
    form = UploadForm()
    if form.validate_on_submit():
        # 获取上传文件的文件名;
        filename = form.file.data.filename

        print(filename)
        # 将上传的文件保存到服务器;
        with open("E:\devopsdemo-master\devopsdemo-master\mat\data.mat", 'wb+') as f:
             form.file.data.save(f)
             flash("上传成功，快去看看吧", 'ok')
        return redirect('/upload/')
    return render_template('upload.html', form=form)


@app.route('/image')
def image():
    return render_template('image.html')




@app.route('/readmat')
def readmat():
     time_start=time.time()
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

     s = np.matrix(S).getH()
     LBP = s * F
     Tik = (s * S + 0.01 * I).I*(s * F)
     Ans_LBP = np.empty([318, 1])

     for i in range(318):
         Ans_LBP[i, 0] = (LBP[i, 0] - min(LBP)) / (max(LBP) - min(LBP))
     X = np.matrix(m['Coord'])[:, 0]
     Y = np.matrix(m['Coord'])[:, 1]
     Flat1 = np.concatenate((Topo, Ans_LBP.T), axis=0).T
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
     with open('data.json', 'a')as f:
         json.dump(Num2,f)

     # print(Num2)

     print('mytable')
     time_end=time.time()
     print('time cost',time_end-time_start,'s')
     Num2 = json.dumps(Num2)
     # print(Num2)
     return(Num2)

     # return render_template('image.html', result_json = json.dumps(Num2))



@app.route('/readmattik')
def readmattik():
     time_start=time.time()
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

     s = np.matrix(S).getH()
     LBP = s * F
     Tik = (s * S + 0.01 * I).I*(s * F)
     Ans_LBP = np.empty([318, 1])

     for i in range(318):
         Ans_LBP[i, 0] = (Tik[i, 0] - min(Tik)) / (max(Tik) - min(Tik))
     X = np.matrix(m['Coord'])[:, 0]
     Y = np.matrix(m['Coord'])[:, 1]
     Flat1 = np.concatenate((Topo, Ans_LBP.T), axis=0).T
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
     with open('data.json', 'a')as f:
         json.dump(Num2,f)

     # print(Num2)

     print('mytable')
     time_end=time.time()
     print('time cost',time_end-time_start,'s')
     Num2 = json.dumps(Num2)
     # print(Num2)
     return(Num2)
     # return render_template('image.html', result_json = json.dumps(Num2))



@app.route('/readmatLW')
def readmatLW():
     time_start=time.time()
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

     s = np.matrix(S).getH()
     # LBP = s * F
     # Tik = (s * S + 0.01 * I).I*(s * F)
     Ans_LW = np.empty([318, 1])
     LW=np.dot(s,F)
     alfa=0.01
     for i in range(2000):
         LW=LW-alfa*np.dot(s,(np.dot(S,LW)-F))




     for i in range(318):
         Ans_LW[i, 0] = (LW[i, 0] - min(LW)) / (max(LW) - min(LW))
     X = np.matrix(m['Coord'])[:, 0]
     Y = np.matrix(m['Coord'])[:, 1]
     Flat1 = np.concatenate((Topo, Ans_LW.T), axis=0).T
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
     with open('data.json', 'a')as f:
         json.dump(Num2,f)

     # print(Num2)

     print('mytable')
     time_end=time.time()
     print('time cost',time_end-time_start,'s')
     Num2 = json.dumps(Num2)
     # print(Num2)
     return(Num2)
     # return render_template('image.html', result_json = json.dumps(Num2))




@app.route('/readmatlp')
def readmatlp():
    time_start=time.time()
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
    for i in range(1):
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
        Ans_LP[i]=pow(Ans_LP[i],2)
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
    with open('data.json', 'a')as f:
        json.dump(Num2,f)

         # print(Num2)

    print('mytable')
    time_end=time.time()
    print('time cost',time_end-time_start,'s')
    Num2 = json.dumps(Num2)
         # print(Num2)
    return(Num2)
         # return render_template('image.html', result_json = json.dumps(Num2))



@app.route('/readmatSB')
def readmatSB():
    time_start=time.time()
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
    for i in range(20):
        up=u
        u=np.dot(C,Ft+lamda*(d-b))
        tmp=u+b

        b=tmp



    for i in range(318):
        Ans_SB[i] = (up[i] - min(up)) / (max(up) - min(up))
        Ans_SB[i]=pow(Ans_SB[i],1.5)
    X = Coord[:, 0]
    Y = Coord[:, 1]
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
    with open('data.json', 'a')as f:
        json.dump(Num2,f)

         # print(Num2)

    print('mytable')
    time_end=time.time()
    print('time cost',time_end-time_start,'s')
    Num2 = json.dumps(Num2)
         # print(Num2)
    return(Num2)
         # return render_template('image.html', result_json = json.dumps(Num2))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    from app.forms import SignupForm
   
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            form.email.errors.append("The Email address is already taken.")
            return render_template('signup.html', form=form)

        newuser = User(form.firstname.data,form.lastname.data,form.email.data,form.password.data)
        db.session.add(newuser)
        db.session.commit()

        session['email'] = newuser.email
        return redirect(url_for('login'))
   
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    from app.forms import LoginForm

    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            session['email'] = form.email.data
            login_user(user,remember=session['remember_me'])
            return redirect(url_for('index'))
        else:
            return render_template('login.html',form=form,failed_auth=True)
                   
    return render_template('login.html',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))





