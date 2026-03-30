import { createClient } from '@supabase/supabase-js';

// Supabase Project Configuration
const supabaseUrl = 'https://guptxxqqexwrembbqlmf.supabase.co';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'REPLACE_WITH_YOUR_ANON_KEY';

export const supabase = createClient(supabaseUrl, supabaseKey);
