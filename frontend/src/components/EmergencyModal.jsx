import React from 'react';
import { AlertOctagon, PhoneCall, X, ShieldAlert } from 'lucide-react';

export default function EmergencyModal({ isOpen, onClose, emergencyData }) {
  if (!isOpen || !emergencyData) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border-2 border-rose-500 overflow-hidden transform transition-all">
        {/* Header */}
        <div className="bg-rose-600 px-6 py-4 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <AlertOctagon className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-bold">EMERGENCY WARNING</h3>
              <p className="text-xs text-rose-100">Critical Symptoms Detected</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white rounded-lg p-1 transition"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-950 text-sm">
            <p className="font-semibold mb-2">High-Risk Red-Flag Symptoms Identified:</p>
            <div className="flex flex-wrap gap-2">
              {emergencyData.detected_symptoms?.map((s, idx) => (
                <span
                  key={idx}
                  className="bg-rose-600 text-white text-xs font-bold px-2.5 py-1 rounded-md tracking-wide"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          <p className="text-slate-700 text-sm leading-relaxed">
            {emergencyData.advisory ||
              'These symptoms can indicate acute cardiac, pulmonary, or cerebrovascular emergencies that require immediate clinical triage.'}
          </p>

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3 text-xs text-amber-900">
            <ShieldAlert className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Do not rely solely on artificial intelligence.</strong> Please bypass routine screening and contact emergency services or proceed to the nearest emergency department right away.
            </span>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex flex-col sm:flex-row gap-3">
            <a
              href="tel:911"
              className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl shadow-lg shadow-rose-600/30 transition text-center"
            >
              <PhoneCall className="w-5 h-5" />
              Call Emergency (911 / 112)
            </a>
            <button
              onClick={onClose}
              className="px-4 py-3 border border-slate-300 text-slate-700 hover:bg-slate-100 font-semibold rounded-xl text-sm transition"
            >
              I Understand, Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
