LISTINGS_ALL = """
SELECT id, data FROM {}.results
ORDER BY created_at DESC 
LIMIT {}
OFFSET {}
"""

LISTINGS_QUERY = """
SELECT id, data FROM {}.results
WHERE {}
ORDER BY created_at \
DESC LIMIT {}
OFFSET {}
"""

LISTINGS_SEARCH = """
SELECT id, data, {} - (embedding <=> {}::vector) AS cossim 
FROM {}.results WHERE {} - (embedding <=> {}::vector) > {}
ORDER BY created_at 
DESC LIMIT {}
OFFSET {}
"""
