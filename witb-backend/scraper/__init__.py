"""Scraper package.

This file is required, not incidental: without it mypy resolves
`pga_tracker_scraper` under two module names ("pga_tracker_scraper" and
"scraper.pga_tracker_scraper") and aborts before checking anything, which
silently disables the type-checking gate for the whole backend.
"""
