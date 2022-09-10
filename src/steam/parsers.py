import logging
from typing import Optional, List

from pydantic import ValidationError

from .domain.models import ItemModel, ItemsJsonModel

logger = logging.getLogger(__name__)


class ItemParser:
    def __init__(self, json_model: ItemsJsonModel):
        self._items = json_model.items
        # TODO: Impl in next sprint
        self._currency_rate = json_model.u

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
        except ValidationError as ex:
            logger.warning(f'Parsing validation error', extra={'account': item['bot'], 'error': ex.errors()[0]})

        return model
