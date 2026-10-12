import React from 'react';
import {
  Info,
  ShieldAlert,
  Brain,
  Database,
  CheckCircle2,
  AlertTriangle,
  Stethoscope,
  Code2,
  FileText,
  Lock
} from 'lucide-react';

export default function About({ onNavigate }) {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 text-brand-700 text-xs font-semibold border border-brand-200">
          <Info className="w-3.5 h-3.5" />
          <span>Clinical Informatics & Ethical AI Principles</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          About the AI Disease Prediction System
        </h1>
        <p className="text-slate-600 text-base max-w-2xl mx-auto leading-relaxed">
          Designed to demonstrate how machine learning classifiers can empower health literacy, prioritize differential probabilities, and safeguard patients through automated emergency triage screening.
        </p>
      </div>

      {/* Core Methodology Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center text-brand-600 font-bold">
            <Brain className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Machine Learning Architecture</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            The prediction engine uses an ensemble <strong>Random Forest Classifier</strong> configured with 100 decision trees, Gini impurity split criterion, and balanced class weights. To ensure statistical integrity:
          </p>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span><strong>Held-Out Stratified Evaluation:</strong> 20% of data (984 records) is partitioned prior to training.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span><strong>Zero Data Leakage:</strong> Symptom vectors and classes are strictly isolated.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span><strong>Calibrated Probability Distribution:</strong> Softmax class probabilities are calculated for differential ranking.</span>
            </li>
          </ul>
        </div>

        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600 font-bold">
            <Database className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Dataset Provenance & Quality</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            The dataset models <strong>131 anatomical and physiological symptoms</strong> across <strong>41 acute and chronic medical conditions</strong>, covering cardiology, respiratory medicine, dermatology, neurology, endocrinology, gastroenterology, and infectious diseases.
          </p>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-700">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span>Balanced multi-class representation across all diagnostic categories.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span>Symptom co-occurrence noise modeling to simulate realistic patient variations.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span>Open, reproducible scripts in <code>dataset/prepare_dataset.py</code>.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Ethical AI Guarantees */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Lock className="w-5 h-5 text-brand-600" />
          Ethical AI & Transparency Principles
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-xs sm:text-sm">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
            <strong className="text-slate-900 block font-bold">1. Zero Fabrication Policy</strong>
            <p className="text-slate-600 leading-relaxed">
              We never fabricate model accuracy, validation numbers, or clinical certifications. All metrics shown are computed directly from Scikit-learn test outputs.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
            <strong className="text-slate-900 block font-bold">2. Honest Uncertainty</strong>
            <p className="text-slate-600 leading-relaxed">
              When few symptoms or ambiguous combinations are entered, the system openly reports &quot;Moderate&quot; or &quot;High&quot; statistical uncertainty rather than false certainty.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
            <strong className="text-slate-900 block font-bold">3. No Pharmacological Prescriptions</strong>
            <p className="text-slate-600 leading-relaxed">
              The application never prescribes drugs or antibiotics. It only provides general lifestyle precautions and recommends the appropriate medical specialist.
            </p>
          </div>
        </div>
      </div>

      {/* Full Medical Disclaimer Callout */}
      <div className="bg-rose-50 border-2 border-rose-300 rounded-3xl p-6 sm:p-8 space-y-4">
        <div className="flex items-center gap-3 text-rose-900 font-extrabold text-base">
          <ShieldAlert className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <span>LEGAL & MEDICAL DISCLAIMER</span>
        </div>
        <p className="text-rose-950 text-xs sm:text-sm leading-relaxed">
          The AI-Based Disease Prediction System is an educational and technological demonstrator. It does not provide clinical diagnoses, formal medical opinions, treatment protocols, or prescriptions.
        </p>
        <p className="text-rose-900/90 text-xs sm:text-sm leading-relaxed">
          If you are experiencing medical symptoms, consult a qualified physician or healthcare provider. If you or someone around you experiences severe symptoms—including crushing chest pain, sudden difficulty breathing, slurred speech, facial drooping, severe blood loss, or loss of consciousness—call your local emergency hotline (<strong>911</strong> / <strong>112</strong>) or visit the nearest emergency facility without delay.
        </p>
      </div>

      {/* CTA */}
      <div className="text-center pt-4">
        <button
          onClick={() => onNavigate('assessment')}
          className="px-8 py-4 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-700 hover:to-teal-700 text-white font-bold rounded-2xl shadow-lg shadow-brand-600/30 text-base transition transform hover:-translate-y-0.5"
        >
          Check Symptoms Now
        </button>
      </div>
    </div>
  );
}
