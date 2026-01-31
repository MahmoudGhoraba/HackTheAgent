import { ReactNode } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  const navItems = [
    { href: '/', label: 'Search', icon: '🔍' },
    { href: '/rag', label: 'Ask AI', icon: '🤖' },
    { href: '/manage', label: 'Manage', icon: '📧' },
    { href: '/stats', label: 'Stats', icon: '📊' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
              <span className="text-3xl">🧠</span>
              <div>
                <h1 className="text-xl font-bold text-gray-900">HackTheAgent</h1>
                <p className="text-xs text-gray-500">Email Brain</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex space-x-1">
              {navItems.map((item) => {
                const isActive = router.pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                      isActive
                        ? 'bg-primary-600 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span>{item.icon}</span>
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2026 HackTheAgent - IBM Dev Day Hackathon</p>
            <div className="flex space-x-4">
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary-600">
                API Docs
              </a>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="hover:text-primary-600">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}