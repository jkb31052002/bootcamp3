from flask import Flask, render_template, request, url_for, abort, redirect
from flask_login import login_user, logout_user, current_user, login_required, LoginManager

from flask import current_app as app

from datetime import datetime, date

from .models import *

#HOME PAGE
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

#ADMIN LOGIN
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')

        this_admin = Admin.query.filter_by(username=u_name).first()

        if not this_admin:
            return render_template('admin_login.html', error="This username does not exist.")
        
        if this_admin.password != pwd:
            return render_template('admin_login.html', error="Incorrect password.")
        
        login_user(this_admin)
        campaigns = Campaign.query.filter_by(flagged=0).all()
        influencers = Influencer.query.filter_by(flagged=0).all()
        flagged_influencers = Influencer.query.filter_by(flagged=1).all()

        return render_template('admin_dashboard.html', current_user=u_name, u_name=u_name, campaigns=campaigns, influencers=influencers, flagged_influencers=flagged_influencers)
    return render_template('admin_login.html')

#ADMIN DASHBOARD
@app.route('/admindashboard')
@login_required
def admindashboard():
    u_name = current_user.username
    campaigns = Campaign.query.filter_by(flagged=0).all()
    influencers = Influencer.query.filter_by(flagged=0).all()
    flagged_influencers = Influencer.query.filter_by(flagged=1).all()

    return render_template('admin_dashboard.html', current_user=u_name, u_name=u_name, campaigns=campaigns, influencers=influencers, flagged_influencers=flagged_influencers)


#ADMIN LOGOUT
@app.route('/adminlogout')
@login_required
def adminlogout():
    logout_user()
    return render_template('admin_login.html', message="You have been logged out successfully.")  


#INFLUENCER REGISTER
@app.route('/influencerregister', methods=['GET', 'POST'])
def influencerregister():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')
        ctg = request.form.get('ctg')
        reach = request.form.get('reach')
        niche = request.form.get('niche')
        platform = request.form.get('platform')


        if not (u_name and pwd and ctg and reach and niche and platform):
            return render_template('influencer_register.html', error="Please fill in all fields.")
        

        this_influencer = Influencer.query.filter_by(username=u_name).first()

        if this_influencer:
            return render_template('influencer_register.html', error="This username already exists. Please choose a different username.")
        
        else:
            new_user = User(username=u_name, user_role=2)
            db.session.add(new_user)
            db.session.commit()

            new_influencer = Influencer(
                name=u_name,
                category=ctg,
                reach=reach,
                niche=niche,
                platform=platform,
                username=u_name,
                password=pwd,
                influencer_id=new_user.id
            )
            db.session.add(new_influencer)
            db.session.commit()

            return redirect('/influencerlogin')
    return render_template('influencer_register.html')


#INFLUENCER_LOGIN
@app.route('/influencerlogin', methods=['GET', 'POST'])
def influencerlogin():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')

        this_influencer = User.query.filter_by(username=u_name).first()

        influencer = Influencer.query.filter_by(username=u_name).first()

        if not this_influencer:
            return render_template('influencer_login.html', error="This username does not exist.")

        if not influencer:
            return render_template('influencer_login.html', error="Influencer not found.")

        if influencer.password != pwd:
            return render_template('influencer_login.html', error="Incorrect password.")
        
        if influencer.flagged == 1:
            return render_template('influencer_login.html', error="Your account has been flagged. Please contact support.")
        
        if this_influencer.user_role == 2:
            login_user(this_influencer)

            user_id = current_user.id


            return render_template('influencer_dashboard.html', current_user=u_name, u_name=u_name, user_id=user_id)
    return render_template('influencer_login.html')



