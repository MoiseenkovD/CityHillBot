from aiogram import Router
from .start import router as start_router
from .category import router as category_router
from .apply import router as apply_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(category_router)
    root.include_router(apply_router)
    return root
