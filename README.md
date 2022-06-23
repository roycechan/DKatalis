# DKatalis Task 2
## Folder Structure
```
+-- src
|   +-- app.py            // source code of dashboard application
|   +-- helpers.py        // helper functions to generate loan amortisation schedules 
|   +-- requirements.txt  // libraries
+-- csvs                  // folder containing .csv files found in retail-banking-demo-data
|   +-- ...
+-- insights              // folder containing screenshot of dashboard for Task 2
|   +-- ...
+-- .env                  // configuration about where the app runs
+-- Dockerfile            // docker image instructions
+-- docker-compose.yaml   // build instructions
```
## Getting Started
### Build and run container
```
docker-compose up
```
### View dashboard
Navigate to [127.0.0.1:5000](http://127.0.0.1:5000).
Otherwise, use your server IP xxx.xxx.xxx.xxx:5000 to view the dashboard.

![image](https://user-images.githubusercontent.com/20048824/175114172-d2a0b03c-ebae-42b7-a9b3-3a5a2750a444.png)

