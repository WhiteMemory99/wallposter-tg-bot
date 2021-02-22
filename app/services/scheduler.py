from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from app import config

BASE_JOB_ID = "posting_{channel_id}_{user_id}"


jobstores = {"default": RedisJobStore(host=config.REDIS_HOST, password=config.REDIS_PASSWORD)}

executors = {"default": AsyncIOExecutor()}

job_defaults = {"coalesce": False, "max_instances": 3, "misfire_grace_time": 330}

apscheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


def setup():
    apscheduler.start()


def shutdown():
    apscheduler.shutdown()
