-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Uploaded PDFs table
CREATE TABLE IF NOT EXISTS uploaded_pdfs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content BYTEA NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Document chunks table (with embedding vector)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES uploaded_pdfs(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384)  
    
);

-- Tools & Parts table
-- CREATE TABLE IF NOT EXISTS document_tools_parts (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     document_id UUID NOT NULL REFERENCES uploaded_pdfs(id) ON DELETE CASCADE,
--     tools TEXT[] DEFAULT '{}',
--     parts TEXT[] DEFAULT '{}',
--     UNIQUE (document_id)
-- );
