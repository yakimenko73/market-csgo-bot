import asyncio
import logging
import threading
from asyncio import Task, CancelledError
from typing import List, Dict

from steam.models import Account

from .workflow import BotWorkflow

logger = logging.getLogger(__name__)


class BotManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def run_bots(self, bots: List[Account]):
        logger.debug(threading.current_thread())
        new_tasks = []
        for bot in bots:
            if bot.login not in self._tasks.keys():
                logger.info(f'Running bot: {bot.login}', extra=self._get_log_extra_data(bot))
                new_tasks.append(self._create_task(bot))

        try:
            [await task for task in new_tasks]
        except CancelledError as ex:
            logging.debug(f'CancelledError: {ex}')

    def stop_bots(self, bots: List[Account]):
        for bot in bots:
            if bot.login in self._tasks.keys():
                logger.info(f'Stopping bot: {bot.login}', extra=self._get_log_extra_data(bot))
                self._tasks[bot.login].cancel()
                self._tasks.pop(bot.login)

    def _create_task(self, bot: Account) -> Task:
        bot_workflow = BotWorkflow(bot)

        task = asyncio.create_task(bot_workflow.run())
        task.set_name(bot.login)
        self._tasks[bot.login] = task

        logger.debug(f'Task created: {task}')

        return task

    # TODO: Move to common package
    @staticmethod
    def _get_log_extra_data(bot: Account) -> dict:
        return {'account': bot.login}
