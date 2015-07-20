# Survey Framework

##Run the interactive demo

  1. navigate to survey_framework directory
  2. run python servers/buttonserver.py
  3. in the browser, go to localhost:2222/index.html

##Getting Started

####Modifying the content
Example: display slide1.png, no instructions, "next" button (since it's the first slide, prev button is disabled)
```python
if sessionData["picCount"]==1:
    ret = {"imageURL": "images/slide1.png",
           "buttonLabels": ["null", "Next"],
           "instructionText": "",
           "sessionData": sessionData,
          }
    return json.dumps(ret)
```
buttonoptions.js deals with the returned json.


####Identifying the users
Generate an id for the client and keep it in their cookies:
```python
gen_id = ''.join(random.choice(string.ascii_uppercase +
  string.digits) for _ in range(6))
response.set_cookie('mturk_id', gen_id, max_age=survey_duration, path='/')
```
Retrieve the cookie to identify the user:
```python
mturk_id = request.cookies.get('mturk_id','NOT SET')
```


####Logging user actions
buttonserver.py keeps everything in the ``` data ``` dictionary: keys - user IDs, values - lists. 
Example: logging the time the user started the survey:
```python
startTime = datetime.datetime.now()
data[gen_id].append("start: "+ str(startTime))
```


####Saving the log
Currently done after the survey is finished.
```python
with open('output/log.json', 'w') as outfile:
    json.dump(data, outfile)
```

####Loading parsed images and instructions on the page
Example: get the image url from json returned by the server and view it on the page
```python
changeImage(jsonData["imageURL"]);
```

####Loading a questionnaire after the experiment is over
If a different page layout is needed, your server-side can include a flag in jsonData to notify the javascript. The following code may be used to switch to a different page:
```python
if ("toSurvey" in jsonData){
  window.location.href = "survey.html";
}
```
The new html file can have it's own different content, styles, and script. In our example, as the experiment is over we load a questionnaire-page which features a new javascript to handle the inputs.

