#!/usr/bin/env python3
"""
Standalone Supabase health check test script.

Usage:
    python test_supabase.py
    or
    uv run test_supabase.py
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.supabase_client import get_supabase
from app.config import get_settings


def supabase_health():
    """Test Supabase DB and Storage connectivity."""
    print("🔍 Testing Supabase connectivity...\n")
    
    # Check config first
    settings = get_settings()
    print(f"📋 Configuration:")
    print(f"   Supabase URL: {'✅ Set' if settings.supabase_url else '❌ Missing'}")
    print(f"   Supabase Key: {'✅ Set' if settings.supabase_key else '❌ Missing'}")
    print(f"   Videos Bucket: {settings.supabase_videos_bucket}\n")
    
    if not settings.supabase_url or not settings.supabase_key:
        print("❌ ERROR: Supabase credentials not configured!")
        print("   Please set SUPABASE_URL and SUPABASE_KEY in backend/.env")
        return False
    
    try:
        sb = get_supabase()
        print("✅ Supabase client initialized\n")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Supabase client")
        print(f"   {e}\n")
        return False
    
    # Test 1: Database connectivity
    print("🧪 Test 1: Database connectivity...")
    try:
        # Use direct client query to test DB connection
        db_result = sb.client.table("listings").select("id").limit(1).execute()
        db_data = db_result.data or []
        db_ok = True
        print(f"   ✅ Database connection successful")
        if db_data:
            print(f"   📊 Sample listing ID: {db_data[0].get('id', 'N/A')}")
        else:
            print(f"   📊 No listings found (empty table is OK)")
    except Exception as e:
        db_ok = False
        print(f"   ❌ Database test failed: {e}")
        import traceback
        print(f"   📋 Details: {traceback.format_exc()}")
    
    print()
    
    # Test 2: Storage connectivity
    print("🧪 Test 2: Storage connectivity...")
    try:
        file_res = sb.upload_file(
            path="health/test007.txt",
            file_bytes=b"nigger",
            content_type="text/plain"
        )
        storage_ok = True
        print(f"   ✅ Storage upload successful")
        print(f"   📁 File URL: {file_res.get('public_url', 'N/A')}")
        print(f"   📍 Storage path: {file_res.get('path', 'N/A')}")
    except Exception as e:
        storage_ok = False
        print(f"   ❌ Storage test failed: {e}")
    
    print()
    
    # Summary
    print("=" * 50)
    if db_ok and storage_ok:
        print("✅ ALL TESTS PASSED - Supabase is working correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        if not db_ok:
            print("   - Database connection failed")
        if not storage_ok:
            print("   - Storage upload failed")
        return False


if __name__ == "__main__":
    success = supabase_health()
    sys.exit(0 if success else 1)
