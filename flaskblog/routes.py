import bcrypt
import secrets,os
from PIL import Image
from flask import url_for,redirect,render_template,request,flash,abort
from flask_wtf import form
from flaskblog.forms import RegisterForm,LoginForm,PostForm,AccountForm,ChangePasswordForm,PasswordResetToken,ResetPasswordForm
from flaskblog import bycrpt,db,app,mail
from flaskblog.models import User,Post
from flask_login import current_user,login_user,logout_user,login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page',default=1,type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(per_page = 2 , page =page)
    return render_template('home.html',posts = posts)


@login_required
@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return url_for('home')
    form = RegisterForm() 
    if form.validate_on_submit():
        hashed_pass = bycrpt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created , Login Now')
        return redirect(url_for('login'))
    return render_template('register.html',title = 'Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return url_for('home')
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email = form.email.data).first()
      password = bycrpt.check_password_hash(user.password,form.password.data)
      if user and password:
        flash('You are logged In')
        login_user(user)
        return redirect(url_for('home'))
      else:
        flash('Wrong Credentials')
        return redirect(url_for('login'))


    return render_template('login.html',title = 'Login',form = form)

@app.route("/logout",methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/newpost",methods = ['GET','POST'])
@login_required
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data , content = form.content.data , author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post has been created')
        return redirect(url_for('home'))
    return render_template('newpost.html',title = "newpost", form = form)

@app.route("/post/<int:user_id>",methods = ['GET','POST'])
@login_required
def post (user_id):
    post = Post.query.get(user_id)
    if current_user != post.author:
        abort(403)
    return render_template('post.html',title= 'Post', post =post)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route("/account",methods = ['GET','POST'])
@login_required
def account():
    form = AccountForm()

    if form.validate_on_submit(): 
        if form.picture.data:
           pic_file = save_picture(form.picture.data)
           current_user.image = pic_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been Updated')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for('static',filename = 'images/'+ current_user.image)
    return render_template('account.html',title = 'Account', form = form,image = image)

@app.route("/change_password",methods = ['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
      current_user_password = bycrpt.check_password_hash(current_user.password,form.current_password.data)  
      if current_user_password:
        current_user.password = bycrpt.generate_password_hash(form.new_password.data).decode('utf-8')
        db.session.commit()
        flash('Your Password has been changed')
        logout_user()
        return redirect(url_for('login'))
      else:
        flash('Something Went Wrong , enter correct details')
        return redirect(url_for('change_password'))

    return render_template('change_password.html',form = form)

@app.route("/post/update/<int:post_id>",methods = ['GET','POST'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.author:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('your post has been Updated')
        return redirect(url_for('home'))
    
    if request.method == 'GET':
        form.title.data  = post.title
        form.content.data = post.content

    return render_template('update.html',title = "update post",form =form)

@app.route("/post/delete/<int:post_id>",methods = ['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.author:
        abort(403)

    flash('your post has been deleted','red')
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/posts/<string:user_name>")
def user_posts(user_name):
   user = User.query.filter_by(username = user_name).first_or_404()
   page = request.args.get('page',default=1,type=int)
   posts = Post.query.filter_by(author=user).order_by(Post.date.desc()).paginate(page = page ,per_page = 3)
   return render_template('user_posts.html',posts = posts, username = user_name)


def send_reset_email(user):
    token = user.get_token()
    msg = Message('Reset Token',sender= 'noreply@demo.com',recipients=[user.email])
    msg.body = f'''To Reset the Password Click this link  {url_for('reset_token',token = token,_external = True )}'''
    mail.send(msg)


@app.route("/reset_token",methods = ['POST','GET'])
def reset_password_token():
    form = PasswordResetToken()

    if form.validate_on_submit():
      user = User.query.filter_by(email = form.email.data).first()
      send_reset_email(user)
      flash('Token has been sent to your email')
      return redirect(url_for('login'))

    return render_template('reset_password_token.html',form = form)


@app.route("/reset_password/<string:token>",methods = ['POST','GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.check_token(token)

    if user is None:
        flash('Something went Wrong or token expired , Try again')
        return redirect(url_for('reset_password_token'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
       user.password = bycrpt.generate_password_hash(form.password.data).decode('utf-8')
       db.session.commit()
       flash('Your password has been changed, login now')
       return redirect(url_for('login'))

    return render_template('reset_password.html',form = form)

@app.errorhandler(401)
def error_401(error):
    return render_template('401.html'),401

@app.errorhandler(403)
def error_403(error):
    return render_template('403.html'),403

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'),404

@app.errorhandler(500)
def error_500(error):
    return render_template('500.html'),500




