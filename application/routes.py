from flask import Flask, render_template, request, url_for, abort, redirect
from flask_login import login_user, logout_user, current_user, login_required, LoginManager

from flask import current_app as app

from datetime import datetime, date

from .models import *

#CAMPAIGN ACTIVE/NOT STATUS
def campaign_isactive(start_date,end_date,present_date):
    present_date = datetime.now().date()
    return start_date <= present_date < end_date

#PROGRESS CALCULATION 
def calculate_campaign_progress(start_date, end_date):
    # current_date = datetime.now().date()
    # total_days = (end_date - start_date).days
    # elapsed_days = (current_date - start_date).days
    # if total_days > 0:
    #     progress = (elapsed_days / total_days) * 100
    # else:
    #     progress = 0
    return 100

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


#SPONSOR REGISTER
@app.route('/sponsorregister', methods=['GET', 'POST'])
def sponsorregister():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')
        c_name = request.form.get('c_name')
        c_budget = int(request.form.get('c_budget'))
        industry = request.form.get('industry')

        if c_budget < 0:
            return render_template('sponsor_register.html', error="Company budget cannot be negative.")
        
        this_sponsor = Sponsor.query.filter_by(username=u_name).first()

        if this_sponsor:
            return render_template('sponsor_register.html', error="This username already exists. Please choose a different username.")
        
        else:
            new_user = User(username=u_name, user_role=1)
            db.session.add(new_user)
            db.session.commit()

            new_sponsor = Sponsor(
                company_name=c_name,
                company_budget=c_budget,
                username=u_name,
                password=pwd,
                industry=industry,
                sponsor_id=new_user.id
            )
            db.session.add(new_sponsor)
            db.session.commit()

            return redirect('/sponsorlogin')   
    return render_template('sponsor_register.html')
    
#SPONSOR LOGIN
@app.route('/sponsorlogin', methods=['GET', 'POST'])
def sponsorlogin():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')

        this_sponsor = User.query.filter_by(username=u_name).first()

        sponsor = Sponsor.query.filter_by(username = u_name).first()

        if not this_sponsor:
            return render_template('sponsor_login.html', error="This username does not exist.")
        
        if sponsor.flagged == 1:
            return render_template('sponsor_login.html', error="Your account has been flagged. Please contact support.")
        
        if this_sponsor.user_role != 1:
            return render_template('sponsor_login.html', error="You are not a sponsor.")

        if sponsor.password != pwd:
            return render_template('sponsor_login.html', error="Incorrect password.")   
        
        login_user(this_sponsor)

        user_id = current_user.id

        user = User.query.get(user_id)

        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id).all()

        active_campaigns = []

        for campaign in campaigns:
            if campaign_isactive(campaign.start_date, campaign.end_date, datetime.now().date()):
                active_campaigns.append(campaign)

        # adrequests = []

        # adrequests = db.session.query(Adrequest).join(Campaign).join(Influencer).filter_by(
        #     Campaign.sponsor_id == sponsor.sponsor_id,
        #     Campaign.flagged == 0,
        #     Influencer.flagged == 0,
        #     Adrequest.status.in_(['Requested to Sponsor', 'Accepted by Sponsor'])
        # ).all()
        return render_template('sponsor_dashboard.html', current_user=u_name, u_name=u_name, user_id=user_id, campaigns=campaigns, active_campaigns=active_campaigns,)
    return render_template('sponsor_login.html')


#SPONSOR DASHBOARD
@app.route('/sponsordashboard')
@login_required
def sponsordashboard():
    user_id = current_user.id
    user = User.query.get(user_id)
    sponsor = Sponsor.query.filter_by(sponsor_id = user.id).first()
    adrequests = db.session.query(Adrequest).join(Campaign).join(Influencer).filter(
        Campaign.sponsor_id == sponsor.sponsor_id,
        Campaign.flagged == 0,
        Influencer.flagged == 0,
        Adrequest.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])
    ).all()

    campaigns = Campaign.query.filter_by(sponsor_id = sponsor.sponsor_id,flagged=0).all()
    # active_campaigns=[]
    # for campaign in campaigns:
    #     if(campaign_isactive(campaign.start_date,campaign.end_date,datetime.now().date())):
    #         active_campaigns.append(campaign)
    return render_template('sponsor_dashboard.html', adrequests=adrequests, u_name=current_user.username, id = User.id, 
                            calculate_campaign_progress=calculate_campaign_progress)



#SPONSOR CREATE CAMPAIGN
@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('desc')
        budget = int(request.form.get('budget'))

        if budget < 0:
            return render_template('create_campaign.html', error="Campaign budget cannot be negative.")
        
        niche = request.form.get('niche')
        sdate = request.form.get('sdate')
        sdate = datetime.strptime(sdate, '%Y-%m-%d').date()
        edate = request.form.get('edate')
        edate = datetime.strptime(edate, '%Y-%m-%d').date()

        current_date = datetime.now().date()

        if edate < sdate:
            return render_template('create_campaign.html', error="End date cannot be before start date.")
        
        if edate < current_date:
            return render_template('create_campaign.html', error="End date cannot be in the past.")
        
        visibility = request.form.get('visibility').lower()
        goals = request.form.get('goals')

        this_id = current_user.id

        sponsor = Sponsor.query.filter_by(sponsor_id=this_id).first()

        new_campaign = Campaign(
            name=name,
            description=desc,
            campaign_budget=budget,
            start_date=sdate,
            end_date=edate,
            visibility=visibility,
            goals=goals,
            niche=niche,
            sponsor_id=sponsor.sponsor_id
        )
        db.session.add(new_campaign)
        db.session.commit()
        return redirect('/sponsor_campaign')
    return render_template('create_campaign.html')


#SPONSOR CAMPAIGNS
@app.route('/sponsor_campaign')
@login_required
def sponsor_campaign():
    this_id = current_user.id
    sponsor = Sponsor.query.filter_by(sponsor_id=this_id).first()

    if sponsor:
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id, flagged=0).all()
        return render_template('sponsor_campaign.html', campaigns=campaigns)
    
#SPONSOR VIEW CAMPAIGN
@app.route('/view_campaign/<int:campaign_id>') 
@login_required
def view_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    adrequests = db.session.query(Adrequest).join(Influencer).filter(
        Adrequest.campaign_id == campaign.id,
        Adrequest.sent_by_sponsor == True,
        Influencer.flagged == 0
    ).all()

    progress = calculate_campaign_progress(campaign.start_date, campaign.end_date)

    return render_template('view_campaign.html', campaign=campaign, adrequests=adrequests, progress=progress)

#SPONSOR DELETE CAMPAIGN
@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign:
        db.session.delete(campaign)
        db.session.commit()
    return redirect('/sponsor_campaign')


