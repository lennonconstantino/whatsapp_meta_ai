SET session_replication_role = 'replica';

DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Starting database cleanup...';
    RAISE NOTICE '==============================================';
END $$;

-- Drop table
DROP TABLE IF EXISTS public.meta_accounts CASCADE;

-- Drop dos índices
DROP INDEX IF EXISTS public.idx_meta_accounts_owner_id;
DROP INDEX IF EXISTS public.idx_meta_accounts_phone_number;
DROP INDEX IF EXISTS public.idx_meta_accounts_business_account_id;
DROP INDEX IF EXISTS public.idx_meta_phone_numbers_gin;

-- Drop do trigger
DO $$
BEGIN
    IF to_regclass('public.meta_accounts') IS NOT NULL THEN
        EXECUTE 'DROP TRIGGER IF EXISTS update_meta_accounts_updated_at ON meta_accounts';
    END IF;
END $$;

-- Drop da function (só se não for usada por outras tabelas)
DROP FUNCTION IF EXISTS public.update_updated_at_column();


-- Re-enable foreign key checks
SET session_replication_role = 'origin';

DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Database cleanup completed!';
    RAISE NOTICE 'All tables, functions, and views removed.';
    RAISE NOTICE '==============================================';
END $$;