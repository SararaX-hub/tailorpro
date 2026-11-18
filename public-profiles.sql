-- Run in Supabase: SQL Editor > New query > paste > Run

create table public.public_profiles (
  shop_id uuid primary key references public.shops(id) on delete cascade,
  shop_name text not null default '',
  craft text not null default 'Tailor',
  region text not null default '',
  area text,
  whatsapp text not null default '',
  bio text,
  photo_paths text[] not null default '{}',
  published boolean not null default false,
  updated_at timestamptz not null default now()
);

alter table public.public_profiles enable row level security;

-- Anyone (no login) can read profiles that their owner chose to publish
create policy "anyone can read published profiles"
  on public.public_profiles for select
  using (published = true);

-- A maker can read, create, change and delete only their own profile
create policy "owner manages own profile"
  on public.public_profiles for all
  using (shop_id = auth.uid())
  with check (shop_id = auth.uid());

grant select on public.public_profiles to anon;
grant select, insert, update, delete on public.public_profiles to authenticated;

create index public_profiles_region_idx on public.public_profiles (region) where published;
