
-- Create table
CREATE TABLE meta_accounts (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    meta_business_account_id VARCHAR(255) NOT NULL,
    phone_number_id VARCHAR(255) NOT NULL,
    meta_phone_number VARCHAR(50) NOT NULL,
    system_user_access_token VARCHAR(500) NOT NULL,
    webhook_verification_token VARCHAR(500) NOT NULL,
    phone_numbers JSONB DEFAULT '[]'::jsonb,
    -- Future implementation
    -- owner_id      TEXT NOT NULL REFERENCES owners(owner_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

);

-- Indexes para melhor performance
-- CREATE INDEX idx_meta_accounts_owner_id ON meta_accounts(owner_id);
CREATE INDEX idx_meta_accounts_phone_number ON meta_accounts(meta_phone_number);
CREATE INDEX idx_meta_accounts_business_account_id ON meta_accounts(meta_business_account_id);
CREATE INDEX idx_meta_phone_numbers_gin ON meta_accounts USING gin(phone_numbers);


COMMENT ON INDEX idx_meta_accounts_owner_id IS 'Índice para busca rápida por owner_id';
COMMENT ON INDEX idx_meta_accounts_phone_number IS 'Índice para busca rápida por meta_phone_number';
COMMENT ON INDEX idx_meta_accounts_business_account_id IS 'Índice para busca rápida por meta_business_account_id';
COMMENT ON INDEX idx_meta_phone_numbers_gin IS 'Índice para busca rápida por meta_phone_numbers usando GIN';


-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_meta_accounts_updated_at
    BEFORE UPDATE ON meta_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();