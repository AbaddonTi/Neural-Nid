import os
import pandas as pd
import pytz


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
from pydantic import BaseModel


# region Metrics
class LogData(BaseModel):
    IP: str
    Question: str
    Answer: str
    Device: str
    Browser: str
    OS: str

app = FastAPI()
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
# endregion


# region Web service
@app.post("/log")
async def log_to_csv(data: LogData):
    try:
        tz = pytz.timezone('Europe/Paris')
        now = datetime.now(tz)
        latest_file_csv = os.path.join(log_dir, "logs.csv")

        if not os.path.exists(latest_file_csv):
            df = pd.DataFrame(columns=['Time', 'IP', 'Question', 'Answer', 'Device', 'Browser', 'OS'])
        else:
            df = pd.read_csv(latest_file_csv)

        new_row = data.dict()
        new_row['Time'] = now.strftime('%Y-%m-%d %H:%M:%S')

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(latest_file_csv, index=False)

        return JSONResponse(content={"message": "Logged successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log data: {str(e)}")



@app.get("/get_latest_log")
async def get_latest_log():
    try:
        latest_file_csv = os.path.join(log_dir, "logs.csv")
        if os.path.exists(latest_file_csv):
            return FileResponse(path=latest_file_csv, filename="logs.csv")
        else:
            return JSONResponse(content={"message": "No logs found"}, status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# endregion
