import logging
from traceback import format_exc as traceback
from typing import Optional, List

from pydantic import ValidationError

from common.utils import get_log_extra as extra
from .domain.models import ItemModel, ItemsJsonModel

logger = logging.getLogger(__name__)


class ItemParser:
    def __init__(self, json_model: ItemsJsonModel):
        self._items = json_model.items

    def parse_for_accounts(self, accounts_names: List[str]) -> List[ItemModel]:
        parsed_counter = 0
        models = []
        for item in self._items:
            if item['bot'] in accounts_names:
                if model := self.parse_model(item):
                    models.append(model)
                    parsed_counter += 1

        logger.info(f'Found {len(self._items)} items. Parsed: {parsed_counter}')

        return models

    @staticmethod
    def parse_model(item: dict) -> Optional[ItemModel]:
        model = None
        try:
            model = ItemModel(**item)
        except ValidationError:
            logger.warning(f'Parsing validation error for {item["asset_id"]} item',
                           extra=extra(item['bot'], traceback()))

        return model
