-- Create customer_memory table for AI long-term memory
CREATE TABLE IF NOT EXISTS customer_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255),
    fact TEXT NOT NULL,
    intent VARCHAR(100),
    summary TEXT, -- Optional, used in some contexts
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast retrieval by phone 
CREATE INDEX IF NOT EXISTS idx_customer_memory_phone ON customer_memory(phone);
CREATE INDEX IF NOT EXISTS idx_customer_memory_created_at ON customer_memory(created_at DESC);
