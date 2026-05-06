from aiogram import Router

from bot.handlers import admin, faq, registration, report, start, status

router = Router(name="root")
router.include_routers(
    admin.router,
    registration.router,
    start.router,
    report.router,
    status.router,
    faq.router,
)
