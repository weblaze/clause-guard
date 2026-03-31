'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
import { Shield, FileSearch, Scale, Zap, Lock, ArrowRight, Gavel } from 'lucide-react';

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null);
      setLoading(false);

      // Clean up sensitive tokens from URL
      if (event === 'SIGNED_IN' || window.location.hash.includes('access_token')) {
        window.history.replaceState(null, '', window.location.pathname);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin,
        }
      });
      if (error) throw error;
    } catch (error) {
      console.error("Error signing in with Google:", error);
    }
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header className="glass" style={{ position: 'sticky', top: 0, zIndex: 100, padding: '1.25rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="flex-center" style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)' }}>
              <Shield size={20} color="white" />
            </div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '900', letterSpacing: '-0.03em' }}>Clause<span className="gradient-text">Guard</span></h1>
          </div>
          
          <nav style={{ display: 'flex', gap: '2.5rem' }}>
            {['Engine', 'Statutes', 'Privacy', 'Compliance'].map((item) => (
              <Link key={item} href={`#${item.toLowerCase()}`} style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '0.9rem', fontWeight: '500', transition: 'color 0.3s' }}>{item}</Link>
            ))}
          </nav>

          <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
            {loading ? (
              <div className="animate-spin" style={{ width: '24px', height: '24px', border: '2px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-gold)', borderRadius: '50%' }}></div>
            ) : user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '0.85rem', fontWeight: '600' }}>{user.user_metadata?.full_name || user.email}</p>
                  <button onClick={logout} style={{ fontSize: '0.7rem', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Terminate Session</button>
                </div>
                <Link href="/analyze" className="btn-primary" style={{ textDecoration: 'none', padding: '0.6rem 1.5rem' }}>Dashboard</Link>
              </div>
            ) : (
              <button onClick={loginWithGoogle} className="btn-primary" style={{ padding: '0.6rem 2rem' }}>Authenticate</button>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{ padding: '8rem 0 6rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', width: '80%', height: '80%', background: 'radial-gradient(circle, rgba(16, 185, 129, 0.05) 0%, transparent 70%)', filter: 'blur(100px)', zIndex: 0 }}></div>
        
        <div className="container" style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1.25rem', borderRadius: '40px', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.1)', marginBottom: '2.5rem', fontSize: '0.85rem', fontWeight: '600', color: 'var(--accent-primary)' }}>
            <Zap size={14} /> Model Tenancy Act 2021 Compliant
          </div>
          
          <h1 className="animate-fade-in" style={{ fontSize: '5.5rem', lineHeight: '1.05', fontWeight: '900', letterSpacing: '-0.04em', marginBottom: '2.5rem', maxWidth: '1000px', marginInline: 'auto' }}>
            Smart Lease Audits <br /> Grounded in <span className="gradient-text">Indian Law</span>
          </h1>
          
          <p className="animate-fade-in" style={{ fontSize: '1.35rem', color: 'var(--text-muted)', marginBottom: '4rem', maxWidth: '650px', marginInline: 'auto', lineHeight: '1.6' }}>
            The AI-powered barrier between predatory rental clauses and tenant rights. Secure, cloud-native automated legal protection.
          </p>

          <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
            <Link href="/analyze" className="btn-primary" style={{ fontSize: '1.2rem', padding: '1.25rem 3.5rem', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              Analyze My Agreement <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats/Features Grid */}
      <section style={{ padding: '6rem 0' }} id="engine">
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2.5rem' }}>
            {[
              { icon: <Gavel />, title: 'Statutory Grounding', desc: 'Every analysis maps directly to the Model Tenancy Act 2021 and regional statutes.' },
              { icon: <FileSearch />, title: 'RAG Architecture', desc: 'Secure retrieval-augmented generation ensures precise clause classification.' },
              { icon: <Lock />, title: 'Cloud Encrypted', desc: 'Documents are processed in secure ephemeral environments and immediately purged.' }
            ].map((feature, i) => (
              <div key={i} className="glass" style={{ padding: '3rem 2.5rem', borderRadius: '32px', textAlign: 'center', transition: 'transform 0.3s' }}>
                <div className="flex-center" style={{ width: '60px', height: '60px', marginInline: 'auto', marginBottom: '2rem', borderRadius: '16px', background: 'rgba(255,255,255,0.02)', color: 'var(--accent-gold)' }}>
                  {feature.icon}
                </div>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 'bold', marginBottom: '1rem' }}>{feature.title}</h3>
                <p style={{ color: 'var(--text-muted)', lineHeight: '1.6' }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer style={{ padding: '4rem 0', borderTop: '1px solid var(--border-glass)', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          &copy; 2026 Clause-Guard. Legal-Grade Cloud Deployment Powered by Vercel & Supabase.
        </p>
      </footer>
    </main>
  );
}
