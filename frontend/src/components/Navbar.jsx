import React, { useState } from 'react';
import {
  Activity,
  Stethoscope,
  BarChart3,
  Info,
  Shield,
  Menu,
  X,
  User,
  LogOut,
  LogIn,
  UserPlus,
  ShieldAlert
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeTab, setActiveTab, backendStatus }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();

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

  const handleLogout = async () => {
    await logout();
    setActiveTab('home');
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
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
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

          {/* Right Action / Auth Controls */}
          <div className="hidden sm:flex items-center gap-2.5">
            {/* Status indicator */}
            <div className="flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-600">
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
              <span className="text-[11px]">
                {backendStatus === 'connected' || backendStatus === 'healthy'
                  ? 'Connected'
                  : backendStatus === 'model_unavailable'
                  ? 'Model Off'
                  : backendStatus === 'disconnected'
                  ? 'Disconnected'
                  : 'Connecting'}
              </span>
            </div>

            {/* Auth Buttons or User Badge */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2 pl-1 border-l border-slate-200">
                <button
                  onClick={() => handleNavClick('profile')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition ${
                    activeTab === 'profile'
                      ? 'bg-brand-50 border-brand-300 text-brand-800'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                  title="Manage account settings"
                >
                  <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-brand-600 to-teal-500 text-white font-bold text-[10px] flex items-center justify-center">
                    {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <span className="max-w-[110px] truncate">{user?.full_name?.split(' ')[0]}</span>
                  {user?.role === 'admin' && (
                    <span className="text-[9px] uppercase font-extrabold px-1 py-0.2 rounded bg-amber-100 text-amber-800">
                      Admin
                    </span>
                  )}
                </button>

                <button
                  onClick={handleLogout}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                  title="Sign out"
                  aria-label="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 pl-1 border-l border-slate-200">
                <button
                  onClick={() => handleNavClick('login')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                    activeTab === 'login'
                      ? 'bg-brand-50 text-brand-700 border border-brand-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Sign In</span>
                </button>

                <button
                  onClick={() => handleNavClick('register')}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-brand-600 to-teal-600 hover:from-brand-700 hover:to-teal-700 text-white text-xs font-bold rounded-xl shadow-sm transition active:scale-95"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Sign Up</span>
                </button>
              </div>
            )}
          </div>

          {/* Mobile menu hamburger */}
          <div className="lg:hidden flex items-center gap-2">
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
        <div className="lg:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-5 space-y-1.5 shadow-xl animate-fadeIn">
          {/* User Status Bar in Mobile */}
          {isAuthenticated ? (
            <div className="p-3 mb-2 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-brand-600 text-white font-bold text-xs flex items-center justify-center">
                  {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">{user?.full_name}</p>
                  <p className="text-[10px] text-slate-500 capitalize">{user?.role} Account</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="text-xs font-bold text-rose-600 hover:underline flex items-center gap-1"
              >
                <LogOut className="w-3 h-3" />
                <span>Log Out</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2 mb-3">
              <button
                onClick={() => handleNavClick('login')}
                className="w-full py-2.5 px-3 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50 text-center"
              >
                Sign In
              </button>
              <button
                onClick={() => handleNavClick('register')}
                className="w-full py-2.5 px-3 rounded-xl bg-brand-600 text-white text-xs font-bold text-center shadow"
              >
                Sign Up
              </button>
            </div>
          )}

          {/* Navigation Items */}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 border border-brand-200'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-4 h-4 text-brand-600" />
                {item.label}
              </button>
            );
          })}

          {isAuthenticated && (
            <button
              onClick={() => handleNavClick('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold ${
                activeTab === 'profile'
                  ? 'bg-brand-50 text-brand-700 border border-brand-200'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <User className="w-4 h-4 text-brand-600" />
              Account Settings
            </button>
          )}

          <div className="pt-2">
            <button
              onClick={() => handleNavClick('assessment')}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-brand-600 to-teal-600 text-white font-bold text-sm rounded-xl shadow"
            >
              <Stethoscope className="w-4 h-4" />
              Check Symptoms Now
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
