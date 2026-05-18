"""Read-only Meta adapter package."""

from .adapter import MetaReadonlyAdapter, MockMetaReadonlyAdapter
from .live import LiveMetaReadonlyAdapter, MetaConfigError, MetaGraphReadonlyClient, load_meta_readonly_config
from .models import AccountSnapshot, AdItem, AdSetItem, CampaignItem

__all__ = [
    "AccountSnapshot",
    "AdItem",
    "AdSetItem",
    "CampaignItem",
    "LiveMetaReadonlyAdapter",
    "MetaConfigError",
    "MetaGraphReadonlyClient",
    "MetaReadonlyAdapter",
    "MockMetaReadonlyAdapter",
    "load_meta_readonly_config",
]
