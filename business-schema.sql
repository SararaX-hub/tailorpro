-- Run this in Supabase SQL Editor (New query > paste > Run)

create table public.expenses (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid not null references public.shops(id) on delete cascade,
  entry_date date not null,
  category text not null default 'Other',
  amount numeric not null default 0,
  note text,
  created_at timestamptz not null default now()
);

create table public.income_entries (
  id uuid primary key default gen_random_uuid(),
  shop_id uuid not null references public.shops(id) on delete cascade,
  entry_date date not null,
  amount numeric not null default 0,
  note text,
  created_at timestamptz not null default now()
);

create index expenses_shop_id_idx on public.expenses(shop_id);
create index income_entries_shop_id_idx on public.income_entries(shop_id);

alter table public.expenses enable row level security;
alter table public.income_entries enable row level security;

create policy "own expenses only" on public.expenses
  for all using (shop_id = auth.uid()) with check (shop_id = auth.uid());

create policy "own income only" on public.income_entries
  for all using (shop_id = auth.uid()) with check (shop_id = auth.uid());
