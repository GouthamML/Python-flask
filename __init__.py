import os
from flask import Flask, render_template, request, redirect, url_for, session, escape, send_from_directory
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField
from wtforms.validators import DataRequired
from werkzeug import secure_filename

app=Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'

app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'jinja'
app.config['UPLOAD_FOLDER'] = '/home/goutham/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx','ppt','c'])
mysql=MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

class NameForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    email = StringField('Email')
    password = PasswordField('Passowrd')
    submit = SubmitField('Submit')
    job = RadioField('Label', choices=[('student','I\'m a Student'),('teacher','I\'m a Lecturer')])
    f_name = StringField('File name')
    #branch = StringField('branch')
    public = RadioField('Label', choices=[(1,'Make it public'),(0,'Keep it private')])
    
    


@app.route('/', methods=['GET','POST'])
def index():
    form=NameForm()
    cur=mysql.connection.cursor()
    if 'username' in session:
        username_session = session['username']
        uname = session['username'].capitalize()
        
        cur.execute("SELECT job FROM login where username = '" + username_session + "'")
        for job1 in cur.fetchall():
                if job1[0]=="student":
                    cur.execute("SELECT sf_check FROM s_profile WHERE s_username = '" + username_session + "'")
                    check_var = cur.fetchone()
                    if check_var==None:
                        return render_template('stud_profile.html')
                    return render_template('index.html',session_name=uname)
                cur.execute("SELECT tf_check FROM t_profile WHERE t_username = '" + username_session + "'")
                check_var = cur.fetchone()
                if check_var==None:
                    return render_template('teach_profile.html')
                return render_template('index_teach.html', session_name=username_session)
     
    return redirect(url_for('login'))


@app.route('/home/myteachers')
def myteachers():
    cur=mysql.connection.cursor()
    username1 = session['username']
    username = str(username1)
    sql1 = "SELECT s_dept FROM s_profile where s_username='" + username1 + "'"
    cur.execute(sql1)
    s_dept1 = cur.fetchone()
    for b in s_dept1:
        s_dept = str(b)
    print s_dept
    sql2 = "SELECT s_clg FROM s_profile where s_username='" + username1 + "'"
    cur.execute(sql2)
    s_clg1 = cur.fetchone()
    for c in s_clg1:
        s_clg = str(c)
    print s_clg
    sql = "SELECT t_name,t_username FROM t_profile where t_clg = '" + s_clg + "' and t_dept = '"+ s_dept + "' "
    cur.execute(sql)
    teachers = []
    hu = []
    hum = []
    teachlist = []
    teachers = cur.fetchall()
    test = dict(teachers)
    print test, type(test), 
    print test['Smitha ML']
    # for a in teachers:
    
  

    print teachers, type(teachers)
    return render_template('my_teachers.html',hu = hu, hum=hum, test = test)

@app.route('/home/<teachname>/profile')
def tprofile(teachname):
    sqlname = "SELECT t_name FROM t_profile where t_username='"+ teachname +"'"
    sqlpic = "SELECT image FROM t_profile WHERE t_username='"+ teachname +"'"
    sqlcollege ="SELECT t_clg FROM t_profile WHERE t_username='"+ teachname +"'"
    cur=mysql.connection.cursor()
    cur.execute(sqlname)
    name=[]
    name = cur.fetchall()
    for a in name:
        name1 = str(a[0])
    print name1
    cur.execute(sqlpic)
    pic = cur.fetchall()
    cur.execute(sqlcollege)
    clg = cur.fetchall()
    print name1, pic, clg, type(pic), pic[0]
    return render_template('tprofile.html',name=name,pic=pic,clg=clg)

@app.route('/t_myprofile')
def t_myprofile():
    cur=mysql.connection.cursor()
    username = session['username']
    
    sqlname = "SELECT t_name, t_dept FROM t_profile where t_username='"+ username +"'"
    cur.execute(sqlname)
    name1 = cur.fetchone()
    name = name1[0]
    dept = name1[1]
    print dept
    return render_template('t_myprofile.html',username=username, name = name, dept = dept)




    




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form=NameForm()
    return render_template('signup.html', form=form)

@app.route('/add_db', methods=['GET', 'POST'])
def add_db():
    form = NameForm()
    
    username1 = request.form['username']
    email1= request.form['email']
    password1=request.form['password']
    job1 = str(form.job.data) 
    cur=mysql.connection.cursor()
    
    cur.execute('''INSERT INTO login (username, email, password, job) VALUES (%s, %s, %s, %s)''' , (username1, email1, password1,job1))
    mysql.connection.commit()
    #return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/sformfill', methods=['GET', 'POST'])
def sformfill():
    if request.method == 'POST':
        name = request.form['name']
        dept = request.form['branch']
        sem =  request.form['sem']
        clg = request.form['clg']
        username = session['username']
        cur=mysql.connection.cursor()
    
        cur.execute("INSERT INTO s_profile(s_name, s_dept, s_sem, s_username, sf_check, s_clg) VALUES(%s, %s, %s, %s, %s, %s)",(name, dept, sem, username, 1, clg)) 
        mysql.connection.commit()

        return redirect(url_for('index'))

@app.route('/tformfill', methods=['GET','POST'])
def tformfill():
     if request.method == 'POST':
        name = request.form['name']
        dept = request.form['branch']
        
        clg = request.form['clg']
        username = session['username']
        file = request.files['file']
        filename = secure_filename(file.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        

        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO t_profile(t_name, t_username, t_dept, t_clg, tf_check, image) VALUES(%s, %s, %s, %s, %s, %s)",(name, username, dept,clg, 1, image)) 
        mysql.connection.commit()

        return redirect(url_for('index'))
        
    
    

    




@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form=NameForm()
    cur=mysql.connection.cursor()
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login4_1.html', form=form)
    
@app.route('/check', methods=["POST"])
def check():
    form=NameForm()
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        username_form  = request.form['username']
        cur.execute("SELECT username AS uname FROM login WHERE username = '" + username_form +"'")
        fetched_name = cur.fetchone()
        if fetched_name == None:
            return 'Invalid username'
            
            
        password_form  = request.form['password']
        cur.execute("SELECT password AS pword FROM login WHERE username = '"+ username_form +"'")
        print username_form, password_form, fetched_name
            
        for row in cur.fetchall():
            if password_form == row[0]:
                print cur.fetchall()
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return 'Invalid password'
        
    #return render_template('login4.html', form=form)
    
@app.route('/upload')
def upload():
    username_session = session['username']
    cur=mysql.connection.cursor()
    cur.execute("SELECT job FROM login where username = '" + username_session + "'")
    for job1 in cur.fetchall():
            if job1[0]=="student":
                return redirect(url_for('index'))
    form=NameForm()
    return render_template('upload.html', form=form)
    

@app.route('/uploading', methods=['POST'])
def uploading():
    form=NameForm()
    cur=mysql.connection.cursor()
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename): 
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        
        
        
        f_name1 = str(form.f_name.data)
        branch1 = request.form['branch']
        
        
        sem1 = request.form['sem']
        public1 = form.public.data
        username = session['username']
        texts = request.form['textarea']
        cur=mysql.connection.cursor()
        #cur.execute("SELECT id as u_id FROM login WHERE username = '" + username + "'")
        
        #u_id1=cur.fetchall()
        
        
        
        cur.execute('''INSERT INTO files(f_name, actualname, f_username, branch, sem, public, description) VALUES (%s, %s, %s, %s, %s, %s, %s)''',[f_name1, filename, username, branch1, sem1, public1, texts])
        mysql.connection.commit()
        return redirect(url_for('index'))


                        
                    
    return 'Couldn\'t complete upload'


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/search_results', methods=['GET','POST'])
def search():
    cur=mysql.connection.cursor()
    search = request.form['search']
    cur.execute("SELECT t_name from t_profile where t_username ='" + search + "'")
    username = cur.fetchall()
    
    return render_template('results.html',username = username)

@app.route('/teacher/<username>', methods=['GET','POST'])
def tprof(username):
    name = username
    cur=mysql.connection.cursor()
    cur.execute("SELECT t_name from t_profile where t_username ='" + name + "'")
    main_name = cur.fetchall()
    return render_template('teach_profile.html', main_name=main_name)



@app.route('/teacher/<username>/files')
def view_files(username):
    name = username
    sql = "SELECT fid from files WHERE f_username ='" + name + "'"
    cur=mysql.connection.cursor()
    ids = []
    cur.execute(sql)
    ids = cur.fetchall()
    #print ids, type(ids[0][0]), int(ids[0][0])
    vf = []
    m = 0
    df = []
    downlink = {}
    for a in ids:
        hu = str(a[0])
        print hu
        sql1 = "SELECT f_name from files where fid ='" + hu + "'"
        cur.execute(sql1)
        files1 = cur.fetchone()
        for b in files1:
            files2 = str(b)
        
        sql2 = "SELECT actualname FROM files where fid = '" + hu +"'"
        cur.execute(sql2)
        fname1 = cur.fetchone()
        for c in fname1:
            fname2 = str(c)

        
        downlink[files2] = fname2
        print downlink
    




    # sql1 = "select f_name from files where fid = %s"  
    # cur.execute(sql1,ids)
    #vf.insert(cur.fetchall())
    return render_template('view_files.html',vf=vf,m=m,df=df, downlink=downlink)
    
    #return 'No files uploaded'
        
        
    
    
    
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))





   
   
if __name__=='__main__':
    app.run(debug=1)
    

