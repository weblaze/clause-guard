'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { auth, storage, db } from '@/lib/firebase';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { onAuthStateChanged, User } from 'firebase/auth';
import { Upload, FileText, CheckCircle, AlertTriangle, ShieldCheck, ArrowLeft, Download, Loader2 } from 'lucide-react';

export default function AnalyzePage() {
  const [user, setUser] = useState<User | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [jurisdiction, setJurisdiction] = useState('Central');
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState('');
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!file || !user) return;
    setAnalyzing(true);
    setProgress('Uploading document to Cloud Storage...');

    try {
      // 1. Upload to Firebase Storage
      const storageRef = ref(storage, `uploads/${user.uid}/${Date.now()}_${file.name}`);
      const uploadResult = await uploadBytes(storageRef, file);
      const fileUrl = await getDownloadURL(uploadResult.ref);

      setProgress('Triggering AI Analysis (RAG + Ollama)...');

      // 2. Call Backend API (Assuming Cloud Run URL)
      // Note: In a real deploy, the URL would be environment-specific.
      // For now, we interact with the FastAPI backend Logic.
      
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          file_url: fileUrl, 
          userId: user.uid, 
          jurisdiction: jurisdiction 
        })
      });

      // MOCK BEHAVIOR FOR PROTOTYPE (Since backend URL is local)
      setTimeout(async () => {
        const mockReport = {
          risk_score: 72,
          risk_category: 'HIGH',
          filename: file.name,
          date: new Date().toLocaleDateString(),
          clauses: [
            {
              original_text: "Security deposit of 6 months required.",
              classification: 'ILLEGAL',
              explanation: "Under Model Tenancy Act 2021, deposit capped at 2 months.",
              statute: "Sec 11, MTA 2021"
            },
            {
              original_text: "Landlord ignores structural maintenance.",
              classification: 'UNFAIR',
              explanation: "Structural health is landlord's liability.",
              statute: "Sec 15, MTA 2021"
            }
          ]
        };

        // 3. Save Report to Firestore
        await addDoc(collection(db, 'reports'), {
          ...mockReport,
          userId: user.uid,
          createdAt: serverTimestamp()
        });

        setReport(mockReport);
        setAnalyzing(false);
      }, 3000);

    } catch (error) {
      console.error("Analysis Failed:", error);
      setAnalyzing(false);
      setProgress('Error occurred during analysis.');
    }
  };

  if (report) {
    return (
      <main className="container animate-fade-in" style={{ padding: '4rem 2rem' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
          <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ArrowLeft size={18} /> Back
          </Link>
          <button className="btn-primary" onClick={() => { setReport(null); setFile(null); }}>New Analysis</button>
        </header>

        <div className="glass" style={{ padding: '3rem', borderRadius: '24px', textAlign: 'center', borderBottom: '4px solid var(--accent-gold)' }}>
          <h2 style={{ fontSize: '3rem', fontWeight: '800' }}><span className="gradient-text">{report.risk_score}</span> <span style={{ fontSize: '1.25rem', color: 'var(--text-muted)' }}>/ 100</span></h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Overall Risk Assessment for <strong>{report.filename}</strong></p>
        </div>

        <section style={{ marginTop: '3rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {report.clauses.map((clause: any, index: number) => (
            <div key={index} className="glass animate-fade-in" style={{ padding: '2rem', borderRadius: '16px', borderLeft: `6px solid ${clause.classification === 'ILLEGAL' ? '#ef4444' : '#fbbf24'}` }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                {clause.classification === 'ILLEGAL' ? <AlertTriangle color="#ef4444" /> : <ShieldCheck color="#fbbf24" />}
                <span style={{ fontWeight: 'bold', color: clause.classification === 'ILLEGAL' ? '#ef4444' : '#fbbf24' }}>{clause.classification}</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>{clause.statute}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <p style={{ fontSize: '0.95rem', fontStyle: 'italic' }}>"{clause.original_text}"</p>
                <p style={{ color: 'var(--text-gold)', fontWeight: '500' }}>{clause.explanation}</p>
              </div>
            </div>
          ))}
        </section>
      </main>
    );
  }

  return (
    <main className="container flex-center" style={{ minHeight: '100vh', padding: '2rem' }}>
      <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '700px', padding: '4rem', borderRadius: '32px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '1.5rem', fontWeight: '800' }}>Legal <span className="gradient-text">Analysis</span> Cloud</h2>
        
        {!user ? (
          <div style={{ padding: '2rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <p style={{ color: '#ef4444', fontWeight: 'bold' }}>Authentication Required</p>
            <p style={{ color: 'var(--text-muted)' }}>Please sign in on the home page to use the analysis engine.</p>
            <Link href="/" className="btn-secondary" style={{ marginTop: '1rem', display: 'inline-block', textDecoration: 'none' }}>Go to Login</Link>
          </div>
        ) : (
          <>
            <div style={{ textAlign: 'left', marginBottom: '2.5rem' }}>
              <label style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 'bold', textTransform: 'uppercase', display: 'block', marginBottom: '0.5rem' }}>Region of Agreement</label>
              <select className="glass" style={{ width: '100%', padding: '1rem', color: 'white', border: '1px solid var(--border-glass)', borderRadius: '12px' }} value={jurisdiction} onChange={e => setJurisdiction(e.target.value)}>
                <option value="Central">Central (Model Tenancy Act 2021)</option>
                <option value="Delhi">Delhi Rent Control</option>
              </select>
            </div>

            <div 
              className="glass" 
              style={{ border: '2px dashed var(--border-glass)', padding: '4rem 2rem', borderRadius: '24px', cursor: 'pointer', marginBottom: '2rem' }}
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <input id="file-upload" type="file" accept=".pdf" style={{ display: 'none' }} onChange={handleFileChange} />
              {file ? (
                <div className="flex-center" style={{ flexDirection: 'column', gap: '1rem' }}>
                  <CheckCircle color="var(--accent-primary)" size={48} />
                  <p style={{ fontWeight: 'bold' }}>{file.name}</p>
                </div>
              ) : (
                <div className="flex-center" style={{ flexDirection: 'column', gap: '1rem' }}>
                  <Upload color="var(--text-muted)" size={48} />
                  <p style={{ color: 'var(--text-muted)' }}>Drop PDF for AI Clause Analysis</p>
                </div>
              )}
            </div>

            <p style={{ marginBottom: '2rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{progress}</p>

            <button className="btn-primary" style={{ width: '100%', padding: '1.25rem', fontSize: '1.2rem' }} disabled={!file || analyzing} onClick={startAnalysis}>
              {analyzing ? <Loader2 className="animate-spin" style={{ marginInline: 'auto' }} /> : 'Execute Cloud Analysis'}
            </button>
          </>
        )}
      </div>
    </main>
  );
}
