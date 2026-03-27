from fastapi import FastAPI
from pydantic import BaseModel
import requests, json, time
from requests.auth import HTTPBasicAuth
 
app = FastAPI()
 
# ===== SESSION STORAGE =====
SESSION = {}
 
# ================= MODELS =================
 
class LoginRequest(BaseModel):
    session_id: str
    url: str
    username: str
    password: str
 
class UploadRequest(BaseModel):
    session_id: str
    file_name: str
    encoded_data: str
 
class StatusRequest(BaseModel):
    session_id: str
    request_id: str
 
class BaseLoadRequest(BaseModel):
    session_id: str
    ledger: str
    source: str
    group_id: str
    parameter: str
 
# ================= LOGIN =================
 
@app.post("/login")
def login(req: LoginRequest):
    try:
        test_url = req.url + "/fscmRestApi/resources/11.13.18.05/erpintegrations"
 
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(req.username, req.password),
            headers={"Content-Type": "application/json"},
            verify=False
        )
 
        if response.status_code in [200, 401]:
            if response.status_code == 401:
                return {"status": "FAILED", "message": "Invalid username or password"}
 
        # ✅ store only if valid
        SESSION[req.session_id] = {
            "url": req.url,
            "username": req.username,
            "password": req.password
        }
 
        return {"status": "SUCCESS", "message": "Login successful"}
 
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
 
 
# ================= COMMON =================
 
def get_creds(session_id):
    if session_id not in SESSION:
        raise Exception("Session not found. Please login first.")
    return SESSION[session_id]
 
 
def check_status(url, username, password, req_id):
    api = f"{url}/fscmRestApi/resources/11.13.18.05/erpintegrations?finder=ESSJobStatusRF;requestId={req_id}"
 
    while True:
        r = requests.get(api, auth=HTTPBasicAuth(username, password), verify=False)
        data = r.json()
        status = data["items"][0]["RequestStatus"]
 
        if status in ["SUCCEEDED", "ERROR", "WARNING"]:
            return status
 
        time.sleep(3)
 
 
# ================= UPLOAD =================
 
from fastapi import UploadFile, File, Form
 
@app.post("/upload")
def upload(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        creds = get_creds(session_id)
 
        # ✅ Read file
        content = file.file.read()
        print(type(file))
        print(file.filename)
        # ✅ Convert to base64
        import base64
        encoded_data = base64.b64encode(content).decode("utf-8")
 
        payload = {
            "OperationName": "importBulkData",
            "DocumentContent": encoded_data,
            "ContentType": "zip",
            "FileName": file.filename,
            "DocumentAccount": "fin$/generalLedger$/import$",
            "JobName": "/oracle/apps/ess/financials/commonModules/shared/common/interfaceLoader,InterfaceLoaderController",
            "ParameterList": f"15,#NULL,N,N,{file.filename}",
            "CallbackURL": "#NULL",
            "JobOptions": "InterfaceDetails=15,ImportOption=N,PurgeOption=N"
        }
 
        url = creds["url"] + "/fscmRestApi/resources/11.13.18.05/erpintegrations"
 
        response = requests.post(
            url,
            data=json.dumps(payload),
            auth=HTTPBasicAuth(creds["username"], creds["password"]),
            headers={"Content-Type": "application/json"},
            verify=False
        )
 
        resp = response.json()
        req_id = resp.get("ReqstId")
 
        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "request_id": req_id
        }
 
    except Exception as e:
        return {"error": str(e)}
 
 
 
# ================= STATUS =================
 
@app.post("/status")
def status(req: StatusRequest):
    creds = get_creds(req.session_id)
 
    final_status = check_status(
        creds["url"],
        creds["username"],
        creds["password"],
        req.request_id
    )
 
    return {
        "request_id": req.request_id,
        "status": final_status
    }
 
 
# ================= BASE LOAD =================
 
@app.post("/base-load")
def base_load(req: BaseLoadRequest):
    creds = get_creds(req.session_id)
 
    payload = {
        "OperationName": "submitESSJobRequest",
        "JobPackageName": "/oracle/apps/ess/financials/generalLedger/programs/common",
        "JobDefName": "JournalImportLauncher",
        "ESSParameters": f"{req.ledger},{req.source},{req.ledger},{req.group_id},{req.parameter}"
    }
 
    url = creds["url"] + "/fscmRestApi/resources/11.13.18.05/erpintegrations"
 
    response = requests.post(
        url,
        data=json.dumps(payload),
        auth=HTTPBasicAuth(creds["username"], creds["password"]),
        headers={"Content-Type": "application/json"},
        verify=False
    )
 
    resp = response.json()
    req_id = resp["ReqstId"]
 
    return {
        "message": "Base Load submitted",
        "request_id": req_id
    }
