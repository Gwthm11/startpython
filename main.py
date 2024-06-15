from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_vertexai import VertexAI
import urllib
import base64
from github import Github
from github import InputGitTreeElement
import requests
import json


llm_mdl   = VertexAI(model_name="gemini-1.5-flash-001",temperature=0)

app   = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def llm(prompt):
    response = llm_mdl.invoke(prompt)
    try:
        response2=response.replace('```terraform','```')
        ss = response2.split('```')[1]
    except:
        ss = response.split('```')[1]
    
    with open("main.tf", "w") as f:
        f.write(ss)
    msg = 'Terraform file generated'     
    
    return msg

def gitcmt(repo,branch,token):
    filename='main.tf'
    url="https://api.github.com/repos/"+repo+"/contents/"+filename
    base64content=base64.b64encode(open(filename,"rb").read())
    data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token}).json()
    sha = data['sha']
    
    
    if base64content.decode('utf-8')+"\n" != data['content']:
        message = json.dumps({"message":"commit made by backend api",
                            "branch": branch,
                            "content": base64content.decode("utf-8") ,
                            "sha": sha
                            })

        resp=requests.put(url, data = message, headers = {"Content-Type": "application/json", "Authorization": "token "+token})
  
    else:
        print("nothing to update")
    msg = 'Git commit done'
    
    return msg

@app.post("/create_rsrc/gke_tf/")
async def gke(cluster_name: str, node_count: str, projectid: str,repo: str,branch: str, token: str):
    
    prompt = f"give a terraform script for creating a gke cluster of name {cluster_name} in location us-central1-c. create {node_count} nodes including the google provider with credential as file named keys.json and project id {projectid} . Give only the script without any commands and explanation."
    
    terra_ai = llm(prompt)
    
    if terra_ai=='Terraform file generated':
        gittsk = gitcmt(repo,branch,token)
    else : 
        out_msg = 'Terraform file is not found'
    
    if gittsk=='Git commit done':
        fnl_msg = 'Resource Created'
    else : 
        fnl_msg = 'Resource creation failed'
        
    return FileResponse("main.tf", media_type="application/octet-stream", filename="main.tf")  

@app.post("/create_rsrc/gcs_b_tf/")
async def gcs_b(bucket_name: str, location: str, storage_class: str, uniform_access: str ,projectid: str,repo: str,branch: str, token: str):
    
    prompt = f"give a terraform script for creating gcs bucket of name {bucket_name} in location {location} with storage class type as {storage_class} and {uniform_access} the uniform bucket level access. Including the google provider with credential as file named keys.json and project id {projectid} . Give only the script without any commands and explanation."
    
    terra_ai = llm(prompt)
    
    if terra_ai=='Terraform file generated':
        gittsk = gitcmt(repo,branch,token)
    else : 
        out_msg = 'Terraform file is not found'
    
    if gittsk=='Git commit done':
        fnl_msg = 'Resource Created'
    else : 
        fnl_msg = 'Resource creation failed'
        
    return FileResponse("main.tf", media_type="application/octet-stream", filename="main.tf") 

@app.post("/create_rsrc/gce_vm_tf/")
async def gce_vm(vm_name: str, machine_type: str, location: str, boot_disk_image: str ,projectid: str,repo: str,branch: str, token: str):
    
    prompt = f"give a terraform script for creating a vm instance of name {vm_name} machine type as {machine_type} in zone {location} with boot disk image {boot_disk_image} and default network. including the google provider with credential as file named keys.json and project id {projectid} . Give only the script without any commands and explanation."
    
    terra_ai = llm(prompt)
    
    if terra_ai=='Terraform file generated':
        gittsk = gitcmt(repo,branch,token)
    else : 
        out_msg = 'Terraform file is not found'
    
    if gittsk=='Git commit done':
        fnl_msg = 'Resource Created'
    else : 
        fnl_msg = 'Resource creation failed'
        
    return FileResponse("main.tf", media_type="application/octet-stream", filename="main.tf") 

@app.get("/")
async def hlth():
    sttr = 'Health Check' 
    return sttr
