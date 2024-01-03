from .main_handlers import router as admin_router
from .vk_console import router as vk_console_router

admin_router.include_router(vk_console_router)
