from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests, json
import mailwrite as asop


SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

           

def createsubPage(databaseId, headers,pageid,subject,date,body):
    #create subpages under the filter heading
    createUrl = 'https://api.notion.com/v1/pages'
    newPageData = {
        "parent": { "page_id": pageid},
        "properties": {
                "title": [
                    {
                        "text": {
                            "content": subject+" "+f"(date:{date})"
                        }
                    }
                ],
        },
                "children": [
                    {
                    "object": "block",
			        "type": "paragraph",
			        "paragraph": {
				        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": body
						}
                    }
                ]
                }
                    }
                ]
        }
    
    data = json.dumps(newPageData)
    # print(str(uploadData))
    res = requests.request("POST", createUrl, headers=headers, data=data)

def createdatabasepage(databaseId,headers,name):
    #create page in notion database with particular name
    createUrl = 'https://api.notion.com/v1/pages'
    newPageData = {
        "parent": { "database_id": databaseId },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        }
    }
    data = json.dumps(newPageData)
    res = requests.request("POST", createUrl, headers=headers, data=data)
    data=json.loads(res.text)
    pageid=data['id']
    return pageid

def createNotion(d):
    #initialize notion database
    token = 'secret_d7FHzPStXT3PzdIPEdKSOPriQKPSbenoTPHaw9qWbRT'#replace with your own notion api token
    databaseId ='3092e5d70b894a859509afb6069b0a9a' #replace with own notion database id
    headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"
    }
    name=input("Enter filter name: ")
    pageid=createdatabasepage(databaseId, headers,name)
    for i in d:
        createsubPage(databaseId, headers,pageid,i,d[i]["date"],d[i]["body"])


def readmail(query,z):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    
    # Call the Gmail API to fetch INBOX
    if z==1:
        results = service.users().messages().list(userId='me',labelIds = ['INBOX'],q=query).execute()
    elif z==2:
        results = service.users().messages().list(userId='me',labelIds = ['INBOX'],q=f"from:{query}").execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        d={}
        for message in messages:
            msg = service.users().messages().get(userId='me',id=message['id'],format="full",metadataHeaders=None).execute()
            snippet=msg["snippet"]
            headers=msg["payload"]["headers"]
            for i in headers:
                if i["name"]=="Subject":
                    subject=i['value']
                    break  
                elif i["name"]=="Date":
                    date=i["value"]
            d[subject]={"date":date,"body":snippet}  
        createNotion(d)  

def main():
  while True:
    print("1.write mail\n2.Filter mail\n3.Exit")
    x=int(input("Enter choice: "))
    if x==1:
        asop.send_message()
        print("sent")
    elif x==2:
        print("1.search by word\n2.Search by mail id")
        y=int(input("Enter choice: "))
        if y==1:
            query=input("Enter word")
            readmail(query,1)
        else:
            query=input("Enter email")
            readmail(query,2)  
    else:
        break
main()       
