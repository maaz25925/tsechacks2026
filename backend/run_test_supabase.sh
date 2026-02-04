#!/bin/bash
# Run Supabase health check test

cd "$(dirname "$0")"

echo "Running Supabase health check..."
echo ""

# Try uv first, fallback to python
if command -v uv &> /dev/null; then
    uv run test_supabase.py
else
    python test_supabase.py
fi
