import React, { useState, useMemo } from 'react';
import {
  Search,
  Check,
  X,
  AlertTriangle,
  Stethoscope,
  Activity,
  Filter,
  Trash2,
  ArrowRight,
  ShieldAlert,
  Loader2,
  Info
} from 'lucide-react';

export default function Assessment({
  symptomsData,
  loadingSymptoms,
  symptomsError,
  onSubmitAssessment,
  isPredicting
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [validationError, setValidationError] = useState('');

  // Extract categories list
  const categories = useMemo(() => {
    if (!symptomsData?.categories) return [];
    return symptomsData.categories.map((c) => c.category);
  }, [symptomsData]);

  // Filter symptoms based on search term and category
  const filteredSymptoms = useMemo(() => {
    if (!symptomsData) return [];

    let list = [];
    if (selectedCategory === 'ALL') {
      list = symptomsData.flat_list || [];
    } else {
      const cat = symptomsData.categories.find((c) => c.category === selectedCategory);
      list = cat ? cat.symptoms : [];
    }

    if (!searchTerm.trim()) return list;

    const query = searchTerm.toLowerCase().trim();
    return list.filter(
      (s) =>
        s.name.toLowerCase().includes(query) ||
        s.id.toLowerCase().includes(query)
    );
  }, [symptomsData, selectedCategory, searchTerm]);

  // Toggle symptom selection
  const toggleSymptom = (symptomId) => {
    setValidationError('');
    setSelectedSymptoms((prev) => {
      if (prev.includes(symptomId)) {
        return prev.filter((id) => id !== symptomId);
      } else {
        return [...prev, symptomId];
      }
    });
  };

  // Clear all selections
  const clearAll = () => {
    setSelectedSymptoms([]);
    setValidationError('');
  };

  // Form submission handler
  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedSymptoms.length === 0) {
      setValidationError('Please select at least one symptom to evaluate.');
      return;
    }
    setValidationError('');
    onSubmitAssessment(selectedSymptoms);
  };

  // Check if any selected symptom is an emergency flag
  const selectedEmergencySymptoms = useMemo(() => {
    if (!symptomsData?.flat_list) return [];
    return selectedSymptoms.filter((id) => {
      const found = symptomsData.flat_list.find((s) => s.id === id);
      return found?.is_emergency;
    });
  }, [selectedSymptoms, symptomsData]);

  if (loadingSymptoms) {
    return (
      <div className="max-w-4xl mx-auto py-24 text-center space-y-4">
        <Loader2 className="w-10 h-10 text-brand-600 animate-spin mx-auto" />
        <h3 className="text-lg font-bold text-slate-800">Loading Clinical Symptom Catalog...</h3>
        <p className="text-slate-500 text-sm">Fetching 131 standardized symptoms from backend...</p>
      </div>
    );
  }

  if (symptomsError) {
    return (
      <div className="max-w-xl mx-auto my-12 bg-rose-50 border border-rose-200 rounded-2xl p-6 text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-rose-600 mx-auto" />
        <h3 className="text-lg font-bold text-rose-900">Failed to Load Symptoms</h3>
        <p className="text-rose-700 text-sm">{symptomsError}</p>
        <p className="text-xs text-slate-500">Ensure the Flask backend API is running on port 5000.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 text-brand-700 text-xs font-semibold border border-brand-200 mb-2">
              <Stethoscope className="w-3.5 h-3.5" />
              <span>Diagnostic Symptom Assessment</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Select Your Symptoms
            </h1>
            <p className="text-slate-600 text-sm sm:text-base">
              Choose all symptoms you are currently experiencing. For the most accurate differential probabilities, select at least 3 symptoms.
            </p>
          </div>

          {/* Quick Counter */}
          <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 px-4 py-2.5 rounded-2xl flex-shrink-0">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">Selected:</span>
            <span className="text-xl font-black text-brand-600">{selectedSymptoms.length}</span>
            {selectedSymptoms.length > 0 && (
              <button
                type="button"
                onClick={clearAll}
                className="text-xs text-rose-600 hover:text-rose-800 font-semibold ml-2 underline"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Emergency Flag Warning within Assessment */}
        {selectedEmergencySymptoms.length > 0 && (
          <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 flex items-start gap-3 text-rose-900 text-sm animate-fadeIn">
            <ShieldAlert className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold">Potentially Severe Symptoms Selected!</span>
              <p className="text-xs text-rose-800 leading-relaxed">
                You have chosen symptoms associated with urgent medical conditions (such as chest pain, breathlessness, or neurological deficits). If you are experiencing sudden, sharp pain or severe breathing difficulty, please call emergency services immediately.
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Symptom Picker */}
        <div className="lg:col-span-8 space-y-6">
          {/* Search Bar & Filter Controls */}
          <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-4">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search symptoms (e.g., headache, cough, fever, nausea, chest pain)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-10 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm placeholder-slate-400"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Category Tabs */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
              <button
                type="button"
                onClick={() => setSelectedCategory('ALL')}
                className={`px-3 py-1.5 rounded-lg font-semibold whitespace-nowrap transition ${
                  selectedCategory === 'ALL'
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All ({symptomsData?.total_count || 131})
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg font-semibold whitespace-nowrap transition ${
                    selectedCategory === cat
                      ? 'bg-brand-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Symptoms Grid */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 pb-2 border-b border-slate-100">
              <span>Showing {filteredSymptoms.length} symptoms</span>
              <span>Click to toggle selection</span>
            </div>

            {filteredSymptoms.length === 0 ? (
              <div className="py-12 text-center text-slate-500 space-y-2">
                <Search className="w-8 h-8 mx-auto text-slate-300" />
                <p className="font-semibold text-slate-700">No matching symptoms found</p>
                <p className="text-xs">Try searching for a different keyword or switch category filters.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-[550px] overflow-y-auto pr-2">
                {filteredSymptoms.map((sym) => {
                  const isSelected = selectedSymptoms.includes(sym.id);
                  return (
                    <button
                      key={sym.id}
                      type="button"
                      onClick={() => toggleSymptom(sym.id)}
                      className={`text-left p-3 rounded-xl border text-xs sm:text-sm font-medium transition-all flex items-start justify-between gap-2 group ${
                        isSelected
                          ? 'bg-brand-50/90 border-brand-500 text-brand-900 shadow-sm ring-1 ring-brand-400'
                          : 'bg-slate-50/50 border-slate-200 hover:border-slate-300 hover:bg-slate-100/80 text-slate-700'
                      }`}
                    >
                      <div className="space-y-1">
                        <span className="leading-snug block font-semibold">{sym.name}</span>
                        {sym.is_emergency && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
                            <ShieldAlert className="w-2.5 h-2.5" />
                            Red Flag
                          </span>
                        )}
                      </div>
                      <div
                        className={`w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5 transition ${
                          isSelected
                            ? 'bg-brand-600 text-white'
                            : 'border border-slate-300 group-hover:border-slate-400'
                        }`}
                      >
                        {isSelected && <Check className="w-3.5 h-3.5" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Selected Summary & Submission */}
        <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-24">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-2">
                <Activity className="w-4 h-4 text-brand-600" />
                Assessment Summary
              </h3>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-100 text-brand-700">
                {selectedSymptoms.length} Selected
              </span>
            </div>

            {/* Selected tags container */}
            {selectedSymptoms.length === 0 ? (
              <div className="p-6 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-center text-xs text-slate-500 space-y-2">
                <Stethoscope className="w-6 h-6 text-slate-400 mx-auto" />
                <p className="font-medium text-slate-700">No symptoms selected yet</p>
                <p>Click symptoms from the list to add them to your analysis.</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Selected Symptoms:</span>
                  <button
                    type="button"
                    onClick={clearAll}
                    className="text-rose-600 hover:text-rose-800 font-semibold"
                  >
                    Remove All
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto pr-1">
                  {selectedSymptoms.map((symId) => {
                    const found = symptomsData?.flat_list?.find((s) => s.id === symId);
                    const name = found ? found.name : symId.replace(/_/g, ' ');
                    return (
                      <span
                        key={symId}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-brand-50 text-brand-800 border border-brand-200"
                      >
                        <span>{name}</span>
                        <button
                          type="button"
                          onClick={() => toggleSymptom(symId)}
                          className="text-brand-600 hover:text-brand-900"
                          aria-label={`Remove ${name}`}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Validation Notice or Alert */}
            {validationError && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-800 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                <span>{validationError}</span>
              </div>
            )}

            {selectedSymptoms.length > 0 && selectedSymptoms.length < 3 && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start gap-2">
                <Info className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>
                  Tip: Selecting 3 or more symptoms helps the model differentiate between conditions that share general symptoms (e.g. fever or fatigue).
                </span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isPredicting || selectedSymptoms.length === 0}
              className={`w-full py-4 rounded-2xl font-bold text-sm shadow-lg transition flex items-center justify-center gap-2 ${
                isPredicting || selectedSymptoms.length === 0
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                  : 'bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-700 hover:to-teal-700 text-white shadow-brand-600/30 hover:shadow-brand-600/50 hover:-translate-y-0.5'
              }`}
            >
              {isPredicting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Evaluating Random Forest Ensembles...</span>
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5" />
                  <span>Analyze Symptoms with AI</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>

            {/* Trust and Privacy info */}
            <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400 space-y-1">
              <p>&bull; Prediction runs locally on Random Forest model (100 estimators).</p>
              <p>&bull; No personal identity or clinical record is stored.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
