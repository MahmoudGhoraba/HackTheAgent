import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Button from '@/components/Button';
import { BrainIcon, SearchIcon, RobotIcon, ChartIcon, MailIcon, ChevronDownIcon } from '@/components/Icons';

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleGetStarted = () => {
    router.push('/ai-agent');
  };

  const handleConnectGmail = () => {
    router.push('/gmail-oauth');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/20 dark:bg-blue-600/20 rounded-full blur-3xl float"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-300/20 dark:bg-blue-500/20 rounded-full blur-3xl float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-200/10 dark:bg-blue-400/10 rounded-full blur-3xl float" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Main content */}
      <div className={`relative z-10 max-w-5xl mx-auto text-center space-y-8 ${mounted ? 'fade-in' : 'opacity-0'}`}>
        {/* Logo and title */}
        <div className="space-y-4">
          <div className="inline-block">
            <BrainIcon className="w-32 h-32 text-blue-600 dark:text-blue-400 mx-auto mb-6 float" />
          </div>
          <h1 className="text-6xl md:text-7xl font-bold gradient-text mb-4">
            Email Brain AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 font-medium max-w-3xl mx-auto">
            Your intelligent email assistant powered by{' '}
            <span className="font-bold gradient-text">IBM watsonx</span>
          </p>
        </div>

        {/* Feature highlights */}
        <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 ${mounted ? 'slide-in-left' : 'opacity-0'}`} style={{ animationDelay: '0.2s' }}>
          <div className="glass rounded-2xl p-6 hover-lift hover-glow">
            <SearchIcon className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Smart Search</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">
              Find emails instantly with natural language queries powered by semantic search
            </p>
          </div>
          
          <div className="glass rounded-2xl p-6 hover-lift hover-glow" style={{ animationDelay: '0.1s' }}>
            <RobotIcon className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">AI Assistant</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">
              Ask questions about your emails and get intelligent, context-aware answers
            </p>
          </div>
          
          <div className="glass rounded-2xl p-6 hover-lift hover-glow" style={{ animationDelay: '0.2s' }}>
            <ChartIcon className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Auto-Organize</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">
              Automatically classify and prioritize emails with advanced ML models
            </p>
          </div>
        </div>

        {/* CTA buttons */}
        <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center mt-12 ${mounted ? 'scale-in' : 'opacity-0'}`} style={{ animationDelay: '0.4s' }}>
          <Button
            onClick={handleGetStarted}
            className="gradient-primary text-white px-8 py-4 text-lg font-semibold rounded-xl hover-lift shadow-glow-blue min-w-[200px]"
          >
            Get Started →
          </Button>
          <Button
            onClick={handleConnectGmail}
            variant="secondary"
            className="glass px-8 py-4 text-lg font-semibold rounded-xl hover-lift min-w-[200px] flex items-center space-x-2"
          >
            <MailIcon className="w-5 h-5" />
            <span>Connect Gmail</span>
          </Button>
        </div>

        {/* Stats */}
        <div className={`grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto ${mounted ? 'fade-in' : 'opacity-0'}`} style={{ animationDelay: '0.6s' }}>
          <div className="text-center">
            <div className="text-3xl font-bold gradient-text">10x</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Faster Search</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold gradient-text">95%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold gradient-text">24/7</div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">Available</div>
          </div>
        </div>

        {/* Tech stack badges */}
        <div className={`flex flex-wrap justify-center gap-3 mt-12 ${mounted ? 'fade-in' : 'opacity-0'}`} style={{ animationDelay: '0.8s' }}>
          <span className="glass px-4 py-2 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200">
            IBM watsonx
          </span>
          <span className="glass px-4 py-2 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200">
            FastAPI
          </span>
          <span className="glass px-4 py-2 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200">
            Next.js
          </span>
          <span className="glass px-4 py-2 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200">
            OAuth 2.0
          </span>
          <span className="glass px-4 py-2 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200">
            RAG Pipeline
          </span>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="text-gray-400 dark:text-gray-500 text-sm">Scroll to explore</div>
        <ChevronDownIcon className="w-6 h-6 text-gray-400 dark:text-gray-500 mx-auto mt-1" />
      </div>
    </div>
  );
}