'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Upload, FileText, CheckCircle, AlertTriangle, ShieldCheck, ArrowLeft, Download } from 'lucide-react';

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [jurisdiction, setJurisdiction] = useState('Central');
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!file) return;
    setAnalyzing(true);
    
    // Simulate backend call (Replace with actual fetch later)
    const formData = new FormData();
    formData.append('file', file);
    formData.append('jurisdiction', jurisdiction);

    try {
      // Mocking response for visual progress setup
      setTimeout(() => {
        setReport({
          risk_score: 65,
          risk_category: 'HIGH',
          filename: file.name,
          clauses: [
            {
              original_text: "The security deposit shall be 5 months' rent, non-refundable upon early termination.",
              classification: 'ILLEGAL',
              explanation: "Under the Model Tenancy Act 2021, the security deposit for residential premises is capped at a maximum of 2 months' rent. Any excess is illegal.",
              statute_cited: "Model Tenancy Act 2021, Sec 11"
            },
            {
              original_text: "Landlord reserves the right to terminate the lease with 7 days' notice without assigning reasons.",
              classification: 'UNFAIR',
              explanation: "Commonly predatory. Standard notice periods are 3 months for rent revision and governed by fair eviction grounds.",
              statute_cited: "Model Tenancy Act 2021, Sec 21"
            },
            {
              original_text: "Tenant is responsible for structural repairs including roofing and outer wall painting.",
              classification: 'UNFAIR',
              explanation: "Structural repairs are typically the landlord's responsibility. Tenant responsibility is limited to routine maintenance.",
              statute_cited: "Model Tenancy Act 2021, Sec 15"
            }
          ]
        });
        setAnalyzing(false);
      }, 3000);
    } catch (err) {
      console.error(err);
      setAnalyzing(false);
    }
  };

  const getClassificationStyles = (type: string) => {
    switch (type) {
      case 'ILLEGAL': return { color: '#ef4444', icon: <AlertTriangle size={20} /> };
      case 'UNFAIR': return { color: '#fbbf24', icon: <AlertTriangle size={20} /> };
      default: return { color: '#10b981', icon: <ShieldCheck size={20} /> };
    }
  };

  if (report) {
    return (
      <main className="container animate-fade-in" style={{ padding: '4rem 2rem' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
          <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ArrowLeft size={18} /> Back to Home
          </Link>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={18} /> Download PDF
            </button>
            <button className="btn-primary" onClick={() => setReport(null)}>New Analysis</button>
          </div>
        </header>

        <section className="glass" style={{ padding: '3rem', borderRadius: '16px', marginBottom: '3rem', textAlign: 'center' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <span className="gradient-text" style={{ fontSize: '4.5rem', fontWeight: 'bold' }}>{report.risk_score}</span>
            <span style={{ fontSize: '1.5rem', marginLeft: '0.5rem', color: 'var(--text-gold)' }}>/ 100</span>
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Overall Risk: <span style={{ color: report.risk_category === 'HIGH' ? '#ef4444' : '#fbbf24' }}>{report.risk_category}</span></h2>
          <p style={{ color: 'var(--text-muted)' }}>We identified several concerns based on the Model Tenancy Act 2021 context.</p>
        </section>

        <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {report.clauses.map((clause: any, i: number) => {
            const styles = getClassificationStyles(clause.classification);
            return (
              <div key={i} className="glass" style={{ padding: '2rem', borderRadius: '12px', borderLeft: `4px solid ${styles.color}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                  {styles.icon}
                  <span style={{ color: styles.color, fontWeight: 'bold' }}>{clause.classification}</span>
                  <span style={{ color: 'var(--text-muted)', marginLeft: 'auto', fontSize: '0.875rem' }}>{clause.statute_cited}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                  <div>
                    <h4 style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Original Clause</h4>
                    <p style={{ fontStyle: 'italic', color: 'var(--text-main)' }}>"{clause.original_text}"</p>
                  </div>
                  <div>
                    <h4 style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Plain-English Explanation</h4>
                    <p style={{ color: 'var(--accent-gold)' }}>{clause.explanation}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </section>
      </main>
    );
  }

  return (
    <main className="container flex-center" style={{ minHeight: '100vh', padding: '4rem 2rem' }}>
      <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '600px', padding: '3rem', borderRadius: '24px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Ready to <span className="gradient-text">Guard</span>?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '3rem' }}>Upload your rental agreement (PDF) to identify predatory or illegal clauses ground in Indian Law.</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', marginBottom: '3rem' }}>
          <div style={{ textAlign: 'left' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Select Jurisdiction</label>
            <select 
              className="glass" 
              style={{ width: '100%', padding: '1rem', borderRadius: '12px', border: '1px solid var(--border-glass)', color: 'var(--text-main)', appearance: 'none' }}
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
            >
              <option value="Central">Central (Model Tenancy Act 2021)</option>
              <option value="Delhi">Delhi Rent Control Act</option>
              <option value="Maharashtra">Maharashtra Rent Control Act</option>
            </select>
          </div>

          <div 
            style={{ 
              border: '2px dashed var(--border-glass)', 
              borderRadius: '16px', 
              padding: '3rem 1.5rem', 
              cursor: 'pointer',
              transition: 'border-color 0.3s'
            }}
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            <input 
              id="file-upload" 
              type="file" 
              accept=".pdf" 
              style={{ display: 'none' }} 
              onChange={handleFileChange}
            />
            {file ? (
              <div className="flex-center" style={{ flexDirection: 'column', gap: '1rem' }}>
                <CheckCircle color="var(--accent-primary)" size={48} />
                <div>
                  <p style={{ fontWeight: '600' }}>{file.name}</p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
            ) : (
              <div className="flex-center" style={{ flexDirection: 'column', gap: '1rem' }}>
                <Upload color="var(--text-muted)" size={48} />
                <p style={{ color: 'var(--text-muted)' }}>Click or drag PDF to analyze</p>
              </div>
            )}
          </div>
        </div>

        <button 
          className="btn-primary" 
          style={{ width: '100%', fontSize: '1.1rem', padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}
          disabled={!file || analyzing}
          onClick={startAnalysis}
        >
          {analyzing ? (
            <>
              <div className="animate-spin" style={{ width: '20px', height: '20px', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
              Analyzing Agreement...
            </>
          ) : (
            <>
              <ShieldCheck size={20} />
              Start Legal Analysis
            </>
          )}
        </button>
      </div>
    </main>
  );
}
