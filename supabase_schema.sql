-- Enable Row Level Security
ALTER TABLE IF EXISTS public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.clauses ENABLE ROW LEVEL SECURITY;

-- 1. Profiles Table (Extending Auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users NOT NULL PRIMARY KEY,
  updated_at TIMESTAMP WITH TIME ZONE,
  username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT
);

-- 2. Reports Table (AI Analysis Metadata)
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  filename TEXT NOT NULL,
  risk_score INTEGER NOT NULL,
  risk_category TEXT NOT NULL,
  jurisdiction TEXT DEFAULT 'Central',
  file_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Clauses Table (Individual Analysis Results)
CREATE TABLE IF NOT EXISTS public.clauses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  report_id UUID REFERENCES public.reports(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  original_text TEXT NOT NULL,
  classification TEXT NOT NULL, -- ILLEGAL, UNFAIR, FAIR
  explanation TEXT,
  statute TEXT,
  remedy TEXT
);

-- RLS Policies
CREATE POLICY "Users can view their own reports" ON public.reports
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reports" ON public.reports
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view clauses of their own reports" ON public.clauses
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.reports 
      WHERE id = public.clauses.report_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert clauses of their own reports" ON public.clauses
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.reports 
      WHERE id = public.clauses.report_id AND user_id = auth.uid()
    )
  );
