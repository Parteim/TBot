from .main_handlers import router as main_router
from .vk_console_handlers import router as vk_console_router

main_router.include_routers(vk_console_router)
router = main_router
