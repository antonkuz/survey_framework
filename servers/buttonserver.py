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
startTime = None
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
  #reference the globals
  global data, startTime
  survey_duration = 10*60*60 #10 hours to prevent retaking

  #get the data that the buttonClicked posted
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]

  if "toSurvey" in sessionData:
    return json.dumps({"toSurvey":True})

  #go to next/prev pic according to button clicked
  buttonClicked = requestData["buttonID"]
  if buttonClicked==0:
    sessionData["picCount"] -= 1
  elif buttonClicked==1:
    sessionData["picCount"] += 1

  if sessionData["picCount"]==2:
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
    ret = {"imageURL": "images/slide2.png",
           "buttonLabels": ["Yo", "Next"],
           "instructionText": "I am text!",
           "sessionData": sessionData,
          }
    return json.dumps(ret)

  if sessionData["picCount"]==3:
    ret = {"imageURL": "images/slide3.png",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Slide 3",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==4:  
    sessionData["playVideo"] = 1
    videoLink="videos/120to140.mp4"
    ret = {"videoURL": videoLink,
           "imageURL": "images/slide4.png",
           "buttonLabels": ['Prev', 'Next'],
           "instructionText": "Notice disabled buttons",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==5:
    sessionData["playVideo"] = 0
    ret = {"imageURL": "images/slide5.png",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==6:
    ret = {"toSurvey": True}
    return json.dumps(ret)

  mturk_id = request.cookies.get('mturk_id','NOT SET')
  
  #record in log
  data[mturk_id].append(buttonClicked)



#when the survey is approved by surveyhandler.js, the button requests this url
#handle_survey records the responses and gives a one line html page in response
#web browsers automatically add head/body syntax for this case
@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  for i in xrange(1,9):
    data[mturk_id].append(request.forms.get(str(i)))
  with open('output/log.json', 'w') as outfile:
    json.dump(data, outfile)
  print("User {} submitted the survey".format(mturk_id))
  return """<img src="images/slidex.png" />
            <br><p>Fun fact: you started the demo at {}</p>
         """.format(startTime)

#the server only writes to log.json, so if there's some data there already,
#we'll copy it to another file 
def backupLog():
  i=1
  while (os.path.isfile("output/log-backup-{}.json".format(i))):
    i+=1
  shutil.copy("output/log.json","output/log-backup-{}.json".format(i))
 
backupLog()
run(app, host='0.0.0.0', port=2222)