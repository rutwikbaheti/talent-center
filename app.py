from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from datetime import datetime 
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/hrdb"
mongo = PyMongo(app)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/recruitment',methods=["GET","POST"])
def recruitment():
    all_jobs = mongo.db.job.find({})
    if('sort_by' in request.args): 
        sort_by = request.args['sort_by']
        if(request.args['sort_by'] == 'newest') :
            all_jobs.sort('date-time',-1)
        elif (request.args['sort_by'] == 'oldest'):   
            all_jobs.sort('date-time',1)   
    else:
        sort_by = None        
    return render_template('recruitment.html',all_jobs=all_jobs,sort_by=sort_by)

@app.route('/add_job',methods=["GET","POST"])
def add_job():
    if request.method == 'POST':
        mongo.db.job.insert_one({
            'job_title':request.form.get("job_title"),
            'job_type' : request.form.get("job_type"),
            'location' : request.form.get("location"),
            'onsite_or_remote' : request.form.get("onsite_or_remote"),
            'department' : request.form.get("department"),
            'experience' : request.form.get("experience"),
            'skills' : request.form.get("skills"),
            'job_decription' : request.form.get("job_decription"),
            'currency' : request.form.get("currency"),
            'min_salary' : request.form.get("min_salary"),
            'max_salary' : request.form.get("max_salary"),
            'date-time': datetime.now(),
            'last_update' : datetime.now()
        })
        return redirect(url_for("recruitment"))
    return render_template('add_job.html')
 
@app.route('/job_info')
def job_info():
    if('_id' in request.args):
        job = mongo.db.job.find_one({"_id" : ObjectId(request.args['_id'])})
    return render_template('job_info.html',job=job)

@app.route('/edit_job',methods=["GET","POST"])
def edit_job():
    if('_id' in request.args):
        job = mongo.db.job.find_one({"_id" : ObjectId(request.args['_id'])})
        if request.method == "POST":
            mongo.db.job.update_many({"_id" : ObjectId(request.args['_id'])},
            {"$set":{'job_title':request.form.get("job_title"),
            'job_type' : request.form.get("job_type"),
            'location' : request.form.get("location"),
            'onsite_or_remote' : request.form.get("onsite_or_remote"),
            'department' : request.form.get("department"),
            'experience' : request.form.get("experience"),
            'skills' : request.form.get("skills"),
            'job_decription' : request.form.get("job_decription"),
            'currency' : request.form.get("currency"),
            'min_salary' : request.form.get("min_salary"),
            'max_salary' : request.form.get("max_salary"),
            'last_update' : datetime.now()}})
            return redirect(url_for("job_info",_id=ObjectId(request.args['_id'])))
    return render_template('edit_job.html',job=job)

@app.route('/delete_job')
def delete_job():
    if('_id' in request.args):
        mongo.db.job.delete_one({"_id" : ObjectId(request.args['_id'])})
    return redirect(url_for("recruitment"))

@app.route('/candidates',methods=["GET","POST"])
def candidates():
    if('_id' in request.args):
        job = mongo.db.job.find_one({"_id" : ObjectId(request.args['_id'])})
        if('sort_by' in request.args): 
            sort_by = request.args['sort_by']
            if(request.args['sort_by'] == 'newest') :
                job['candidate'].sort(key=lambda item:item['date_time'], reverse=True)
            elif (request.args['sort_by'] == 'oldest'):   
                job['candidate'].sort(key=lambda item:item['date_time'])
        else:
            sort_by = None;        
    return render_template('candidates.html',job=job,sort_by=sort_by)

@app.route('/add_candidate',methods=["GET","POST"])
def add_candidate():
    if('_id' in request.args):
        job = mongo.db.job.find_one({'_id' : ObjectId(request.args['_id'])})
        if request.method == "POST":
            info = {}
            info["_id"]= ObjectId()
            info['phone_no']=request.form['phone_no']
            info['email']=request.form['email']
            info['education']=request.form['education']
            info['experience']=request.form['experience']
            info['current_ctc']=request.form['current_ctc']
            info['expected_ctc']=request.form['expected_ctc']
            info['current_location']=request.form['current_location']
            info['current_company']=request.form['current_company']
            info['notice_period']=request.form['notice_period']
            info['comments']=request.form['comments']
            info['date_time'] = datetime.now()
            info['last_update'] = datetime.now()
            mongo.db.job.update_one({"_id" : ObjectId(request.args['_id'])},
            {'$push':  {'candidate' : info}})
            id = ObjectId(request.args['_id'])
            return redirect(url_for("candidates",_id = ObjectId(request.args['_id'])))
    return render_template('add_candidate.html',job=job)

@app.route("/edit_candidate/",methods=["GET","POST"])
def edit_candidate():
    if('_id' in request.args):
        job = mongo.db.job.find_one({"_id" : ObjectId(request.args['_id'])})
        if('candidate_id' in request.args):
            for i in job['candidate']:
                if( i["_id"] == ObjectId(request.args['candidate_id'])):
                    candidate = i 
                    if request.method == "POST":
                        mongo.db.job.update_many(
                            {"_id" : ObjectId(request.args['_id']),
                            "candidate._id":ObjectId(request.args['candidate_id'])},
                            {"$set" : {
                                'candidate.$.phone_no' : request.form.get('phone_no'),
                                'candidate.$.email' : request.form.get('email'),
                                'candidate.$.education' : request.form.get('education'),
                                'candidate.$.experience' : request.form.get('experience'),
                                'candidate.$.current_ctc' : request.form.get('current_ctc'),
                                'candidate.$.expected_ctc' : request.form.get('expected_ctc'),
                                'candidate.$.current_location' : request.form.get('current_location'),
                                'candidate.$.current_company' : request.form.get('current_company'),
                                'candidate.$.notice_period' : request.form.get('notice_period'),
                                'candidate.$.comments' : request.form.get('comments')
                            }   }
                        )
                        return redirect(url_for('candidates',_id=ObjectId(request.args['_id'])))
    return render_template('edit_candidate.html',job=job,candidate=candidate)        

@app.route('/delete_candidate')
def delete_candidate():
    if('_id' in request.args):
        if('candidate_id' in request.args):
            mongo.db.job.update_one(
            {"_id" : ObjectId(request.args['_id'])},
            {"$pull" : 
                {"candidate" : {"_id" : ObjectId(request.args['candidate_id'])}}
            }
            )
    return redirect(url_for('candidates',_id=ObjectId(request.args['_id'])))

@app.route('/employee',methods=["GET","POST"])
def employee():
    return render_template('employee.html')

@app.route('/add_employee')
def add_employee():
    return render_template('add_employee.html')

if __name__ == "__main__":
  app.run(debug=True)