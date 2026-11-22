"""
API v1 Router Aggregator.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import system
from app.api.v1 import browser
from app.api.v1 import rg_ai
from app.api.v1 import response_validation
from app.api.v1 import stocks
from app.api.v1 import market
from app.api.v1 import overview
from app.api.v1 import learning
from app.api.v1 import conversations
from app.api.v1 import analyses
from app.api.v1 import preferences

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(system.router, tags=["System v1"])
v1_router.include_router(browser.router, tags=["Browser Automation"])
v1_router.include_router(rg_ai.router, tags=["RG AI Intelligence Orchestration"])
v1_router.include_router(response_validation.router, tags=["RG AI Response Validation"])
v1_router.include_router(stocks.router, tags=["Stock Market Price Tracking"])
v1_router.include_router(market.router, tags=["Market Overview & Indices"])
v1_router.include_router(overview.router, tags=["Market Overview & Intelligence"])
v1_router.include_router(learning.router, tags=["Learning & Education"])
v1_router.include_router(conversations.router, tags=["Conversations & Chat History"])
v1_router.include_router(analyses.router, tags=["Saved Analyses"])
v1_router.include_router(preferences.router, tags=["User Preferences"])



