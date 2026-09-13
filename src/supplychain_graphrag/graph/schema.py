
# CONSTRAINTS
CONSTRAINTS = [
    # `key` is the normalised identity of an entity (see ingest/resolve.py).
    # This constraint is what makes entity resolution *enforceable* rather than
    # merely attempted: two spellings that resolve to the same key cannot
    # become two nodes, because the database will not allow it.
    "CREATE CONSTRAINT entity_key IF NOT EXISTS "
    "FOR (e:Entity) REQUIRE e.key IS UNIQUE",

    "CREATE CONSTRAINT document_id IF NOT EXISTS "
    "FOR (d:Document) REQUIRE d.doc_id IS UNIQUE",

    "CREATE CONSTRAINT chunk_id IF NOT EXISTS "
    "FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE",
]

# VECTOR INDEX
VECTOR_INDEX_NAME = "chunk_embedding_index"

VECTOR_INDEX_TEMPLATE = """
CREATE VECTOR INDEX {name} IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {{indexConfig: {{
  `vector.dimensions`: {dims},
  `vector.similarity_function`: 'cosine'
}}}}
"""