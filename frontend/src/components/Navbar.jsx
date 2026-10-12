import React, { useState } from 'react';
import { Activity, Stethoscope, BarChart3, Info, Shield, Menu, X, CheckCircle2 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, backendStatus }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Home', icon: Activity },
    { id: 'assessment', label: 'Check Symptoms', icon: Stethoscope },
    { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
    { id: 'dashboard', label: 'Dashboard & Privacy', icon: Shield },
    { id: 'about', label: 'About & Clinical Notice', icon: Info },
  ];

  const handleNavClick = (id) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div
            onClick={() => handleNavClick('home')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition">
              <Stethoscope className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 group-hover:text-brand-600 transition">
                  Health<span className="text-teal-600">AI</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-100 text-brand-700">
                  ML-v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">Disease Prediction System</p>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 shadow-sm border border-brand-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Right Action / System Status */}
          <div className="hidden sm:flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-600">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected' || backendStatus === 'healthy'
                    ? 'bg-emerald-500 animate-pulse'
                    : backendStatus === 'model_unavailable'
                    ? 'bg-amber-500'
                    : backendStatus === 'disconnected'
                    ? 'bg-rose-500'
                    : 'bg-amber-400 animate-pulse'
                }`}
              />
              <span>
                {backendStatus === 'connected' || backendStatus === 'healthy'
                  ? 'Connected'
                  : backendStatus === 'model_unavailable'
                  ? 'Model Unavailable'
                  : backendStatus === 'disconnected'
                  ? 'Disconnected'
                  : 'Connecting...'}
              </span>
            </div>
            {activeTab !== 'assessment' && (
              <button
                onClick={() => handleNavClick('assessment')}
                className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-700 hover:to-teal-700 text-white text-sm font-semibold rounded-xl shadow-md shadow-brand-600/20 hover:shadow-lg transition transform active:scale-95"
              >
                <Stethoscope className="w-4 h-4" />
                Check Symptoms
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-lg animate-fadeIn">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-base font-semibold ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 border border-brand-200'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-5 h-5 text-brand-600" />
                {item.label}
              </button>
            );
          })}
          <div className="pt-2">
            <button
              onClick={() => handleNavClick('assessment')}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-brand-600 text-white font-semibold rounded-xl shadow"
            >
              <Stethoscope className="w-5 h-5" />
              Check Symptoms Now
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
