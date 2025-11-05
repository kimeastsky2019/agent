from fastapi import APIRouter

from app.api.v1 import auth, ontology, collaboration, spaces

api_router = APIRouter()

# 각 라우터 포함
api_router.include_router(auth.router)
api_router.include_router(ontology.router)
api_router.include_router(collaboration.router)
api_router.include_router(spaces.router)
