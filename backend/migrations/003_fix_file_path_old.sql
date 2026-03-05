-- Migration: Fix file_path_old column constraint
-- Makes file_path_old nullable since we're not using it anymore

-- Make file_path_old nullable
ALTER TABLE artifacts ALTER COLUMN file_path_old DROP NOT NULL;

-- Or alternatively, drop it entirely (uncomment if preferred):
-- ALTER TABLE artifacts DROP COLUMN IF EXISTS file_path_old;
