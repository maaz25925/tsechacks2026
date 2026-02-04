#!/usr/bin/env python3
"""
Quick check: Verify you're using Supabase SERVICE ROLE key (not anon key).

Service role key bypasses RLS policies.
Anon key is subject to RLS policies.

Run: uv run python check_service_role.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings

s = get_settings()

print("=" * 60)
print("Supabase Key Check")
print("=" * 60)

if not s.supabase_key:
    print("❌ SUPABASE_KEY not set in .env")
    sys.exit(1)

key = s.supabase_key.strip()

# Service role keys are longer and start with eyJ... (JWT)
# Anon keys are shorter
if len(key) > 150 and key.startswith("eyJ"):
    print("✅ Key looks like SERVICE ROLE key (long JWT)")
    print(f"   Length: {len(key)} chars")
    print(f"   Starts with: {key[:10]}...")
    print("\n✅ This should bypass RLS policies.")
else:
    print("⚠️  Key might be ANON key (shorter)")
    print(f"   Length: {len(key)} chars")
    print(f"   Starts with: {key[:20]}...")
    print("\n⚠️  ANON keys are subject to RLS policies.")
    print("   Use SERVICE ROLE key in backend/.env for backend operations.")
    print("   Get it from: Supabase Dashboard -> Settings -> API -> service_role key")

print("\n" + "=" * 60)
print("Next steps:")
print("1. Ensure SUPABASE_KEY in .env is the SERVICE ROLE key")
print("2. Run fix_rls_policies.sql in Supabase SQL Editor")
print("3. Check Storage bucket 'videos' has upload policies")
print("=" * 60)
