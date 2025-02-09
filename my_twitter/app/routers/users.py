from fastapi import APIRouter

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
