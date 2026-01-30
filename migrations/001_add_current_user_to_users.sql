-- 001_add_current_user_to_users.sql
-- Add a flag to mark which user is currently logged in (desktop app)
BEGIN TRANSACTION;

-- Add column with NOT NULL default 0 so existing rows are false
ALTER TABLE users ADD COLUMN current_user INTEGER NOT NULL DEFAULT 0;

-- (Optional) index to speed up queries looking for the current user
CREATE INDEX IF NOT EXISTS idx_users_current_user ON users(current_user);

COMMIT;
