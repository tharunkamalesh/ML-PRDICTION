import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DisclaimerBanner from './components/DisclaimerBanner';
import EmergencyModal from './components/EmergencyModal';

import Home from './pages/Home';
import Assessment from './pages/Assessment';
import Results from './pages/Results';
import ModelEvaluation from './pages/ModelEvaluation';
import Dashboard from './pages/Dashboard';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Profile from './pages/Profile';

import { AuthProvider, useAuth } from './context/AuthContext';

import {
  checkHealth,
  fetchSymptoms,
  predictDisease,
  fetchModelMetrics,
  fetchDashboardStats,
  fetchAssessmentHistory,
  clearAssessmentHistory
} from './services/api';

function MainApp() {
  const { user, isAuthenticated, isAdmin } = useAuth();

  const [activeTab, setActiveTab] = useState('home');
  const [returnToTab, setReturnToTab] = useState('home');
  const [backendStatus, setBackendStatus] = useState('connecting');

  // Symptoms catalog state
  const [symptomsData, setSymptomsData] = useState(null);
  const [loadingSymptoms, setLoadingSymptoms] = useState(true);
  const [symptomsError, setSymptomsError] = useState('');

  // Prediction analysis state
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  // Model evaluation metrics state
  const [metrics, setMetrics] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [metricsError, setMetricsError] = useState('');

  // Dashboard and history state
  const [dashboardStats, setDashboardStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Emergency modal state
  const [emergencyModalOpen, setEmergencyModalOpen] = useState(false);
  const [emergencyData, setEmergencyData] = useState(null);

  const refreshDashboardData = useCallback(async () => {
    try {
      setLoadingHistory(true);
      const [stats, hist] = await Promise.all([
        fetchDashboardStats(),
        fetchAssessmentHistory(25, isAdmin)
      ]);
      setDashboardStats(stats);
      setHistory(hist);
    } catch (err) {
      console.warn('Could not refresh dashboard stats:', err);
    } finally {
      setLoadingHistory(false);
    }
  }, [isAdmin]);

  // Initial data loading on mount
  useEffect(() => {
    async function initApp() {
      try {
        const health = await checkHealth();
        if (health.status === 'healthy' && health.model_loaded) {
          setBackendStatus('connected');
        } else if (!health.model_loaded) {
          setBackendStatus('model_unavailable');
        } else {
          setBackendStatus(health.status || 'connected');
        }
      } catch (err) {
        setBackendStatus('disconnected');
      }

      try {
        setLoadingSymptoms(true);
        const symData = await fetchSymptoms();
        setSymptomsData(symData);
      } catch (err) {
        setSymptomsError(err.message || 'Failed to connect to symptoms service');
      } finally {
        setLoadingSymptoms(false);
      }

      try {
        setLoadingMetrics(true);
        const m = await fetchModelMetrics();
        setMetrics(m);
      } catch (err) {
        setMetricsError(err.message || 'Failed to load model metrics');
      } finally {
        setLoadingMetrics(false);
      }

      refreshDashboardData();
    }

    initApp();
  }, [refreshDashboardData]);

  // Refresh history whenever authentication state changes
  useEffect(() => {
    refreshDashboardData();
  }, [isAuthenticated, isAdmin, refreshDashboardData]);

  // Assessment submission handler
  const handleAssessmentSubmit = async (selectedSymptoms) => {
    if (!isAuthenticated) {
      setReturnToTab('assessment');
      setActiveTab('login');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    try {
      setIsPredicting(true);
      const result = await predictDisease(selectedSymptoms);
      setPredictionResult(result);

      // Check if critical emergency symptoms triggered
      if (result.emergency_alert && result.emergency_alert.triggered) {
        setEmergencyData(result.emergency_alert);
        setEmergencyModalOpen(true);
      }

      setActiveTab('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      // Update history in background
      refreshDashboardData();
    } catch (err) {
      if (err.message === 'AUTH_REQUIRED') {
        setReturnToTab('assessment');
        setActiveTab('login');
      } else {
        alert(`Prediction failed: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setIsPredicting(false);
    }
  };

  const handleClearHistory = async () => {
    await clearAssessmentHistory(isAdmin ? 'all' : 'personal');
    await refreshDashboardData();
  };

  const handleResetAssessment = () => {
    setPredictionResult(null);
    setActiveTab('assessment');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigate = (tab, intendedReturn = null) => {
    if (intendedReturn) {
      setReturnToTab(intendedReturn);
    } else if (tab === 'login' || tab === 'register') {
      if (activeTab !== 'login' && activeTab !== 'register') {
        setReturnToTab(activeTab);
      }
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Clinical & Hotline Notice */}
      <DisclaimerBanner />

      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={handleNavigate}
        backendStatus={backendStatus}
      />

      {/* Main Content Router */}
      <main className="flex-1">
        {activeTab === 'home' && (
          <Home
            onNavigate={handleNavigate}
            stats={dashboardStats}
          />
        )}

        {activeTab === 'assessment' && (
          <Assessment
            symptomsData={symptomsData}
            loadingSymptoms={loadingSymptoms}
            symptomsError={symptomsError}
            onSubmitAssessment={handleAssessmentSubmit}
            isPredicting={isPredicting}
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'results' && (
          <Results
            result={predictionResult}
            onReset={handleResetAssessment}
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'evaluation' && (
          <ModelEvaluation
            metrics={metrics}
            loadingMetrics={loadingMetrics}
            metricsError={metricsError}
          />
        )}

        {activeTab === 'dashboard' && (
          <Dashboard
            dashboardStats={dashboardStats}
            history={history}
            loadingHistory={loadingHistory}
            onRefreshHistory={refreshDashboardData}
            onClearHistory={handleClearHistory}
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'about' && (
          <About onNavigate={handleNavigate} />
        )}

        {activeTab === 'login' && (
          <Login
            onNavigate={handleNavigate}
            returnTo={returnToTab}
          />
        )}

        {activeTab === 'register' && (
          <Register
            onNavigate={handleNavigate}
            returnTo={returnToTab}
          />
        )}

        {activeTab === 'forgot-password' && (
          <ForgotPassword
            onNavigate={handleNavigate}
          />
        )}

        {activeTab === 'profile' && (
          <Profile
            onNavigate={handleNavigate}
          />
        )}
      </main>

      {/* Emergency Triage Modal */}
      <EmergencyModal
        isOpen={emergencyModalOpen}
        onClose={() => setEmergencyModalOpen(false)}
        emergencyData={emergencyData}
      />

      {/* Footer */}
      <Footer onNavigate={handleNavigate} />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
