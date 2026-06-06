-- Switch name_embedding to OpenAI text-embedding-3-small dimensions (1536)
ALTER TABLE catalog_reports
DROP COLUMN IF EXISTS name_embedding;

ALTER TABLE catalog_reports
ADD COLUMN name_embedding vector(1536);
