-- ValidMed Schema
-- Verified AI Literature & Intelligence Database for Medical Devices

-- Core device table (source: FDA AI/ML device list)
create table devices (
  id bigint generated always as identity primary key,
  fda_submission_number text unique not null,
  device_name text not null,
  company text not null,
  decision_date date,
  specialty_panel text,
  product_code text,
  device_class smallint,
  clearance_type text,
  predicate_device text,
  evidence_score numeric(4,1) default 0,
  evidence_count int default 0,
  evidence_count_ss int default 0,  -- Semantic Scholar (non-PubMed)
  safety_event_count int default 0,
  recall_count int default 0,
  trial_count int default 0,
  has_fda_summary boolean default false,
  fda_summary_url text,
  years_since_clearance numeric(3,1),
  last_enriched_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Published evidence (source: PubMed)
create table evidence (
  id bigint generated always as identity primary key,
  device_id bigint references devices(id) on delete cascade,
  pmid text unique not null,
  title text,
  journal text,
  pub_date date,
  study_type text,
  is_manufacturer_authored boolean default false,
  abstract text,
  created_at timestamptz default now()
);

-- Adverse events (source: FDA MAUDE)
create table safety_events (
  id bigint generated always as identity primary key,
  device_id bigint references devices(id) on delete cascade,
  report_number text unique not null,
  event_type text,
  date_of_event date,
  narrative_text text,
  patient_outcome text,
  source_type text,
  created_at timestamptz default now()
);

-- Recalls (source: FDA recall database)
create table recalls (
  id bigint generated always as identity primary key,
  device_id bigint references devices(id) on delete cascade,
  recall_number text unique not null,
  reason text,
  date_initiated date,
  status text,
  root_cause text,
  product_description text,
  created_at timestamptz default now()
);

-- Clinical trials (source: ClinicalTrials.gov)
create table trials (
  id bigint generated always as identity primary key,
  device_id bigint references devices(id) on delete cascade,
  nct_id text unique not null,
  title text,
  status text,
  has_results boolean default false,
  start_date date,
  completion_date date,
  sponsor text,
  phase text,
  enrollment int,
  created_at timestamptz default now()
);

-- Indexes for common queries
create index idx_devices_company on devices(company);
create index idx_devices_specialty on devices(specialty_panel);
create index idx_devices_score on devices(evidence_score);
create index idx_evidence_device on evidence(device_id);
create index idx_safety_events_device on safety_events(device_id);
create index idx_recalls_device on recalls(device_id);
create index idx_trials_device on trials(device_id);
