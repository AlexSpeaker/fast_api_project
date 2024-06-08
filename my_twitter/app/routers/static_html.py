import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from my_twitter.app.utils.dependencies import GetDBDIRInfo

router = APIRouter(
    tags=["index"],
    responses={404: {"description": "Not found"}},
)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon_route(instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)]):
    """Иконка."""
    dir_info: dict = instance.get_dir_info()
    return FileResponse(os.path.join(dir_info["BASE_DIR_STATIC"], "favicon.ico"))


@router.get("/", response_class=HTMLResponse)
async def index_route(
    request: Request, instance: Annotated[GetDBDIRInfo, Depends(GetDBDIRInfo)]
):
    """Стартовая страница."""
    dir_info: dict = instance.get_dir_info()
    templates = Jinja2Templates(directory=dir_info["BASE_DIR_STATIC"])
    return templates.TemplateResponse(request, "index.html")
