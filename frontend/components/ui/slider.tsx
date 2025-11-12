"use client"

import * as React from "react"

interface SliderProps {
  value: number[];
  onValueChange: (value: number[]) => void;
  max?: number;
  step?: number;
  className?: string;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ value, onValueChange, max = 100, step = 1, className = "" }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onValueChange([parseFloat(e.target.value)]);
    };

    return (
      <input
        ref={ref}
        type="range"
        min="0"
        max={max}
        step={step}
        value={value[0] || 0}
        onChange={handleChange}
        className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider ${className}`}
        style={{
          background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(value[0] || 0) / max * 100}%, #e5e7eb ${(value[0] || 0) / max * 100}%, #e5e7eb 100%)`
        }}
      />
    );
  }
);

Slider.displayName = "Slider";

export { Slider };
