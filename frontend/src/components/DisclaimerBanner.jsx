import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-500/10 border-b border-amber-200/80 px-4 py-2.5 text-xs sm:text-sm text-amber-900">
      <div className="max-w-7xl mx-auto flex items-center justify-center sm:justify-start gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <span>
          <strong>Educational & Preliminary Screening Tool:</strong> Not a substitute for professional medical diagnosis or clinical judgment.
        </span>
      </div>
    </div>
  );
}
