import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header className="glass" style={{ position: 'sticky', top: 0, zIndex: 100, padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' }}></div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Clause<span className="gradient-text">Guard</span></h1>
          </div>
          <nav style={{ display: 'flex', gap: '2rem' }}>
            <Link href="#features" style={{ color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.3s' }}>Features</Link>
            <Link href="#how-it-works" style={{ color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.3s' }}>How it Works</Link>
            <Link href="#legal-statutes" style={{ color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.3s' }}>Legal Database</Link>
          </nav>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link href="/auth/login" className="btn-secondary" style={{ textDecoration: 'none' }}>Login</Link>
            <Link href="/analyze" className="btn-primary" style={{ textDecoration: 'none' }}>Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{ flex: 1, display: 'flex', alignItems: 'center', padding: '6rem 0', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%)', filter: 'blur(60px)' }}></div>
        <div style={{ position: 'absolute', bottom: '-10%', left: '-10%', width: '400px', height: '400px', background: 'radial-gradient(circle, rgba(14, 165, 233, 0.1) 0%, transparent 70%)', filter: 'blur(50px)' }}></div>
        
        <div className="container" style={{ textAlign: 'center', position: 'relative', zIndex: 1, maxWidth: '800px' }}>
          <span className="animate-fade-in" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-primary)', padding: '0.5rem 1.25rem', borderRadius: '100px', fontSize: '0.875rem', fontWeight: '600', marginBottom: '1.5rem', display: 'inline-block' }}>
            AI-Powered Rental Protection
          </span>
          <h1 className="animate-fade-in" style={{ fontSize: '4.5rem', lineHeight: '1.1', marginBottom: '2rem', fontWeight: 'bold' }}>
            Bridge the <span className="gradient-text">Information Gap</span> between landlords and tenants.
          </h1>
          <p className="animate-fade-in" style={{ fontSize: '1.25rem', color: 'var(--text-muted)', marginBottom: '3rem', maxWidth: '600px', marginInline: 'auto' }}>
            Identify predatory or illegal clauses in lease agreements using jurisdictional RAG analysis. Analysis grounded in Indian Tenancy Laws.
          </p>
          <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
            <Link href="/analyze" className="btn-primary" style={{ fontSize: '1.1rem', padding: '1rem 2.5rem', textDecoration: 'none' }}>Analyze Your Lease</Link>
            <Link href="#how-it-works" className="btn-secondary" style={{ fontSize: '1.1rem', padding: '1rem 2.5rem', textDecoration: 'none' }}>See How It Works</Link>
          </div>
        </div>
      </section>

      {/* Trust & Modernity Stats */}
      <section style={{ backgroundColor: 'var(--bg-surface)', padding: '4rem 0', borderTop: '1px solid var(--border-glass)' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', textAlign: 'center' }}>
          <div>
            <h3 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-main)' }}>100%</h3>
            <p style={{ color: 'var(--text-muted)' }}>Indian Statutes Context</p>
          </div>
          <div>
            <h3 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-main)' }}>85%+</h3>
            <p style={{ color: 'var(--text-muted)' }}>Semantic Accuracy</p>
          </div>
          <div>
            <h3 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--text-main)' }}>&lt;15s</h3>
            <p style={{ color: 'var(--text-muted)' }}>Rapid Legal Analysis</p>
          </div>
        </div>
      </section>

      {/* Footer (Simplified) */}
      <footer style={{ padding: '3rem 0', borderTop: '1px solid var(--border-glass)', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>&copy; 2026 Clause-Guard. Dedicated to tenant rights in India.</p>
      </footer>
    </main>
  );
}
