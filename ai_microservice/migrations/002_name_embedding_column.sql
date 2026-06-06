-- Drop old column if it exists with wrong dimension
ALTER TABLE catalog_reports
DROP COLUMN IF EXISTS name_embedding;

-- Add with correct dimension for local model (384)
-- Change to vector(1536) if switching to OpenAI
ALTER TABLE catalog_reports
ADD COLUMN name_embedding vector(384);

-- local (all-MiniLM-L6-v2) = 384 dimensions
-- openai (text-embedding-3-small) = 1536 dimensions
