import * as React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  labelClassName?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, labelClassName, value, onChange, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className={cn("text-sm font-bold leading-none text-black peer-disabled:cursor-not-allowed peer-disabled:opacity-70", labelClassName)}>
            {label}
          </label>
        )}
        <input
          type={type}
          value={value}
          onChange={onChange}
          className={cn(
            'block h-[5vh] w-full rounded-full border border-gray-300 bg-white px-[2vh] py-[1vh] text-[1.6vh] text-gray-900 ring-offset-white transition-all duration-200 file:border-0 file:bg-transparent file:text-[1.6vh] file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-[0.6vh] focus-visible:ring-blue-600/20 focus-visible:border-blue-600 focus-visible:border-[0.3vh] focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-red-500 focus-visible:ring-red-500',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="animate-in slide-in-from-top-1 text-[1.4vh] md:text-[1.6vh] font-medium text-red-600 mt-[0.5vh] ml-[1vh]">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';

export { Input };
