# Survey Framework

##To run

  1. navigate to buttonoptions directory
  2. run python/servers/buttonserver.py
  3. in the browser, go to localhost:2222/tableturn.html

##Getting Started

####Modifying the content
Example: display Slide1.jpg, instructions, "next" button (since it's the first slide, prev button is disabled)
```python
if sessionData["picCount"]==1:
  ret = {"imageURL": "images/Slide1.JPG",
         "buttonLabels": ["null", "Next"],
         "instructionText": "Instructions 1/3",
         "sessionData": sessionData,
         "buttonClass": "btn-primary"}
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

####Loading new content on the page
Example: get the image url from json returned by the server and view it on the page
```python
changeImage(jsonData["imageURL"]);
```
Example: when the server determines that the game is over, it adds "toSurvey" to the data
```python
if ("toSurvey" in jsonData){
  window.location.href = "survey.html";
}
```