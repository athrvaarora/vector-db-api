import React from 'react';
import { 
  ArrowUpIcon, 
  ArrowDownIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';

interface MetricsCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    period: string;
  };
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  change,
  icon: Icon,
  variant = 'primary',
  size = 'md',
  className = '',
}) => {
  const variantClasses = {
    primary: {
      bg: 'from-primary-500 to-primary-600',
      text: 'text-white',
      accent: 'bg-primary-400/20',
    },
    secondary: {
      bg: 'from-secondary-500 to-secondary-600',
      text: 'text-white',
      accent: 'bg-secondary-400/20',
    },
    accent: {
      bg: 'from-accent-500 to-accent-600',
      text: 'text-white',
      accent: 'bg-accent-400/20',
    },
    success: {
      bg: 'from-green-500 to-emerald-600',
      text: 'text-white',
      accent: 'bg-green-400/20',
    },
    warning: {
      bg: 'from-yellow-500 to-orange-600',
      text: 'text-white',
      accent: 'bg-yellow-400/20',
    },
    danger: {
      bg: 'from-red-500 to-rose-600',
      text: 'text-white',
      accent: 'bg-red-400/20',
    },
  };

  const sizeClasses = {
    sm: {
      padding: 'p-4',
      title: 'text-xs',
      value: 'text-lg',
      icon: 'h-6 w-6',
    },
    md: {
      padding: 'p-6',
      title: 'text-sm',
      value: 'text-2xl',
      icon: 'h-8 w-8',
    },
    lg: {
      padding: 'p-8',
      title: 'text-base',
      value: 'text-4xl',
      icon: 'h-10 w-10',
    },
  };

  const getChangeColor = (changeValue: number) => {
    if (changeValue > 0) return 'text-green-400';
    if (changeValue < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const getChangeIcon = (changeValue: number) => {
    if (changeValue > 0) return ArrowTrendingUpIcon;
    if (changeValue < 0) return ArrowTrendingDownIcon;
    return null;
  };

  const classes = variantClasses[variant];
  const sizes = sizeClasses[size];

  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${classes.bg} shadow-xl shadow-${variant}-500/25 hover:shadow-2xl hover:shadow-${variant}-500/40 transition-all duration-300 hover:scale-105 group ${className}`}>
      {/* Background decoration */}
      <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full" />
      <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-white/5 rounded-full" />
      
      <div className={`relative ${sizes.padding}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className={`${classes.text} ${sizes.title} font-semibold uppercase tracking-wider opacity-90`}>
              {title}
            </h3>
            <p className={`${classes.text} ${sizes.value} font-bold mt-2 tracking-tight`}>
              {value}
            </p>
            
            {change && (
              <div className="flex items-center mt-3 space-x-2">
                {getChangeIcon(change.value) && (
                  React.createElement(getChangeIcon(change.value)!, {
                    className: `h-4 w-4 ${getChangeColor(change.value)}`
                  })
                )}
                <span className={`text-sm font-medium ${getChangeColor(change.value)}`}>
                  {change.value > 0 ? '+' : ''}{change.value}%
                </span>
                <span className="text-white/70 text-sm">
                  vs {change.period}
                </span>
              </div>
            )}
          </div>
          
          {Icon && (
            <div className={`${classes.accent} rounded-xl p-3 group-hover:scale-110 transition-transform duration-300`}>
              <Icon className={`${sizes.icon} ${classes.text}`} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricsCard;