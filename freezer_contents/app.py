from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin, login_user,login_required,logout_user,current_user
from datetime import datetime
from sqlalchemy  import and_
from pws import hash_password, verify_password


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freezer.db'
app.config['SECRET_KEY']='thisisasecret'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)



class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True)
    user_password = db.Column(db.String(200),unique=True)
    freezers = db.relationship('Freezer', backref='owner')
    
    

class Freezer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    shelf_name = db.Column(db.String(200),nullable=True)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
    
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        
        name = request.form['nam']
        password = request.form['pw']
        if name =='administrator1':
            user = User.query.filter_by(user_name=name).first()
            s_pw = user.user_password
            if s_pw ==password:
                login_user(user)
        else:
            user =User.query.filter_by(user_name=name).first()
            s_pw = user.user_password
            if verify_password(s_pw,password):
                                
                login_user(user)
            
    
    
    return render_template(('index.html'))



@app.route('/freezer_contents',methods=['GET','POST'])
@login_required
def freezer_contents():
    
    if request.method == 'POST':
        
        content = request.form['content']
        shelf = request.form['shelf_name']
        new_record = Freezer(content= content,shelf_name = shelf,owner_id = current_user.id)
        
        try:
            db.session.add(new_record)
            db.session.commit()
            
            return redirect('/freezer_contents')
        
        except:
            return 'There was an issue adding your task'
        
    elif request.method =='GET':
        s = str(request.args.get('s'))
        c_t = request.args.get('c_t')
        num= len(current_user.freezers)
        num = int(num-1)
        
        if c_t =="":
            shelfs=[]
            if s=='top':
                i=int(0)
                for each in current_user.freezers:
                    
                    shelf_name = current_user.freezers[i].shelf_name
                    if shelf_name == 'top':
                        shelfs.append(each)
                    i=i+1
                
            elif s=='middle':
                i=int(0)
                for each in current_user.freezers:
                    
                    shelf_name = current_user.freezers[i].shelf_name
                    if shelf_name == 'middle':
                        shelfs.append(each)
                    i=i+1
            elif s=='bottom':
                i=int(0)
                for each in current_user.freezers:
                    
                    shelf_name = current_user.freezers[i].shelf_name
                    if shelf_name == 'bottom':
                        shelfs.append(each)
                    i=i+1
            else:
                shelfs = current_user.freezers
                
        else:
            shelfs=[]
            i= int(0)
            for each in current_user.freezers:
                
                    content = current_user.freezers[i].content
                    if content == c_t:
                        shelfs.append(each)
                    i=i+1
            
    return render_template('freezer_contents.html',shelfs = shelfs)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete =Freezer.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/freezer_contents')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    shelf = Freezer.query.get_or_404(id)
    if request.method == 'POST':
        shelf.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/freezer_contents')
        except:
            return 'there was an issue updating your shelf'
    else:
        return render_template('update.html', shelf=shelf)
    
    
@app.route("/admin", methods=['GET','POST'])
@login_required
def admin():
    
    if current_user.user_name == 'new_admin':
        users = User.query.all()
        return render_template(('admin.html'),users = users)
        
    
    
    return render_template(('admin.html'),users = users)

    
    
    
@app.route('/update_user/<int:id>',methods=['GET','POST'])
@login_required
def update_user(id):
    this_user = User.query.get_or_404(id)
    if request.method == 'POST':
       
        new_password =request.form['password']
        new_password = hash_password(new_password)
        this_user.user_password = new_password
        
        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return 'there was an issue updating this user'
    else:
        return render_template('update_user.html',this_user=this_user)
    
@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    user_to_delete =User.query.get_or_404(id)
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'There was a problem deleting that user'
    
    

    
@app.route("/profile", methods=['GET','POST'])
@login_required
def profile():
    users=[]
    user = current_user
    users.append(user)
        
    
    
    return render_template(('profile.html'),users = users)

@app.route('/change_password',methods=['GET','POST'])
def change_password():
    user = current_user
    if request.method == 'POST':
        new_password =request.form['password']
        new_password = hash_password(new_password)
        user.user_password = new_password
        
        try:
            db.session.commit()
            return render_template('profile.html',user=user)
        except:
            return 'there was an issue updating your password'
    else:
        return render_template('change_password.html')
    



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name =request.form['user_name']
        password = request.form['user_password']
        password = hash_password(password)
        new_record = User(user_name = name,user_password = password)
        if new_record!= None:
            try:

                db.session.add(new_record)
                db.session.commit()
                return redirect('/register')
                
                

            except:
                return 'There was a problem adding your details'
    else:
        return render_template(('register.html'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template(('index.html'))
   
if __name__ == '__main__':
    
    app.run(debug = True)