-- Migration: Add Escrow and Milestone tables for milestone-based payments

-- Create escrows table
CREATE TABLE escrows (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  finternet_intent_id TEXT NOT NULL UNIQUE,
  total_amount FLOAT NOT NULL,
  locked_amount FLOAT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT status_check CHECK (status IN ('active', 'released', 'failed'))
);

-- Create index on session_id for faster lookups
CREATE INDEX escrows_session_id_idx ON escrows(session_id);
CREATE INDEX escrows_intent_id_idx ON escrows(finternet_intent_id);

-- Create milestones table
CREATE TABLE milestones (
  id TEXT PRIMARY KEY,
  escrow_id TEXT NOT NULL REFERENCES escrows(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  index INT NOT NULL,
  description TEXT NOT NULL,
  amount FLOAT NOT NULL,
  percentage FLOAT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  proof_data JSONB DEFAULT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT status_check CHECK (status IN ('pending', 'proof_submitted', 'completed', 'failed')),
  CONSTRAINT percentage_check CHECK (percentage >= 0 AND percentage <= 100),
  CONSTRAINT amount_check CHECK (amount > 0)
);

-- Create indexes on milestones
CREATE INDEX milestones_escrow_id_idx ON milestones(escrow_id);
CREATE INDEX milestones_session_id_idx ON milestones(session_id);
CREATE INDEX milestones_status_idx ON milestones(status);

-- Grant appropriate permissions (adjust roles as needed for your Supabase setup)
-- For Supabase, the default authenticated user should have access via RLS policies
