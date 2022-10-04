import asyncio
import logging
from asyncio import Task, CancelledError
from typing import List, Dict

from common.utils import get_log_extra as extra
from steam.models import Account
from .workflow import BotWorkflow

logger = logging.getLogger(__name__)


class BotManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def run_bots(self, bots: List[Account]):
        try:
            [await task for task in [self._create_task(bot) for bot in bots if bot.login not in self._tasks]]
        except CancelledError:
            pass

    def stop_bots(self, bots: List[Account]):
        for bot in bots:
            if bot.login in self._tasks:
                task = self._tasks[bot.login]
                if not task.done():
                    logger.info('Stopping bot', extra=extra(bot.login))
                    task.cancel()
                self._tasks.pop(bot.login)

    def _create_task(self, bot: Account) -> Task:
        bot_workflow = BotWorkflow(bot)

        task = asyncio.create_task(bot_workflow.run())
        task.set_name(bot.login)
        self._tasks[bot.login] = task

        logger.debug(f'Created new task: {task}')
        logger.info('Running bot', extra=extra(bot.login))

        return task
