from .destinations import router as destinations_router
from .endorsements import router as endorsements_router
from .recommendations import router as recommendations_router

__all__ = ["destinations_router", "endorsements_router", "recommendations_router"]
