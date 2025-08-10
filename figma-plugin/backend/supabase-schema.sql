-- Growth99 Figma Plugin MVP Database Schema
-- Run these commands in your Supabase SQL editor

-- Sessions table (MVP - basic tracking)
create table if not exists sessions (
  id uuid default gen_random_uuid() primary key,
  project_id text not null,
  user_id text not null,
  figma_file_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (optional for MVP)
-- alter table sessions enable row level security;

-- Future tables (ready for implementation)
-- Uncomment when ready to expand beyond MVP

/*
-- Projects table
create table if not exists projects (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  description text,
  figma_file_id text,
  user_id text not null,
  design_system jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Generated pages table
create table if not exists generated_pages (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade,
  page_name text not null,
  page_spec jsonb not null,
  figma_page_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Chat history table
create table if not exists chat_history (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade,
  message text not null,
  role text not null check (role in ('user', 'assistant')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
*/