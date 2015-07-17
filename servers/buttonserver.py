"""
buttonserver.py
    handles post requests from javascript on the client side
    redirects to html pages
"""

from bottle import Bottle, run, static_file, request,response
import json
import string
import random
import json
import os
import shutil
import time 
import datetime

app = Bottle()
data = dict()
d=dict()
timestart1 = dict()
timestart2 = dict()
#loads static pages from the directory
#example: website.com/index.html
#server will load index.html from the directory
@app.route('<path:path>')
def server_static(path):
  return static_file(path, root=".")

#handles buttonpress post requests by buttonClicked function in the js
#the input is provided through the request data
#we retrieve it using json.loads
#the server decides what to load next by looking into the request data
# and seeing what the current state of the webapp is
@app.post('/ui/button')
def do_click():
  global prevTableTheta

  #init dictionary of users
  global d

  #add artificial delay
  time.sleep(0.5)

  #manually set value
  totalPicsNum = 19
  survey_duration = 10*60*60 #10 hours to prevent retaking

  #get the data that the buttonClicked posted
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]

  if "toSurvey" in sessionData:
    return json.dumps({"toSurvey":True})

  #init log variable
  global data

  #go to next/prev pic according to button clicked
  buttonClicked = requestData["buttonID"]
  if buttonClicked==0:
    sessionData["picCount"] -= 1
  elif buttonClicked==1:
    sessionData["picCount"] += 1

  if sessionData["picCount"]==1:
    ret = {"imageURL": "images/Slide1.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": "Instructions 1/4",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==2:
    ret = {"imageURL": "images/Slide2.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": "Instructions 2/4",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==3:
    ret = {"imageURL": "images/Slide3.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Instructions 3/4",
           "sessionData": sessionData}
    return json.dumps(ret)
  
  if sessionData["picCount"]==4:
    ret = {"imageURL": "images/Slide4.JPG",
           "buttonLabels": ["Prev", "START"],
           "instructionText": "Instructions 4/4",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==5:
    #generate a cookie with user's ID
    gen_id = ''.join(random.choice(string.ascii_uppercase +
      string.digits) for _ in range(6))
    response.set_cookie('mturk_id', gen_id, max_age=survey_duration, path='/')
    data[gen_id] = []
    #get ip
    ip = request.environ.get('REMOTE_ADDR')
    data[gen_id].append(ip)
    #timestamp
    startTime = datetime.datetime.now()
    data[gen_id].append("start: "+ str(startTime))
    timestart1[gen_id] = startTime   
    sessionData["playVideo"] = 1
    videoLink="videos/120to140.mp4"
    ret = {"videoURL": videoLink,
           "buttonLabels": ['Prev', 'Survey'],
           "instructionText": "ID Assigned, log started.",
           "sessionData": sessionData,
           "buttonClass": "btn-success"}
    return json.dumps(ret)

  if sessionData["picCount"]==6:
    ret = {"toSurvey": True}
    return json.dumps(ret)

  
  #following code may need mturk_id, so get it once now
  mturk_id = request.cookies.get('mturk_id','NOT SET')
  
  #record in log
  data[mturk_id].append(buttonClicked)



#when the survey is approved by surveyhandler.js, the button requests this url
#handle_survey records the responses and gives a one line html page in response
#web browsers automatically add head/body syntax for this case
@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  for i in xrange(1,17):
    data[mturk_id].append(request.forms.get(str(i)))
  with open('output/log.json', 'w') as outfile:
    json.dump(data, outfile)
  print("User {} submitted the survey".format(mturk_id))
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

#the server only writes to log.json, so if there's some data there already,
#we'll copy it to another file 
def backupLog():
  i=1
  while (os.path.isfile("output/log-backup-{}.json".format(i))):
    i+=1
  shutil.copy("output/log.json","output/log-backup-{}.json".format(i))
 
backupLog()
run(app, host='0.0.0.0', port=2222)
