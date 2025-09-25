import React, { useState } from 'react';
import { User, Mail, Lock, UserPlus, LogIn, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from './AuthContext';

export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;

    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const success = await login(username, password);
        if (!success) {
          setError('Invalid username or password');
        }
      } else {
        // Validation for registration
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          return;
        }
        if (password.length < 6) {
          setError('Password must be at least 6 characters long');
          return;
        }
        if (username.length < 3) {
          setError('Username must be at least 3 characters long');
          return;
        }

        const success = await register(username, email, password);
        if (!success) {
          setError('Registration failed. Username or email might already be taken.');
        }
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const useDemoCredentials = () => {
    setUsername('default_user');
    setPassword('default123');
    setIsLogin(true);
  };

  return (
    <div className="min-h-screen w-full bg-teal-100 flex justify-center items-center">
      <div className="max-w-md px-6">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-teal-600 rounded-xl mb-8">
            <User className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-slate-800 mb-4">
            Welcome to URL Changer
          </h1>
          <p className="text-slate-600 text-xl">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </p>
        </div>

        {/* Demo Credentials Notice */}
        <div className="bg-blue-100 border-2 border-blue-400 rounded-xl p-6 mb-8 w-full max-w-md">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-blue-800 text-lg mb-2">Demo Account Available</h3>
              <p className="text-blue-700 mb-4">
                You can use the demo account to test the application with existing URLs.
              </p>
              <button
                onClick={useDemoCredentials}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
              >
                Use Demo Account
              </button>
            </div>
          </div>
        </div>

        {/* Auth Form */}
        <div className="bg-white rounded-2xl p-10 shadow-lg w-full max-w-md">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-lg font-bold text-slate-800 mb-3">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-300 rounded-xl 
                           text-slate-800 text-lg placeholder-slate-500 focus:border-teal-500 
                           outline-none transition-colors"
                  required
                />
              </div>
            </div>

            {/* Email (Registration only) */}
            {!isLogin && (
              <div>
                <label htmlFor="email" className="block text-lg font-bold text-slate-800 mb-3">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-300 rounded-xl 
                             text-slate-800 text-lg placeholder-slate-500 focus:border-teal-500 
                             outline-none transition-colors"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-lg font-bold text-slate-800 mb-3">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-300 rounded-xl 
                           text-slate-800 text-lg placeholder-slate-500 focus:border-teal-500 
                           outline-none transition-colors"
                  required
                />
              </div>
            </div>

            {/* Confirm Password (Registration only) */}
            {!isLogin && (
              <div>
                <label htmlFor="confirmPassword" className="block text-lg font-bold text-slate-800 mb-3">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-300 rounded-xl 
                             text-slate-800 text-lg placeholder-slate-500 focus:border-teal-500 
                             outline-none transition-colors"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-100 border-2 border-red-400 rounded-xl p-4">
                <p className="text-red-800 text-lg font-semibold">
                  {error}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={clsx(
                'w-full py-4 px-6 rounded-xl font-bold text-xl transition-colors shadow-lg flex items-center justify-center gap-3',
                loading
                  ? 'bg-slate-400 cursor-not-allowed text-slate-600'
                  : 'bg-teal-600 hover:bg-teal-700 text-white'
              )}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-slate-600 border-t-transparent"></div>
                  {isLogin ? 'Signing In...' : 'Creating Account...'}
                </>
              ) : (
                <>
                  {isLogin ? <LogIn className="w-6 h-6" /> : <UserPlus className="w-6 h-6" />}
                  {isLogin ? 'Sign In' : 'Create Account'}
                </>
              )}
            </button>

            {/* Switch Mode */}
            <div className="text-center pt-4">
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setEmail('');
                  setConfirmPassword('');
                }}
                className="text-teal-600 hover:text-teal-700 font-semibold text-lg"
              >
                {isLogin 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Sign in"
                }
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}