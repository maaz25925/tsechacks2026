-- Migration: Add new fields to listings table for enhanced video upload flow
-- Run this in Supabase SQL Editor

-- Add category field (text, nullable)
alter table if exists public.listings
  add column if not exists category text;

-- Add visibility field (text, nullable) with check constraint
alter table if exists public.listings
  add column if not exists visibility text check (visibility in ('draft', 'public', 'private'));

-- Add base_price field (double precision, nullable)
alter table if exists public.listings
  add column if not exists base_price double precision;

-- Add transcription_url field (text, nullable)
alter table if exists public.listings
  add column if not exists transcription_url text;

-- Add course_outcomes field (jsonb, nullable) - stores array of strings
alter table if exists public.listings
  add column if not exists course_outcomes jsonb;

-- Optional: Add comment for documentation
comment on column public.listings.category is 'Course category (e.g., "meditation", "music", "fitness")';
comment on column public.listings.visibility is 'Visibility setting: draft, public, or private';
comment on column public.listings.base_price is 'Base price/cost of the course';
comment on column public.listings.transcription_url is 'URL to transcription file in Supabase Storage';
comment on column public.listings.course_outcomes is 'AI-generated learning outcomes as JSON array of strings';
