import { ReactNode } from 'react';

interface AlertProps {
  children: ReactNode;
  type?: 'info' | 'success' | 'warning' | 'error';
  onClose?: () => void;
  className?: string;
}

export default function Alert({ children, type = 'info', onClose, className = '' }: AlertProps) {
  const styles = {
    info: 'glass border-blue-300 text-blue-900',
    success: 'glass border-green-300 text-green-900',
    warning: 'glass border-yellow-300 text-yellow-900',
    error: 'glass border-red-300 text-red-900',
  };

  const bgStyles = {
    info: 'bg-blue-100/50',
    success: 'bg-green-100/50',
    warning: 'bg-yellow-100/50',
    error: 'bg-red-100/50',
  };

  const icons = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    error: '❌',
  };

  return (
    <div className={`border-2 rounded-xl p-4 ${styles[type]} ${bgStyles[type]} flex items-start space-x-3 shadow-lg fade-in ${className}`}>
      <span className="text-2xl flex-shrink-0">{icons[type]}</span>
      <div className="flex-1 font-medium">{children}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 transition-all hover:scale-110 flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-lg hover:bg-white/50"
        >
          ✕
        </button>
      )}
    </div>
  );
}