import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}

export default function Card({ children, className = '', hover = false, gradient = false }: CardProps) {
  return (
    <div
      className={`${
        gradient ? 'gradient-card' : 'glass'
      } rounded-2xl shadow-lg p-6 ${
        hover ? 'hover-lift hover-glow' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}