
import { AuthProvider, useAuth } from './AuthContext';
import URLShortener from './URLShortener';
import AuthForm from './AuthForm';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen w-full bg-teal-100 flex justify-center items-center">
        <div className="max-w-md px-6">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-teal-600 border-t-transparent mx-auto mb-4"></div>
            <p className="text-teal-700 text-xl font-semibold">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <URLShortener /> : <AuthForm />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
