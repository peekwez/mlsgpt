LISTINGS_ALL = """
SELECT id, data FROM {}.results
"""

LISTINGS_QUERY = """
SELECT id, data FROM {}.results
WHERE {}
"""

LISTINGS_SEARCH = """
SELECT id, data, {} - (embedding <=> {}::vector) AS cossim 
FROM {}.results WHERE {} - (embedding <=> {}::vector) > {}
"""
