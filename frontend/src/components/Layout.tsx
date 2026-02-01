import { ReactNode, useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import DarkModeToggle from './DarkModeToggle';
import { BrainIcon, HomeIcon, RobotIcon, MailIcon, ChartIcon } from './Icons';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { href: '/', label: 'Home', Icon: HomeIcon },
    { href: '/ai-agent', label: 'AI Agent', Icon: RobotIcon },
    { href: '/analytics', label: 'Analytics', Icon: ChartIcon },
    { href: '/gmail-oauth', label: 'Gmail', Icon: MailIcon },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className={`glass sticky top-0 z-50 transition-all duration-300 ${
        scrolled ? 'shadow-lg' : ''
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center space-x-3 hover-lift transition-all group"
            >
              <BrainIcon className="w-8 h-8 text-blue-600 dark:text-blue-400 float" />
              <div>
                <h1 className="text-xl font-bold gradient-text">Email Brain AI</h1>
                <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">Powered by IBM watsonx</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center space-x-2">
              {navItems.map((item) => {
                const isActive = router.pathname === item.href;
                const Icon = item.Icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl transition-all font-semibold ${
                      isActive
                        ? 'gradient-primary text-white shadow-glow-blue'
                        : 'glass text-gray-700 dark:text-gray-200 hover-lift'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
              <DarkModeToggle />
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="glass mt-auto border-t border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand */}
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">🧠</span>
                <span className="font-bold gradient-text text-lg">Email Brain AI</span>
              </div>
              <p className="text-sm text-gray-600">
                Intelligent email management powered by IBM watsonx and advanced AI
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/ai-agent" className="text-gray-600 hover:text-blue-600 transition-colors">
                    AI Agent
                  </Link>
                </li>
                <li>
                  <Link href="/gmail-oauth" className="text-gray-600 hover:text-blue-600 transition-colors">
                    Gmail Connection
                  </Link>
                </li>
                <li>
                  <a
                    href="http://localhost:8000/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-blue-600 transition-colors"
                  >
                    API Documentation
                  </a>
                </li>
              </ul>
            </div>

            {/* Tech Stack */}
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Built With</h3>
              <div className="flex flex-wrap gap-2">
                <span className="glass px-3 py-1 rounded-full text-xs font-medium">
                  IBM watsonx
                </span>
                <span className="glass px-3 py-1 rounded-full text-xs font-medium">
                  FastAPI
                </span>
                <span className="glass px-3 py-1 rounded-full text-xs font-medium">
                  Next.js
                </span>
                <span className="glass px-3 py-1 rounded-full text-xs font-medium">
                  Tailwind CSS
                </span>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between text-sm text-gray-600">
            <p>© 2026 Email Brain AI - IBM Dev Day Hackathon</p>
            <div className="flex items-center space-x-4 mt-4 sm:mt-0">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors font-medium"
              >
                API Docs →
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors font-medium"
              >
                GitHub →
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}