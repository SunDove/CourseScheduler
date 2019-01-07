import requests
import json


class CourseGrabber:

    def __init__(self):
        pass

    def doSearch(self, fields, semester="2191"):
        url = "https://classes.colorado.edu/api/"
        querystring = {"page":"fose","route":"search"}
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'Postman-Token': "44ff740c-90b5-4cb0-ae59-c0a53a2bd4b3"
        }
        c = []
        ignore = ['srcdb', 'type']
        for f in fields:
            if f in ignore:
                continue
            c.append({"field":f, "value":fields[f]})
        payload = {
            "other": {"srcdb":str(semester)},
            "criteria": c
        }
        r = requests.post(url, headers=headers, params = querystring, data=json.dumps(payload))
        return r.text

    def getSections(self, fields):
        url = "https://classes.colorado.edu/api/"
        querystring = {"page":"fose","route":"details"}
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'Postman-Token': "44ff740c-90b5-4cb0-ae59-c0a53a2bd4b3"
        }
        c = {}
        ignore = ['type']
        for f in fields:
            if f in ignore:
                continue
            c[f] = fields[f]
        payload = c
        r = requests.post(url, headers=headers, params = querystring, data=json.dumps(payload))
        return r.text

    def getAuthToken(self, username, password):

        session = requests.Session()

        # get the inital page, found url by disecting js code from
        # mycuinfo.colorado.edu
        init_page = session.get("https://ping.prod.cu.edu/as/authorization.oauth2?client_id=CUBoulderClassSearch&response_type=token&IdpSelectorId=BoulderIDP&scope=AcademicRecords&redirect_uri=https://classes.colorado.edu/sam/oauth.html")
        init_text = init_page.text

        # set the post data for the next request
        samlValue = init_text.split('name="SAMLRequest" value="')[1].split('"')[0]
        relay = init_text.split('name="RelayState" value="')[1].split('"')[0]
        action = init_text.split('method="post" action="')[1].split('"')[0]
        ver1_data = {
            "SAMLRequest" : samlValue,
            "RelayState" : relay
        }

        # human verification page num. 1
        post_page = session.post(action, data=ver1_data)
        post_page_text = post_page.text

        postURL = post_page_text.split('fm-login" name="login" action="')[1].split('"')[0]
        login_data = {
            "timezoneOffset": "0",
            "_eventId_proceed": "Log In",
            "j_username": username,
            "j_password": password
        }

        # user login page
        login_request = session.post(
            "https://fedauth.colorado.edu" + postURL, data=login_data)

        login_text = login_request.text

        RelayState = login_text.split('name="RelayState" value="')[
            1].split('"')[0]
        SAMLResponse = login_text.split(
            'name="SAMLResponse" value="')[1].split('"')[0]

        ver3_data = {
            "RelayState": RelayState,
            "SAMLResponse": SAMLResponse
        }

        # human verification page num. 3
        third_post_page = session.post(
            "https://ping.prod.cu.edu/sp/ACS.saml2",
            data=ver3_data)

        ind = third_post_page.url.find('access_token=')
        end = third_post_page.url.find('&', ind+1)
        return third_post_page.url[ind+13:end]

    def getUserId(self, token):
        r = requests.get('https://classes.colorado.edu/api/?page=sisproxy&oauth_token='+token)
        text = r.text
        text = text[text.find('(')+1: text.find(')')]
        print(text)
        return json.loads(text)
