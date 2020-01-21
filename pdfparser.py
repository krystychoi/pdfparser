#! usr/bin/python/

from tika import parser
import xml.etree.ElementTree as ET 
import requests
import sys

def getContent(pdf_url):
    try:
        file_data = parser.from_file(pdf_url)
        text = file_data["content"][:800]
        return text
    except:
        return None

production = True 

if production == True:
    solrURL = "" #provide SOLR URL
    webURL = "" #provide PDF display URL 
else:
    solrURL = "" #provide SOLR URL
    webURL = "" #provide PDF display URL

parameters = "select?q=date%3A%5B2019-06-01T00%3A00%3A00Z%20TO%202019-06-04T00%3A00%3A00Z%5D&rows=1236"
query = solrURL + parameters
response = requests.get(query)
f = open("bfresponse.xml", "wb")
f.write(response.content)
f.close()

tree = ET.parse("bfresponse.xml")
root = tree.getroot()

for result in root.iter("result"):
    numFound = result.attrib["numFound"]
    if numFound != 0:
        for doc in result:
            for child in doc:
                if child.attrib["name"] == "id":
                    id = child.text                  
                if child.attrib["name"] == "url":
                    url = child.text.replace("/", "%2F")
                    pdf_url = webURL + url
                    contentshort = getContent(pdf_url)                    
            updateURL = solrURL + "update?commit=true"
            updateDATA = '[{"id":"' + id + '","contentshort":{"set":"' + str(contentshort) + '"}}]'
            updateHEADERS = {'Content-type':'application/json'}
            runUpdate = requests.post(url=updateURL,data=updateDATA.encode("utf-8"),headers=updateHEADERS)
