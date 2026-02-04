from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from app.config import get_settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupabaseService:
    """
    Thin wrapper around supabase-py.

    Notes:
    - We use PostgREST via `supabase.table(...).select/insert/update/...`.
    - For hackathon MVP we keep DB operations simple and explicit.
    """

    def __init__(self) -> None:
        s = get_settings()
        if not s.supabase_url or not s.supabase_key:
            raise RuntimeError(
                "Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY in backend/.env."
            )
        self.client: Client = create_client(s.supabase_url, s.supabase_key)
        self.videos_bucket: str = s.supabase_videos_bucket

    # ---------- DB helpers ----------
    def select(self, table: str, columns: str = "*", **filters: Any) -> list[dict[str, Any]]:
        q = self.client.table(table).select(columns)
        for k, v in filters.items():
            q = q.eq(k, v)
        try:
            res = q.execute()
            return list(res.data or [])
        except Exception as e:
            print(f"SUPABASE SELECT ERROR on {table}: {e}")
            raise e

    def maybe_single(self, table: str, columns: str = "*", **filters: Any) -> dict[str, Any] | None:
        q = self.client.table(table).select(columns)
        for k, v in filters.items():
            q = q.eq(k, v)
        try:
            res = q.maybe_single().execute()
            if not res:
                print(f"SUPABASE MAYBE_SINGLE ERROR: execute() returned None for {table}")
                return None
            return res.data
        except Exception as e:
            print(f"SUPABASE MAYBE_SINGLE ERROR on {table}: {e}")
            raise e

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        try:
            res = self.client.table(table).insert(row).execute()
            if not res.data:
                print(f"SUPABASE INSERT WARNING: No data returned for {table}")
                return row
            return res.data[0]
        except Exception as e:
            print(f"SUPABASE INSERT ERROR on {table}: {e}")
            raise e

    def upsert(self, table: str, row: dict[str, Any], *, on_conflict: str = "id") -> dict[str, Any]:
        try:
            res = self.client.table(table).upsert(row, on_conflict=on_conflict).execute()
            if not res.data:
                return row
            return res.data[0]
        except Exception as e:
            print(f"SUPABASE UPSERT ERROR on {table}: {e}")
            raise e

    def update(self, table: str, updates: dict[str, Any], *, match: dict[str, Any]) -> dict[str, Any]:
        try:
            q = self.client.table(table).update(updates)
            for k, v in match.items():
                q = q.eq(k, v)
            res = q.execute()
            if not res.data:
                return updates
            return res.data[0]
        except Exception as e:
            print(f"SUPABASE UPDATE ERROR on {table}: {e}")
            raise e

    # ---------- Storage helpers ----------
    def upload_video(self, *, path: str, file_bytes: bytes, content_type: str) -> dict[str, Any]:
        """
        Uploads to Supabase Storage bucket and returns:
        { "path": "...", "public_url": "...", "bucket": "videos" }

        Bucket should be public for `public_url` to be directly playable.
        If bucket is private, front-end should request signed URLs instead.
        """
        bucket = self.client.storage.from_(self.videos_bucket)
        bucket.upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public = bucket.get_public_url(path)
        # supabase-py returns either dict or string depending on version; normalize
        public_url = public.get("publicUrl") if isinstance(public, dict) else public
        return {"path": path, "public_url": public_url, "bucket": self.videos_bucket}

    def upload_file(
        self, *, path: str, file_bytes: bytes, content_type: str, bucket_name: str | None = None
    ) -> dict[str, Any]:
        """
        Generic file upload to Supabase Storage.
        Uses videos bucket by default, but can specify another bucket.

        Returns: { "path": "...", "public_url": "...", "bucket": "..." }
        """
        bucket_name = bucket_name or self.videos_bucket
        bucket = self.client.storage.from_(bucket_name)
        bucket.upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public = bucket.get_public_url(path)
        public_url = public.get("publicUrl") if isinstance(public, dict) else public
        return {"path": path, "public_url": public_url, "bucket": bucket_name}

    def get_signed_url(self, *, path: str, expires_in: int = 3600, bucket_name: str | None = None) -> str:
        """
        Generate a signed URL for private bucket access.
        expires_in: seconds (default 1 hour)

        Returns signed URL string that expires after expires_in seconds.
        """
        bucket_name = bucket_name or self.videos_bucket
        bucket = self.client.storage.from_(bucket_name)
        signed = bucket.create_signed_url(path=path, expires_in=expires_in)
        # supabase-py may return dict or string
        if isinstance(signed, dict):
            return signed.get("signedURL") or signed.get("signedUrl") or str(signed)
        return str(signed)


_svc: SupabaseService | None = None


def get_supabase() -> SupabaseService:
    global _svc
    if _svc is None:
        _svc = SupabaseService()
    return _svc

