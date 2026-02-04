-- Fix Row Level Security (RLS) policies for backend operations
-- Run this in Supabase SQL Editor
--
-- IMPORTANT: Make sure backend/.env uses SERVICE ROLE key (not anon key)
-- Get it from: Supabase Dashboard -> Settings -> API -> service_role (secret)

-- ============================================================
-- QUICK FIX: Disable RLS entirely (for hackathon MVP)
-- ============================================================
-- Uncomment these if you want to disable RLS quickly:
/*
ALTER TABLE public.listings DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments DISABLE ROW LEVEL SECURITY;
*/

-- ============================================================
-- PROPER FIX: Create RLS policies (recommended)
-- ============================================================
-- 1. LISTINGS TABLE - Allow service role to insert/update
-- ============================================================

-- Option B: Create policies that allow service role (recommended)
-- Drop existing policies if any
DROP POLICY IF EXISTS "Service role can insert listings" ON public.listings;
DROP POLICY IF EXISTS "Service role can update listings" ON public.listings;
DROP POLICY IF EXISTS "Service role can select listings" ON public.listings;
DROP POLICY IF EXISTS "Anyone can view published listings" ON public.listings;

-- Enable RLS
ALTER TABLE public.listings ENABLE ROW LEVEL SECURITY;

-- Policy: Service role (backend) can do everything
CREATE POLICY "Service role can insert listings"
ON public.listings FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "Service role can update listings"
ON public.listings FOR UPDATE
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role can select listings"
ON public.listings FOR SELECT
TO service_role
USING (true);

-- Policy: Public can view published listings (for discovery endpoint)
CREATE POLICY "Anyone can view published listings"
ON public.listings FOR SELECT
TO anon, authenticated
USING (status = 'published' AND (visibility IS NULL OR visibility = 'public'));

-- ============================================================
-- 2. USERS TABLE - Allow service role operations
-- ============================================================

DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage users"
ON public.users FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Users can view own profile"
ON public.users FOR SELECT
TO authenticated
USING (auth.uid()::text = id);

-- ============================================================
-- 3. SESSIONS TABLE - Allow service role operations
-- ============================================================

DROP POLICY IF EXISTS "Service role can manage sessions" ON public.sessions;

ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage sessions"
ON public.sessions FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================
-- 4. REVIEWS TABLE - Allow service role operations
-- ============================================================

DROP POLICY IF EXISTS "Service role can manage reviews" ON public.reviews;

ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage reviews"
ON public.reviews FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================
-- 5. PAYMENTS TABLE - Allow service role operations
-- ============================================================

DROP POLICY IF EXISTS "Service role can manage payments" ON public.payments;

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage payments"
ON public.payments FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================
-- 6. STORAGE BUCKET - Allow uploads (videos bucket)
-- ============================================================

-- IMPORTANT: Storage policies are managed in Supabase Dashboard:
-- 1. Go to: Storage -> videos bucket -> Policies
-- 2. Create policy:
--    - Policy name: "Service role can upload"
--    - Allowed operation: INSERT
--    - Target roles: service_role
--    - Policy definition: true
--    - Check expression: true
--
-- OR use SQL below (may need to adjust based on your Supabase version):

-- Check if bucket exists
SELECT name, public FROM storage.buckets WHERE name = 'videos';

-- If bucket doesn't exist, create it:
-- INSERT INTO storage.buckets (id, name, public) VALUES ('videos', 'videos', true);

-- Drop existing policies if any
DELETE FROM storage.policies WHERE bucket_id = 'videos';

-- Allow service role to upload/read/delete (bypasses RLS)
INSERT INTO storage.policies (name, bucket_id, definition, check_expression, role)
VALUES 
  ('Service role can upload', 'videos', 'true', 'true', 'service_role'),
  ('Service role can read', 'videos', 'true', NULL, 'service_role'),
  ('Service role can delete', 'videos', 'true', 'true', 'service_role');

-- Allow public read (if bucket is public)
INSERT INTO storage.policies (name, bucket_id, definition, check_expression, role)
VALUES 
  ('Public can read videos', 'videos', 'true', NULL, 'anon');

-- ============================================================
-- VERIFICATION
-- ============================================================

-- Check policies on listings
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' AND tablename = 'listings';

-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('listings', 'users', 'sessions', 'reviews', 'payments');
