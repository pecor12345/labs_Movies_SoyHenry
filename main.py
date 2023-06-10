
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()


@app.get("/dataframe")
def get_dataframe():
    data = {'Name': ['John', 'Jane', 'Alice'],
            'Age': [25, 30, 35]}
    df = pd.DataFrame(data)
    return JSONResponse(content=df.to_json(orient='records'), media_type='application/json')


nest_asyncio.apply()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
