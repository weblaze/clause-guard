'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
import { Upload, FileText, CheckCircle, AlertTriangle, ShieldCheck, ArrowLeft, Download, Loader2, Gauge, Scale } from 'lucide-react';

export default function AnalyzePage() {
  const [user, setUser] = useState<any>(null);
  const [file, setFile] = useState<File | null>(null);
  const [jurisdiction, setJurisdiction] = useState('Central');
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState('');
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!file || !user) return;
    setAnalyzing(true);
    setProgress('Uploading document to Supabase Cloud...');

    try {
      // 1. Upload to Supabase Storage
      const filePath = `uploads/${user.id}/${Date.now()}_${file.name}`;
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('agreements')
        .upload(filePath, file);

      if (uploadError) throw uploadError;

      const { data: { publicUrl } } = supabase.storage
        .from('agreements')
        .getPublicUrl(filePath);

      setProgress('Triggering AI Analysis (Vercel Edge Engine)...');

      // MOCK BEHAVIOR FOR PROTOTYPE (Supabase Logic Simulation)
      setTimeout(async () => {
        const mockReport = {
          risk_score: 84,
          risk_category: 'CRITICAL',
          filename: file.name,
          clauses: [
            {
              title: "Security Deposit Cap",
              original_text: "The tenant shall provide a security deposit equivalent to 10 months' rent (INR 1,50,000).",
              classification: 'ILLEGAL',
              explanation: "Security deposits are capped at two months' rent under the Model Tenancy Act.",
              statute: "Section 11, MTA 2021",
              action: "Request reduction to 2 months rent."
            }
          ]
        };

        // 2. Save Report to Supabase Database
        const { data: reportData, error: reportError } = await supabase
          .from('reports')
          .insert([
            {
              user_id: user.id,
              filename: file.name,
              risk_score: mockReport.risk_score,
              risk_category: mockReport.risk_category,
              jurisdiction: jurisdiction,
              file_url: publicUrl
            }
          ])
          .select();

        if (reportError) throw reportError;

        // 3. Save granular clauses
        const reportId = reportData[0].id;
        const clausesToInsert = mockReport.clauses.map(c => ({
          report_id: reportId,
          ...c,
          remedy: c.action // mapping action to remedy
        }));

        const { error: clausesError } = await supabase
          .from('clauses')
          .insert(clausesToInsert);

        if (clausesError) throw clausesError;

        setReport(mockReport);
        setAnalyzing(false);
      }, 4000);

    } catch (error) {
      console.error("Analysis Failed:", error);
      setAnalyzing(false);
      setProgress('Error: Cloud analysis failed (Verify Supabase Bucket exists).');
    }
  };

  if (report) {
    return (
      <main className="container animate-fade-in" style={{ padding: '4rem 2rem' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4rem' }}>
          <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
            <ArrowLeft size={16} /> Exit Analysis
          </Link>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn-secondary" style={{ padding: '0.6rem 1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={16} /> Download Report
            </button>
            <button className="btn-primary" style={{ padding: '0.6rem 1.2rem' }} onClick={() => { setReport(null); setFile(null); }}>Analyze Another</button>
          </div>
        </header>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '3rem' }}>
          {/* Summary Card */}
          <aside>
            <div className="glass" style={{ padding: '2.5rem', borderRadius: '24px', position: 'sticky', top: '120px' }}>
              <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                <div style={{ position: 'relative', display: 'inline-block' }}>
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(16, 185, 129, 0.1)" strokeWidth="8" />
                    <circle 
                      cx="60" cy="60" r="54" fill="none" 
                      stroke="url(#gradient)" strokeWidth="8" 
                      strokeDasharray="339.292" 
                      strokeDashoffset={339.292 * (1 - report.risk_score / 100)} 
                      strokeLinecap="round" 
                      style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="var(--accent-primary)" />
                        <stop offset="100%" stopColor="var(--accent-secondary)" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                    <span style={{ fontSize: '2rem', fontWeight: '800' }}>{report.risk_score}</span>
                  </div>
                </div>
                <h3 style={{ fontSize: '1.5rem', marginTop: '1rem', fontWeight: 'bold' }}>Risk Index</h3>
                <p style={{ color: 'var(--accent-gold)', fontWeight: 'bold', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{report.risk_category}</p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="flex-center" style={{ justifyContent: 'space-between', fontSize: '0.9rem', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Jurisdiction</span>
                  <span style={{ fontWeight: '500' }}>{jurisdiction}</span>
                </div>
                <div className="flex-center" style={{ justifyContent: 'space-between', fontSize: '0.9rem', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Compliance</span>
                  <span style={{ fontWeight: '500', color: report.risk_score > 70 ? '#ef4444' : '#10b981' }}>
                    {report.risk_score > 70 ? 'LOW' : 'HIGH'}
                  </span>
                </div>
              </div>
            </div>
          </aside>

          {/* Clauses List */}
          <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '1rem' }}>Identified <span className="gradient-text">Clauses</span></h2>
            {report.clauses.map((clause: any, index: number) => (
              <div 
                key={index} 
                className="glass animate-fade-in" 
                style={{ 
                  padding: '2rem', 
                  borderRadius: '24px', 
                  borderLeft: `8px solid ${clause.classification === 'ILLEGAL' ? '#ef4444' : clause.classification === 'UNFAIR' ? '#fbbf24' : '#10b981'}`,
                  animationDelay: `${index * 0.1}s`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>{clause.title}</h4>
                    <span 
                      style={{ 
                        fontSize: '0.7rem', 
                        fontWeight: 'bold', 
                        padding: '0.25rem 0.75rem', 
                        borderRadius: '20px', 
                        background: clause.classification === 'ILLEGAL' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                        color: clause.classification === 'ILLEGAL' ? '#ef4444' : '#10b981',
                        border: `1px solid ${clause.classification === 'ILLEGAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`
                      }}
                    >
                      {clause.classification}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Ref Statute</span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)', fontWeight: '500' }}>{clause.statute}</span>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1px 1fr', gap: '2rem', alignItems: 'center' }}>
                  <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '16px' }}>
                    <label style={{ fontSize: '0.65rem', fontWeight: 'bold', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.75rem', display: 'block' }}>Original Text</label>
                    <p style={{ fontSize: '0.9rem', fontStyle: 'italic', lineHeight: '1.6' }}>"{clause.original_text}"</p>
                  </div>
                  <div style={{ height: '80%', background: 'var(--border-glass)' }}></div>
                  <div>
                    <label style={{ fontSize: '0.65rem', fontWeight: 'bold', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.75rem', display: 'block' }}>Legal Guidance</label>
                    <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: '1rem', lineHeight: '1.6' }}>{clause.explanation}</p>
                    <div style={{ padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                      <p style={{ fontSize: '0.85rem', color: 'var(--accent-primary)', fontWeight: '600' }}>Action: {clause.action}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="container flex-center" style={{ minHeight: '100vh', padding: '4rem 2rem' }}>
      <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '800px', padding: '5rem 4rem', borderRadius: '40px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '4px', background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-gold))' }}></div>
        
        <div style={{ display: 'inline-flex', padding: '1rem', borderRadius: '20px', background: 'rgba(16, 185, 129, 0.05)', marginBottom: '2rem' }}>
          <Scale size={40} className="gradient-text" />
        </div>
        
        <h2 style={{ fontSize: '3rem', marginBottom: '1rem', fontWeight: '900', letterSpacing: '-0.02em' }}>Clause<span className="gradient-text">Guard</span> Analysis</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginBottom: '3rem', maxWidth: '500px', marginInline: 'auto' }}>
          Upload your rental agreement PDF for a high-fidelity audit grounded in the Model Tenancy Act 2021.
        </p>
        
        {!user ? (
          <div style={{ padding: '2.5rem', background: 'rgba(239, 68, 68, 0.05)', borderRadius: '24px', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
            <p style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '0.5rem' }}>Cloud Access Restricted</p>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Secure cloud analysis requires an active legal session.</p>
            <Link href="/" className="btn-primary" style={{ textDecoration: 'none', padding: '0.8rem 2rem' }}>Return to Login</Link>
          </div>
        ) : (
          <div style={{ maxWidth: '500px', marginInline: 'auto' }}>
            <div style={{ textAlign: 'left', marginBottom: '2.5rem' }}>
              <label style={{ color: 'var(--text-muted)', fontSize: '0.7rem', fontWeight: '800', textTransform: 'uppercase', display: 'block', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>Deployment Jurisdiction</label>
              <select className="glass" style={{ width: '100%', padding: '1.25rem', color: 'white', border: '1px solid var(--border-glass)', borderRadius: '16px', appearance: 'none', cursor: 'pointer' }} value={jurisdiction} onChange={e => setJurisdiction(e.target.value)}>
                <option value="Central">India Central (MTA 2021)</option>
                <option value="Delhi">Delhi Rent Act (Special)</option>
                <option value="Maharashtra">Maharashtra Rent Control</option>
              </select>
            </div>

            <div 
              className="glass" 
              style={{ border: '2px dashed var(--border-glass)', padding: '5rem 2rem', borderRadius: '32px', cursor: 'pointer', marginBottom: '2.5rem', transition: 'all 0.3s ease' }}
              onMouseOver={e => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
              onMouseOut={e => e.currentTarget.style.borderColor = 'var(--border-glass)'}
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <input id="file-upload" type="file" accept=".pdf" style={{ display: 'none' }} onChange={handleFileChange} />
              {file ? (
                <div className="flex-center" style={{ flexDirection: 'column', gap: '1.25rem' }}>
                  <div style={{ padding: '1rem', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)' }}>
                    <CheckCircle color="var(--accent-primary)" size={40} />
                  </div>
                  <p style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{file.name}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Ready for processing</p>
                </div>
              ) : (
                <div className="flex-center" style={{ flexDirection: 'column', gap: '1.25rem' }}>
                  <Upload color="var(--text-muted)" size={40} />
                  <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Drop Document or Click to Upload</p>
                  <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.2)' }}>Supports PDF up to 10MB</p>
                </div>
              )}
            </div>

            <p style={{ marginBottom: '2rem', color: 'var(--accent-gold)', fontWeight: 'bold', fontSize: '0.85rem' }}>{progress}</p>

            <button className="btn-primary" style={{ width: '100%', padding: '1.4rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }} disabled={!file || analyzing} onClick={startAnalysis}>
              {analyzing ? <Loader2 className="animate-spin" /> : <Gauge size={24} />}
              {analyzing ? 'Processing Cloud Engine...' : 'Run Legal Audit'}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
