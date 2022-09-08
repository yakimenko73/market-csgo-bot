import logging
from typing import Optional

from pydantic import ValidationError

from .domain.models import ItemModel

logger = logging.getLogger(__name__)


class ItemParser:
    def __init__(self, currency_rate: float = None):
        # TODO: Impl in next sprint
        self._currency_rate = currency_rate

    @staticmethod
    def parse_model(item: dict) -> Optional[ItemModel]:
        model = None
        try:
            model = ItemModel(**item)
        except ValidationError as ex:
            logger.warning(f'Parsing validation error', extra={'account': item['bot'], 'error': ex.errors()[0]})

        return model
