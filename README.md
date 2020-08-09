## Deploy instructions


1. Rename *you_need.env* to *.env* and fill config constants

2. Build and start containers(need docker and docker-compose to be installed)

```
docker-compose up -d
```

3. Prepare router(need to automate this step):

3.1 Make named access-lists
3.2 Make and firewall rules for this lists
3.3 Place up/down scripts for ppp profile
3.4 Make specific user for this application
3.5 Other security preparations
3.6 Create and fill VPN accounts


---


### How it works


There are several hosts that communicate and interact together:

- Client
- Router
- Django web API(hiddden behind NGINX + gunicorn) that does almost all logic
- Telegram updates watcher — just triggers API when client confirmes connection in chat


---


### Few words about process roadmap


1. Client connects to VPN service

2. Connection triggers script that does:
- Moves source ip address of client to DENY_LIST(sandbox)
- Sends request to API */client/connect/* endpoint with payload that contains **source ip**, **destination ip** and **chat id**

3. Backend makes:
- verification that client has not exceed unconfirmed connections limit
    - sends "ban" command to router and client's ip moves to permanent ban list on router
- either creates new client or edits existed client instance
- sends confirmation button to client's chat

4. Watcher listens(or watches(lol)) telegram updates and here are few scenarios:
- client clicks button and wathcer sends confirm request to API(move next step)
- client waits too long, button will be removed and client will be disconnected from router by background celery task, that triggers API's */client/timecheck/* endpoint and backend does all the work

5. Backend checks if client is connected:
- If true — client is confirmed, backend triggers router to move client to PERMIT_LIST(allow)
- If disconnected — notifies about this fact in chat
- If router is unavailable — notifies about this too

6. When client disconnects from router, script does:
- remove client's ip from PERMIT_LIST
- send request to API to change client's status


---


### TODO

-[ ] tests


---
