import asyncio
from datetime import datetime, timedelta
from src.likes.models import UserLike

from sqlalchemy import delete, and_
from src.database import get_async_session
from celery import Celery

from src.config import settings

celery = Celery('tasks', broker=settings.rabbit_url)


@celery.task
def update_admin_xlsx():
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(delete_old_records()))

async def delete_old_records():
    # Определите, сколько дней вы хотите сохранять записи
    days_to_keep = 7
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    # Удаление записей, старше заданного периода
    async for session in get_async_session():
        stmt = delete(UserLike).where(and_(UserLike.created_at < cutoff_date, UserLike.is_like == False))
        await session.execute(stmt)
        await session.commit()



celery.conf.beat_schedule = {
    'sync-every-15-seconds': {
        'task': 'tasks.update_admin_xlsx',
        'schedule': 10,  # Интервал в секундах
    },
}