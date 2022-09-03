from starlette.middleware.cors import CORSMiddleware
from service.excelParser import *
from endpoints.endpoints import *
from routes.api import router as api_router
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,     
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=['GET'],
    allow_headers=['Content-Type', 'application/xml'],
)


app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, log_level="info", reload=True)
    print("Running...")