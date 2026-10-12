import React from 'react';
import { AlertTriangle, PhoneCall } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-500/10 border-b border-amber-200/80 px-4 py-2.5 text-xs sm:text-sm text-amber-900">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>
            <strong>Educational & Preliminary Screening Tool:</strong> Not a substitute for professional medical diagnosis or clinical judgment.
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200">
          <PhoneCall className="w-3 h-3 text-rose-600" />
          <span>Experiencing severe distress? Call 911 / 112 immediately.</span>
        </div>
      </div>
    </div>
  );
}
