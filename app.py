print('Starting project chat bot Content Searching ::: ')
from fastapi import FastAPI, Request
import time, datetime
from configs.middleware import log_request_middleware

from elasticapm import set_context
from starlette.requests import Request
from elasticapm.utils.disttracing import TraceParent
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv('configs/.env.secret')
load_dotenv('configs/.env.shared')

ALLOWED_ORIGINS = ['*']

app = FastAPI(
    title="Project Chat AI: Content Searching API (2023)", 
    description=f"Created by zax \n TNT Media and Network Co., Ltd. \n Started at {datetime.datetime.now().strftime('%c')}",
    docs_url="/",
    version="1.0.0",
    )

app.add_middleware(  
    CORSMiddleware,  
    allow_origins=ALLOWED_ORIGINS,  # Allows CORS for this specific origin  
    allow_credentials=True,  
    allow_methods=["*"],  # Allows all methods  
    allow_headers=["*"],  # Allows all headers  
)  

@app.middleware("http")  
async def add_process_time_header(request: Request, call_next):  
    trace_parent = TraceParent.from_headers(request.headers)  
    set_context({  
        "method": request.method,  
        "url_path": request.url.path,  
    }, 'request')  
    response = await call_next(request)  
    set_context({  
        "status_code": response.status_code,  
    }, 'response')  
    # Check if the status code is not in the range of 200-299  
    if 200 <= response.status_code < 300:  
        transaction_status = 'success'  
    else:  
        transaction_status = 'failure'  
    return response  

app.middleware("http")(log_request_middleware)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = "{0:.2f}ms".format(process_time)
    return response

from utils.manage_db import create_index_es
create_index_es()

from routes.content_embedded_route import content_embedded_route
app.include_router(content_embedded_route)

from routes.content_search_route import content_search_route
app.include_router(content_search_route)

from routes.content_sync_route import content_sync_route
app.include_router(content_sync_route)

from routes.content_report_route import content_report_route
app.include_router(content_report_route)
print('Started project chat bot Content Searching ::: ')