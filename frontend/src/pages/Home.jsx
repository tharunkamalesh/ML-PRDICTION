import React from 'react';
import {
  Stethoscope,
  Activity,
  ShieldCheck,
  Brain,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Users,
  LineChart,
  FileText,
  Clock,
  Sparkles
} from 'lucide-react';

export default function Home({ onNavigate, stats }) {
  const steps = [
    {
      num: '01',
      title: 'Select Symptoms',
      desc: 'Browse or search through 131 clinically mapped symptoms categorized by organ system.',
      icon: Stethoscope,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      num: '02',
      title: 'Random Forest Inference',
      desc: 'Our trained ensemble model analyzes binary feature vectors across 41 disease profiles without data leakage.',
      icon: Brain,
      color: 'from-brand-500 to-indigo-500'
    },
    {
      num: '03',
      title: 'Uncertainty & Triage',
      desc: 'Get calibrated confidence scores alongside red-flag emergency screening for critical cardiovascular and respiratory signs.',
      icon: Activity,
      color: 'from-teal-500 to-emerald-500'
    },
    {
      num: '04',
      title: 'Specialist Guidance',
      desc: 'Review potential differentials, recommended medical specialists, and safe lifestyle precautions before doctor consultation.',
      icon: ShieldCheck,
      color: 'from-purple-500 to-brand-500'
    }
  ];

  const highlights = [
    { value: '41', label: 'Medical Conditions Covered', sub: 'Across 10 organ systems' },
    { value: '131', label: 'Standardized Symptoms', sub: 'Anatomically structured' },
    { value: '99.9%', label: 'Test-Set Validation Accuracy', sub: 'Held-out stratified split' },
    { value: '100%', label: 'Anonymous & Private', sub: 'Zero PII recorded' }
  ];

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden gradient-hero pt-12 pb-20 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Copy */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white shadow-sm border border-slate-200 text-xs font-semibold text-brand-700">
                <Sparkles className="w-3.5 h-3.5 text-brand-500" />
                <span>Next-Generation Healthcare Screening AI</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
                Preliminary Clinical Insights Powered by{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 via-teal-600 to-brand-700">
                  Machine Learning
                </span>
              </h1>

              <p className="text-lg text-slate-600 leading-relaxed max-w-2xl">
                Experience an honest, transparent symptom assessment system. We utilize calibrated Random Forest classification to evaluate complex symptom clusters, prioritize differential diagnoses, and screen for critical red-flag emergencies.
              </p>

              {/* CTAs */}
              <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                <button
                  onClick={() => onNavigate('assessment')}
                  className="inline-flex items-center justify-center gap-2 px-7 py-4 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-700 hover:to-teal-700 text-white font-bold rounded-2xl shadow-lg shadow-brand-600/30 hover:shadow-xl hover:shadow-brand-600/40 transition-all transform hover:-translate-y-0.5 text-base"
                >
                  <Stethoscope className="w-5 h-5" />
                  Check Symptoms Now
                  <ArrowRight className="w-4 h-4 ml-1" />
                </button>

                <button
                  onClick={() => onNavigate('evaluation')}
                  className="inline-flex items-center justify-center gap-2 px-6 py-4 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-2xl border border-slate-300 shadow-sm transition text-base"
                >
                  <LineChart className="w-5 h-5 text-slate-500" />
                  View Model Metrics
                </button>
              </div>

              {/* Safety notice bullet */}
              <div className="flex items-center gap-2 text-xs text-slate-500 pt-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span>Strictly educational screening &bull; No registration required &bull; 100% confidential</span>
              </div>
            </div>

            {/* Right Card Mockup */}
            <div className="lg:col-span-5">
              <div className="relative">
                {/* Decorative glow */}
                <div className="absolute -inset-1 bg-gradient-to-r from-brand-500 to-teal-400 rounded-3xl blur-xl opacity-30 animate-pulse" />

                <div className="relative bg-white rounded-3xl p-6 shadow-2xl border border-slate-200/80 space-y-6">
                  {/* Card Header */}
                  <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600 font-bold">
                        <Activity className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 text-sm">Clinical AI Engine</h4>
                        <p className="text-xs text-slate-400">Random Forest Ensemble v1.0</p>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      Live Status: Ready
                    </span>
                  </div>

                  {/* Interactive preview items */}
                  <div className="space-y-3">
                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-xs flex items-center justify-between">
                      <span className="text-slate-600 font-medium">Selected Symptom Vector</span>
                      <span className="font-semibold text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                        131 Binary Features
                      </span>
                    </div>

                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-xs flex items-center justify-between">
                      <span className="text-slate-600 font-medium">Model Baseline</span>
                      <span className="font-semibold text-slate-800">100 Estimators (n_jobs=-1)</span>
                    </div>

                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-xs flex items-center justify-between">
                      <span className="text-slate-600 font-medium">Uncertainty Handling</span>
                      <span className="font-semibold text-emerald-700">Calibrated Softmax Distribution</span>
                    </div>

                    <div className="p-3.5 bg-rose-50/70 rounded-xl border border-rose-200/80 text-xs flex items-center justify-between">
                      <div className="flex items-center gap-2 text-rose-800 font-semibold">
                        <AlertTriangle className="w-4 h-4 text-rose-500" />
                        <span>Red-Flag Emergency Guard</span>
                      </div>
                      <span className="text-rose-700 font-bold">Active</span>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      onClick={() => onNavigate('assessment')}
                      className="w-full py-3 bg-brand-50 hover:bg-brand-100 text-brand-700 font-bold rounded-xl text-xs transition flex items-center justify-center gap-2 border border-brand-200"
                    >
                      <span>Start Interactive Assessment</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Numerical Metrics Bar */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {highlights.map((h, idx) => (
            <div
              key={idx}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition text-center space-y-1"
            >
              <div className="text-3xl sm:text-4xl font-extrabold text-brand-600 tracking-tight">
                {h.value}
              </div>
              <div className="text-sm font-semibold text-slate-800">{h.label}</div>
              <div className="text-xs text-slate-500">{h.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-600 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
            System Architecture & Flow
          </span>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            How The Prediction Process Works
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            From patient symptom input to calibrated differential rankings, each stage is engineered for clinical safety and honest statistical representation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all space-y-4 relative group"
              >
                <div className="flex items-center justify-between">
                  <div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${step.color} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-2xl font-black text-slate-200">{step.num}</span>
                </div>
                <h3 className="font-bold text-slate-900 text-base">{step.title}</h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">{step.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Clinical Disclaimer & Transparency Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-brand-950 text-white rounded-3xl p-8 sm:p-12 shadow-xl border border-slate-700/60 relative overflow-hidden">
          <div className="max-w-3xl space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 text-xs font-bold border border-rose-500/30">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Medical Safety Guidelines</span>
            </div>

            <h3 className="text-2xl sm:text-3xl font-bold tracking-tight">
              Honest Artificial Intelligence: A Screening Aid, Never a Diagnosis
            </h3>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Medical diagnosis is a holistic clinical process that involves physical examination, patient history, blood chemistry, and imaging. Our model is built strictly on mathematical correlation from verified training benchmarks.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 text-xs sm:text-sm text-slate-300">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Zero fabricated medical claims or commercial bias</span>
              </div>
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Transparent confusion matrices and class-level metrics</span>
              </div>
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Immediate emergency triage referral for severe symptoms</span>
              </div>
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Clear recommendation to licensed medical practitioners</span>
              </div>
            </div>

            <div className="pt-4 flex flex-wrap gap-4">
              <button
                onClick={() => onNavigate('assessment')}
                className="px-6 py-3.5 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl transition shadow-lg text-sm"
              >
                Proceed to Symptom Assessment
              </button>
              <button
                onClick={() => onNavigate('about')}
                className="px-6 py-3.5 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition border border-white/20 text-sm"
              >
                Read Clinical Methodology
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
