import secrets
from werkzeug.urls import url_parse
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, logout_user, login_user
from flask_user import roles_required
from trial.models import Post, User, Contract, Role
from trial.admin.forms import RegistrationForm, BlogPostForm, ContractDetailsForm
from trial.users.forms import LoginForm
from trial.admin.utils import save_photo
import re
import requests
from trial import db, bcrypt


admin = Blueprint('admin', __name__)



@admin.route('/dashboard')
@roles_required('Admin')
def dashboard():
    return render_template('admin/dashboard.html')


@admin.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #Hash Password
        hashed_pswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.email.data == "admin@highways.com":
            #Create Instance of the user
            user = User(username=form.username.data, email=form.email.data, password=hashed_pswd)
            #Add user to the database
            user.roles.append(Role(name='Admin'))
            db.session.add(user)
            db.session.commit()
            flash('Admin has been created successfully. You can now log in', 'success')
            return redirect(url_for('admin.register'))
        else:
            #Create Instance of the user
            user = User(username=form.username.data, email=form.email.data, password=hashed_pswd)
            #Add user to the database
            db.session.add(user)
            db.session.commit()
            flash('New user has been added successfully. You can now log in', 'success')
            return redirect(url_for('admin.register'))
    return render_template('admin/register.html', title='Register', form=form)

#Create route for Blog news update
@admin.route('/blog_news/new', methods=['GET', 'POST'])
def create_blog():
    form = BlogPostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.blog_content.data
        picture = save_photo(form.picture.data) 

        #Upload post into the database
        post = Post(title=title, body=content, image=picture, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been submitted', 'success')
        return redirect(url_for('blogs.blog'))
    return render_template('admin/create_news.html', title='New Post', form=form)

#Add new Contract details to the database
@admin.route('/add_contract', methods=['GET', 'POST'])
def add_contract():

    form = ContractDetailsForm()

    if form.validate_on_submit():
    
        match = re.search(r"youtube\.com/.*v=([^&]*)", form.video_link.data) 
        video_id_youtube = match.group(1)

        image_url = "https://img.youtube.com/vi/" + \
            video_id_youtube + "/mqdefault.jpg" 
        img_data = requests.get(image_url).content
        random_hex = secrets.token_hex(16)
        thumb_filename = random_hex + ".jpg"

        with open(current_app.root_path + '/static/thumbs/' + thumb_filename, 'wb') as handler:
            handler.write(img_data)

        uploaded_details = Contract(name_of_contract=form.name_of_contract.data, length=form.length.data, 
                                          lot=form.lot.data, contract_sum=form.contract_sum.data, 
                                          contractor=form.contractor.data, date_commenced=form.date_commenced.data, 
                                          date_completed=form.date_completed.data, video_title=form.video_title.data, 
                                          video_link=form.video_link.data, video_description=form.video_description.data,
                                          video_thumb=thumb_filename, user_id=current_user.id)

        # saving to database
        db.session.add(uploaded_details)
        db.session.commit()
        flash('Data added successfully', 'success')
        return redirect(url_for('admin.add_contract'))

    return render_template('admin/contract_details-form.html', form=form)


#Route for logout
@admin.route('/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('users.login'))



@admin.route('/video/edit/<int:contract_id>', methods=['GET', 'POST'])
def edit_video(contract_id):

    contract = Contract.query.get_or_404(contract_id)

    #if not contract.user_id == current_user.id:
     #   flash('You are not allowed to view this page!', 'danger')
      #  return redirect(url_for('admin.dashboard'))

    form = ContractDetailsForm()

    if form.validate_on_submit():
        match = re.search(r"youtube\.com/.*v=([^&]*)", form.video_link.data)
        video_id_youtube = match.group(1)

        image_url = "https://img.youtube.com/vi/" + \
            video_id_youtube + "/mqdefault.jpg"
        img_data = requests.get(image_url).content
        random_hex = secrets.token_hex(16)
        thumb_filename = random_hex + ".jpg"

        with open(current_app.root_path + '/static/thumbs/' + thumb_filename, 'wb') as handler:
            handler.write(img_data)

        contract.name_of_contract = form.name_of_contract.data
        contract.length = form.length.data
        contract.lot = form.lot.data
        contract.contract_sum = form.contract_sum.data
        contract.contractor = form.contractor.data
        contract.date_commenced = form.date_commenced.data
        contract.date_completed = form.date_completed.data
        contract.video_title = form.video_title.data
        contract.video_link = form.video_link.data
        contract.video_description = form.video_description.data
        contract.video_thumb = thumb_filename

        # saving to database
        db.session.commit()
        flash('Video updated successfully', 'success')
        return redirect(url_for('admin.contract_view_dash'))
    
    elif request.method == 'GET':
        form.name_of_contract.data = contract.name_of_contract
        form.length.data = contract.length
        form.lot.data = contract.lot
        form.contract_sum.data = contract.contract_sum
        form.contractor.data = contract.contractor
        form.date_commenced.data = contract.date_commenced
        form.date_completed.data = contract.date_completed
        form.video_title.data = contract.video_title
        form.video_link.data = contract.video_link
        form.video_description.data = contract.video_description

    return render_template('admin/contract_details-edit.html', title=contract.video_title, form=form, contract=contract, contract_id=contract_id)


@admin.route("/contract_details/dashboard", methods=['GET', 'POST'])
def contract_view_dash():
    contract = Contract.query.order_by(Contract.id.desc()).all()

    return render_template('admin/contract-details-dash.html', title='Dashboard', contract=contract)

