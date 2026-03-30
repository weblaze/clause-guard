'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { auth } from '@/lib/firebase';
import { onAuthStateChanged, signInWithPopup, GoogleAuthProvider, signOut, User } from 'firebase/auth';

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error("Error signing in with Google:", error);
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

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
            <Link href="#features" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Features</Link>
            <Link href="#how-it-works" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>How it Works</Link>
          </nav>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {loading ? (
              <div className="animate-spin" style={{ width: '20px', height: '20px', border: '2px solid var(--text-muted)', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
            ) : user ? (
              <>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{user.displayName}</span>
                <button onClick={logout} className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>Logout</button>
                <Link href="/analyze" className="btn-primary" style={{ textDecoration: 'none' }}>Dashboard</Link>
              </>
            ) : (
              <>
                <button onClick={loginWithGoogle} className="btn-secondary">Login</button>
                <Link href="/analyze" className="btn-primary" style={{ textDecoration: 'none' }}>Get Started</Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{ flex: 1, display: 'flex', alignItems: 'center', padding: '6rem 0', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%)', filter: 'blur(60px)' }}></div>
        <div className="container" style={{ textAlign: 'center', position: 'relative', zIndex: 1, maxWidth: '800px' }}>
          <h1 className="animate-fade-in" style={{ fontSize: '4.5rem', lineHeight: '1.1', marginBottom: '2rem', fontWeight: 'bold' }}>
            Bridge the <span className="gradient-text">Information Gap</span> between landlords and tenants.
          </h1>
          <p className="animate-fade-in" style={{ fontSize: '1.25rem', color: 'var(--text-muted)', marginBottom: '3rem', maxWidth: '600px', marginInline: 'auto' }}>
            Cloud-native lease analysis ground in Indian Law. Deploying secure, automated protection for every tenant.
          </p>
          <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem' }}>
            <Link href="/analyze" className="btn-primary" style={{ fontSize: '1.1rem', padding: '1rem 2.5rem', textDecoration: 'none' }}>Analyze Your Lease</Link>
            {!user && <button onClick={loginWithGoogle} className="btn-secondary" style={{ fontSize: '1.1rem', padding: '1rem 2.5rem' }}>Sign In with Google</button>}
          </div>
        </div>
      </section>

      <footer style={{ padding: '3rem 0', borderTop: '1px solid var(--border-glass)', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>&copy; 2026 Clause-Guard. Firebase Cloud Deployment Active.</p>
      </footer>
    </main>
  );
}
