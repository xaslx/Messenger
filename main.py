from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from src.auth.dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from logger import logger
from contextlib import asynccontextmanager
from config import settings
from src.routers.auth import auth_router
from src.routers.main import main_router
from redis_init import redis
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.app import handle_web_hook
from src.schemas.user import UserOut
from src.bot.app import on_startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield




app: FastAPI = FastAPI(
    title='Мессенджер',
    lifespan=lifespan
)


app.mount('/src/static', StaticFiles(directory='src/static'), name='static')


app.add_route(f'/{settings.TOKEN_BOT}', handle_web_hook, methods=['POST'])
app.include_router(auth_router)
app.include_router(main_router)


@app.middleware('http')
async def update_online_status(
    request: Request, 
    call_next, 
    session: AsyncSession = Depends(get_async_session)):

    '''При каждом запросе user_id записывается в редис на 1 минуту для того чтобы отслеживать что он онлайн'''

    token = request.cookies.get('user_access_token')
    response = await call_next(request)
    if token:
        user = await get_current_user(async_db=session, token=token)
        if user:
            await redis.set(f"user:{user.id}:is_online", "1", ex=60)
        return response
    return response



@app.exception_handler(404)
async def http_exception_handler(request, exc):
    #редирект в случае если не нашелся путь
    return RedirectResponse(url="/messages")