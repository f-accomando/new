WO-1b (fix): on claude/search-filters, `parse_filters("tag=")` must reject an empty value.
Files: src/server/search.py and tests/test_search.py only.
Verify: python -m pytest tests/test_search.py -k filters -> exit 0.
Deliver with a DELIVERED line; expected eta 30 min.
