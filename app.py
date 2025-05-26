from flask import Flask, render_template, request, redirect, session
from time import time

app = Flask(__name__)
app.secret_key = 'blockchain_secure'

# Config
VALID_KEY = 'RightToVote'
admins = {'Adeeba H':'HabeedA','Gagan':'nagaG','Sarumati':'itamuraS'}
valid_voters = {f"1HK22CS{str(i).zfill(3)}": {'password':None, 'vote':None} for i in range(1,101)}
candidates = ["💪Momin","💬K Ayesha","🧩Akshay BM"]
blockchain = []

def new_block(voter_id):
    block = {'index': len(blockchain), 'timestamp': time(), 'transactions':[{'voter_id': voter_id}]}
    blockchain.append(block)

@app.route('/', methods=['GET','POST'])
def login():
    error = None
    if request.method=='POST':
        if request.form['public_key']==VALID_KEY:
            return redirect('/home')
        error='Invalid public key'
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method=='POST':
        aid = request.form['admin_id']
        apass = request.form['admin_pass']
        if aid in admins and admins[aid]==apass:
            session['admin']=aid
            return redirect('/admin_page')
        error='Unauthorized'
    return render_template('admin_login.html', error=error)

@app.route('/admin_page')
def admin_page():
    if 'admin' not in session:
        return redirect('/admin_login')
    return render_template('admin.html', blockchain=blockchain)

@app.route('/voter_login', methods=['GET','POST'])
def voter_login():
    error = None
    if request.method=='POST':
        vid = request.form['voter_id'].strip().upper()
        pwd = request.form['password']
        cpwd = request.form['confirm_password']
        if vid not in valid_voters:
            error='Invalid Voter ID'
        else:
            stored = valid_voters[vid]['password']
            if stored is None:
                if pwd!=cpwd:
                    error='Passwords do not match'
                else:
                    valid_voters[vid]['password']=pwd
                    session['voter']=vid
                    return redirect('/vote')
            else:
                if pwd==cpwd==stored:
                    session['voter']=vid
                    return redirect('/vote')
                error='Authentication failed'
    return render_template('voter_login.html', error=error)

@app.route('/vote', methods=['GET','POST'])
def vote():
    vid = session.get('voter')
    if not vid:
        return redirect('/voter_login')
    if request.method=='POST':
        if valid_voters[vid]['vote'] is None:
            candidate = request.form['candidate']
            valid_voters[vid]['vote'] = candidate
            new_block(vid)
            message = 'Vote cast successfully!'
        else:
            message = 'You have already voted.'
        return render_template('vote.html', candidates=candidates, message=message)
    return render_template('vote.html', candidates=candidates)

@app.route('/check_login', methods=['GET','POST'])
def check_login():
    error = None
    if request.method=='POST':
        vid = request.form['voter_id'].strip().upper()
        pwd = request.form['password']
        if vid in valid_voters and valid_voters[vid]['password']==pwd:
            session['check']=vid
            return redirect('/check')
        error='Authentication failed'
    return render_template('check_login.html', error=error)

@app.route('/check')
def check():
    vid = session.get('check')
    if not vid:
        return redirect('/check_login')
    return render_template('check.html', vote=valid_voters[vid]['vote'])

if __name__=='__main__':
    app.run(debug=True)