from fastapi import APIRouter, status, Depends, BackgroundTasks

from configs.security import UnauthorizedMessage, get_token
from configs.logger import logger
from configs.db import content_embedded_collection
from controllers.elastic import Elastic
from utils.exception_handling import handle_exceptions
from bson import ObjectId
import os

content_sync_route = APIRouter(tags=["CONTENT_SYNC"])
elastic = Elastic()


@content_sync_route.get(
    "/content/sync/product",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def find_all_embedded(
    token_auth: str = Depends(get_token)
):
    return {"message": "Success"}