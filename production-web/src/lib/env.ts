const requiredPublicEnv = {
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
  supabaseAnonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
};

export function getSupabaseEnv() {
  if (!requiredPublicEnv.supabaseUrl || !requiredPublicEnv.supabaseAnonKey) {
    throw new Error(
      "Faltan NEXT_PUBLIC_SUPABASE_URL o NEXT_PUBLIC_SUPABASE_ANON_KEY.",
    );
  }

  return {
    url: requiredPublicEnv.supabaseUrl,
    anonKey: requiredPublicEnv.supabaseAnonKey,
  };
}
