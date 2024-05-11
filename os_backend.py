from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import numpy as np
import copy

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST','GET'])
def upload_file():
    alloc = []
    maxi = []
    avail = []
    req = [] 
    by = None
    if 'file' not in request.files:
        return jsonify({'response':'No file part','seq':0})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'response':'No selected file','seq':0})

    if file:
        filename = file.filename
        path=str(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(path, 'r') as file:
            lines = file.readlines()
            part=1
            for line in lines:
                if '-' in line:
                    part+=1
                    continue
                if part==1:
                    try:
                        array = [int(x) for x in line.split(',')]
                    except:
                        return jsonify({'response':'Not a valid file format','seq':0})
                    alloc.append(array)
                elif part==2:
                    try:
                        array = [int(x) for x in line.split(',')]
                    except:
                        return jsonify({'response':'Not a valid file format','seq':0})
                    maxi.append(array)
                elif part==3:
                    try:
                        avail = [int(x) for x in line.split(',')]
                    except:
                        return jsonify({'response':'Not a valid file format','seq':0})
                elif part==4:
                    try:
                        by=int(line)
                    except:
                        return jsonify({'response':'Not a valid file format','seq':0})
                else:
                    try:
                        array = [int(x) for x in line.split(',')]
                    except:
                        return jsonify({'response':'Not a valid file format','seq':0})
                    req=[int(x) for x in line.split(',')]
    proc=len(alloc)
    res=len(avail)
    need=[]
    for i in range(proc):
        n=[]
        for j in range(res):
            if alloc[i][j]<0 or maxi[i][j]<0:
                return jsonify({'response':'Negative numbers not allowed','seq':0})
            if alloc[i][j]>maxi[i][j]:
                return jsonify({'response':'Allocation exceeds maximum value for resource '+str(j)+' in process '+str(i),'seq':0})
            my_need=maxi[i][j]-alloc[i][j]
            n.append(my_need)
        need.append(n)
    if by!=None:
        for j in range(res):
            if req[j]==None:
                req[j]=0
            if req[j]>need[by][j]:
                return jsonify({'response':'Request cannot be granted','seq':0})
        for i in range(res):
            if req[i]>avail[i]:
                return jsonify({'response':'Request cannot be granted','seq':0})
        for j in range(res):
            avail[j]-=req[j]
            alloc[by][j]+=req[j]
            need[by][j]-=req[j]
    comp=[0]*proc
    curr=0
    seq=[]
    exp=''
    work=copy.deepcopy(avail)
    while 0 in comp:
        c=0
        for i in range(res):
            if need[curr][i]>work[i]:
                curr_exp='Process '+str(curr)+': Need: '+str(need[curr])+' > Work'+str(work)+" Skipped"
                exp=exp+curr_exp+'\n'
                c+=1
                if c>=proc:
                    return jsonify({'response':'No Safe Seqeunce','seq':0})
                if curr==proc-1:
                    curr=0
                else:
                    curr+=1
                break
        else:
            if comp[curr]==0:
                curr_exp='Process '+str(curr)+': Need: '+str(need[curr])+' < Work'+str(work)+' and Completed=False,      Work=Work + Allocation['+str(curr)+'] = '
                c=0
                seq.append(str(curr))
                comp[curr]=1
                for i in range(res):
                    work[i]+=alloc[curr][i]
                curr_exp=curr_exp+str(work)
                exp=exp+curr_exp+'\n'
            if curr==proc-1:
                    curr=0
            else:
                    curr+=1
                
    print(seq)
    ans=''.join(seq)
    return jsonify({'response':ans,'seq':1,'need':need, 'exp': exp})

    
@app.route('/manual', methods=['POST','GET'])
def manual():
    alloc=request.get_json()['A']
    maxi=request.get_json()['M']
    avail=request.get_json()['AV']
    by=request.get_json()['by']
    proc=len(alloc)
    res=len(avail)
    need=[]
    for i in range(proc):
        n=[]
        for j in range(res):
            if alloc[i][j]==None or maxi[i][j]==None:
                return jsonify({'response':'Please fill in all fields','seq':0})
            if alloc[i][j]<0 or maxi[i][j]<0:
                return jsonify({'response':'Negative numbers not allowed','seq':0})
            if alloc[i][j]>maxi[i][j]:
                return jsonify({'response':'Allocation exceeds maximum value for resource '+str(j)+' in process '+str(i),'seq':0})
            my_need=maxi[i][j]-alloc[i][j]
            n.append(my_need)
        need.append(n)
    if by!=0:
        req=request.get_json()['R']
        for j in range(res):
            if req[j]==None:
                req[j]=0
            if req[j]>need[by-1][j]:
                return jsonify({'response':'Request cannot be granted','seq':0})
        for i in range(res):
            if req[i]>avail[i]:
                return jsonify({'response':'Request cannot be granted','seq':0})
        for j in range(res):
            avail[j]-=req[j]
            alloc[by-1][j]=req[j]+alloc[by-1][j]
            need[by-1][j]-=req[j]
    comp=[0]*proc
    curr=0
    seq=[]
    exp=''
    work=copy.deepcopy(avail)
    while 0 in comp:
        c=0
        for i in range(res):
            if need[curr][i]>work[i]:
                curr_exp='Process '+str(curr)+': Need: '+str(need[curr])+' > Work'+str(work)+" Skipped"
                exp=exp+curr_exp+'\n'
                c+=1
                if c>=proc:
                    return jsonify({'response':'No Safe Sequence','seq':0})
                if curr==proc-1:
                    curr=0
                else:
                    curr+=1
                break
        else:
            if comp[curr]==0:
                curr_exp='Process '+str(curr)+': Need: '+str(need[curr])+' < Work'+str(work)+' and Completed=False,      Work=Work + Allocation['+str(curr)+'] = '
                c=0
                seq.append(str(curr))
                comp[curr]=1
                for i in range(res):
                    work[i]+=alloc[curr][i]
                curr_exp=curr_exp+str(work)
                exp=exp+curr_exp+'\n'
            if curr==proc-1:
                    curr=0
            else:
                    curr+=1
                
    ans=''.join(seq)
    return jsonify({'response':ans,'seq':1,'need':need,'exp':exp})

if __name__ == '__main__':
    app.run(debug=True)
