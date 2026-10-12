import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  PhoneCall,
  UserCheck,
  Stethoscope,
  Activity,
  ArrowLeft,
  ShieldCheck,
  HelpCircle,
  FileCheck2,
  LineChart,
  Info
} from 'lucide-react';

export default function Results({ result, onReset, onNavigate }) {
  if (!result) {
    return (
      <div className="max-w-xl mx-auto my-16 text-center space-y-4">
        <Activity className="w-12 h-12 text-slate-400 mx-auto" />
        <h3 className="text-xl font-bold text-slate-800">No Assessment Results Available</h3>
        <p className="text-slate-500 text-sm">Please select symptoms to view preliminary machine learning predictions.</p>
        <button
          onClick={onReset}
          className="px-6 py-2.5 bg-brand-600 text-white font-semibold rounded-xl text-sm"
        >
          Go to Symptom Assessment
        </button>
      </div>
    );
  }

  const {
    primary_prediction,
    uncertainty,
    top_differential_diagnoses,
    emergency_alert,
    selected_symptoms_processed,
    symptom_count,
    disclaimer
  } = result;

  const isEmergency = emergency_alert && emergency_alert.triggered;

  // Determine uncertainty badge styling
  const getUncertaintyBadge = (level) => {
    switch (level) {
      case 'Low':
        return {
          bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
          dot: 'bg-emerald-500',
          label: 'Low Statistical Uncertainty'
        };
      case 'Moderate':
        return {
          bg: 'bg-amber-50 text-amber-800 border-amber-200',
          dot: 'bg-amber-500',
          label: 'Moderate Statistical Uncertainty'
        };
      default:
        return {
          bg: 'bg-rose-50 text-rose-800 border-rose-200',
          dot: 'bg-rose-500',
          label: 'High Statistical Uncertainty'
        };
    }
  };

  const uncBadge = getUncertaintyBadge(uncertainty?.level || 'Moderate');

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Navigation / Reset Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-brand-600 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Modify Symptoms & Re-evaluate</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('evaluation')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-xs font-semibold text-slate-700 transition"
          >
            <LineChart className="w-3.5 h-3.5 text-brand-600" />
            <span>Verify Model Validation Metrics</span>
          </button>
          <span className="text-xs text-slate-400">
            Assessed: {symptom_count} Symptoms
          </span>
        </div>
      </div>

      {/* Emergency Callout (if active) */}
      {isEmergency && (
        <div className="bg-rose-600 text-white rounded-3xl p-6 sm:p-8 shadow-xl border-2 border-rose-400 animate-fadeIn space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center flex-shrink-0">
              <AlertOctagon className="w-7 h-7 text-white animate-pulse" />
            </div>
            <div>
              <span className="text-xs uppercase tracking-widest font-black text-rose-200">
                CRITICAL TRIAGE ALERT
              </span>
              <h2 className="text-2xl font-black">Urgent Medical Attention Required</h2>
            </div>
          </div>

          <p className="text-rose-100 text-sm sm:text-base leading-relaxed">
            {emergency_alert.advisory}
          </p>

          <div className="bg-white/10 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="text-xs space-y-1">
              <span className="font-bold text-white">Emergency Red-Flag Symptoms Present:</span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {emergency_alert.detected_symptoms?.map((s, idx) => (
                  <span
                    key={idx}
                    className="bg-white text-rose-900 font-bold px-2 py-0.5 rounded text-xs"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <a
              href="tel:911"
              className="inline-flex items-center gap-2 px-5 py-3 bg-white text-rose-700 hover:bg-rose-50 font-black rounded-xl text-sm shadow-md transition"
            >
              <PhoneCall className="w-4 h-4" />
              Call Emergency (911 / 112)
            </a>
          </div>
        </div>
      )}

      {/* Primary Prediction Hero Card */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-md space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-700 bg-brand-50 px-2.5 py-1 rounded-md border border-brand-200">
                Primary Model Hypothesis
              </span>
              <span
                className={`text-xs font-bold px-2.5 py-1 rounded-md border ${
                  primary_prediction.severity.includes('CRITICAL')
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-teal-50 text-teal-700 border-teal-200'
                }`}
              >
                Severity: {primary_prediction.severity}
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {primary_prediction.disease}
            </h1>
            <p className="text-slate-600 text-sm max-w-2xl leading-relaxed">
              {primary_prediction.description}
            </p>
          </div>

          {/* Calibrated Probability Pill */}
          <div className="bg-gradient-to-br from-slate-50 to-brand-50/50 border border-brand-200 rounded-2xl p-5 text-center flex-shrink-0 min-w-[200px] space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Confidence Score
            </span>
            <div className="text-3xl sm:text-4xl font-black text-brand-600">
              {primary_prediction.confidence_percent}%
            </div>
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="bg-brand-500 h-full rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, primary_prediction.confidence_percent)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Uncertainty and Calibration Analysis */}
        <div className={`p-4 rounded-2xl border ${uncBadge.bg} flex items-start gap-3 text-xs sm:text-sm`}>
          <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
            <span className={`w-2.5 h-2.5 rounded-full ${uncBadge.dot}`} />
            <strong className="whitespace-nowrap">{uncBadge.label}:</strong>
          </div>
          <span className="leading-relaxed">{uncertainty?.explanation}</span>
        </div>

        {/* Recommended Specialist & Clinical Precautions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Specialist card */}
          <div className="p-5 rounded-2xl bg-teal-50/50 border border-teal-200 space-y-3">
            <div className="flex items-center gap-2.5 text-teal-800 font-bold text-sm">
              <UserCheck className="w-5 h-5 text-teal-600" />
              <span>Recommended Medical Specialist</span>
            </div>
            <p className="text-slate-700 text-base font-extrabold">
              {primary_prediction.specialist}
            </p>
            <p className="text-xs text-slate-600 leading-relaxed">
              If your symptoms persist, consult a certified {primary_prediction.specialist} for complete laboratory diagnosis, clinical imaging, and treatment.
            </p>
          </div>

          {/* Precautions card */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center gap-2.5 text-slate-800 font-bold text-sm">
              <FileCheck2 className="w-5 h-5 text-brand-600" />
              <span>General Lifestyle & Clinical Precautions</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-700">
              {primary_prediction.precautions?.map((p, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Differential Diagnoses Comparison Table / Cards */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Activity className="w-5 h-5 text-brand-600" />
              Top Differential Diagnoses
            </h3>
            <p className="text-xs text-slate-500">
              Random Forest probability distribution across other plausible candidate conditions.
            </p>
          </div>
          <span className="text-xs font-semibold text-slate-500">
            Top {top_differential_diagnoses?.length} Ranked Conditions
          </span>
        </div>

        <div className="space-y-3">
          {top_differential_diagnoses?.map((item, idx) => {
            const isTop = idx === 0;
            return (
              <div
                key={idx}
                className={`p-4 rounded-2xl border transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                  isTop
                    ? 'bg-brand-50/50 border-brand-300 ring-1 ring-brand-200'
                    : 'bg-slate-50/50 border-slate-200 hover:bg-slate-100/50'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[11px] flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">{item.disease}</h4>
                    {isTop && (
                      <span className="text-[10px] font-bold bg-brand-600 text-white px-2 py-0.5 rounded">
                        Top Prediction
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500">
                    Consult: <span className="font-semibold text-slate-700">{item.specialist}</span> &bull; Severity: <span className="font-semibold text-slate-700">{item.severity}</span>
                  </p>
                </div>

                <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                  <div className="w-32 bg-slate-200 h-2.5 rounded-full overflow-hidden hidden sm:block">
                    <div
                      className={`h-full rounded-full ${
                        isTop ? 'bg-brand-600' : 'bg-slate-400'
                      }`}
                      style={{ width: `${Math.min(100, item.confidence_percent)}%` }}
                    />
                  </div>
                  <span className="font-black text-sm text-slate-900 w-16 text-right">
                    {item.confidence_percent}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Evaluated Symptoms Audit */}
      <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 text-xs text-slate-600 space-y-2">
        <span className="font-bold text-slate-800 block">Evaluated Symptom Profile:</span>
        <div className="flex flex-wrap gap-1.5">
          {selected_symptoms_processed?.map((s, idx) => (
            <span
              key={idx}
              className="bg-white border border-slate-200 px-2.5 py-1 rounded-md text-slate-700 font-medium"
            >
              {s}
            </span>
          ))}
        </div>
      </div>

      {/* Crucial Medical Disclaimer Card */}
      <div className="bg-amber-500/10 border-2 border-amber-300 rounded-3xl p-6 sm:p-8 space-y-3">
        <div className="flex items-center gap-3 text-amber-900 font-extrabold text-base">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <span>MANDATORY CLINICAL & REGULATORY DISCLAIMER</span>
        </div>
        <p className="text-amber-950 text-xs sm:text-sm leading-relaxed">
          {disclaimer}
        </p>
        <p className="text-amber-900/80 text-xs leading-relaxed">
          Under no circumstances should this tool be used to self-prescribe pharmaceuticals, adjust existing medication dosages, or ignore advice from your personal physician. If symptoms worsen, seek professional medical care immediately.
        </p>
      </div>

      {/* Bottom Action CTAs */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
        <button
          onClick={onReset}
          className="w-full sm:w-auto px-6 py-3.5 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl transition shadow-md shadow-brand-600/20 text-sm"
        >
          Perform Another Assessment
        </button>

        <button
          onClick={() => onNavigate('evaluation')}
          className="w-full sm:w-auto px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-xl border border-slate-300 transition text-sm flex items-center justify-center gap-2"
        >
          <LineChart className="w-4 h-4 text-brand-600" />
          <span>Inspect Model Metrics & Confusion Matrix</span>
        </button>
      </div>
    </div>
  );
}
