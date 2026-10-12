import React from 'react';
import { Stethoscope, ShieldCheck, Heart, ExternalLink, Activity } from 'lucide-react';

export default function Footer({ onNavigate }) {
  return (
    <footer className="bg-slate-900 text-slate-300 pt-12 pb-8 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand Col */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-500 to-teal-400 flex items-center justify-center text-white">
                <Stethoscope className="w-5 h-5" />
              </div>
              <span className="font-extrabold text-xl text-white tracking-tight">
                Health<span className="text-teal-400">AI</span> Systems
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-md leading-relaxed">
              An intelligent, transparent clinical screening tool powered by Random Forest classification. Built to provide preliminary symptom insights, highlight differential diagnosis probabilities, and detect red-flag medical emergencies.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-400 pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero PII Collection &bull; Privacy-Preserving Architecture &bull; Open Benchmark</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-3 uppercase tracking-wider">Navigation</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <button
                  onClick={() => onNavigate('home')}
                  className="hover:text-white transition"
                >
                  Home Landing
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('assessment')}
                  className="hover:text-white transition text-teal-400 font-medium"
                >
                  Check Symptoms
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('evaluation')}
                  className="hover:text-white transition"
                >
                  Model Evaluation & Metrics
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('dashboard')}
                  className="hover:text-white transition"
                >
                  Usage Dashboard & History
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('about')}
                  className="hover:text-white transition"
                >
                  Methodology & Disclaimer
                </button>
              </li>
            </ul>
          </div>

          {/* Clinical Resources & Hotline */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-3 uppercase tracking-wider">Clinical Safety</h4>
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700/80">
                <span className="text-rose-400 font-bold block mb-1">Emergency Services</span>
                <p className="text-slate-300">
                  Dial <strong>911</strong> (US/CA) or <strong>112</strong> (EU/Global) for sudden chest pain, stroke symptoms, or severe respiratory failure.
                </p>
              </div>
              <p className="text-slate-400 leading-relaxed">
                For educational screening demonstration only. Do not make diagnostic or pharmacological decisions without a certified medical doctor.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>&copy; {new Date().getFullYear()} AI-Based Disease Prediction System. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              Trained on 41 Classes &bull; 131 Clinical Symptoms
            </span>
            <span>Scikit-learn + React + Flask</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
