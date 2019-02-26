from import_export import resources
from .models import MarketItem


class MarketItemResource(resources.ModelResource):
    class Meta:
        model = MarketItem
