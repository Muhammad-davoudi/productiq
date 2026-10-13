import React from 'react';

export default function KPICard({ title, value, subtitle, highlight = false, badge = null }) {
  const formattedValue = typeof value === 'number' ? value.toLocaleString('fa-IR') : value;

  return (
    <div
      className={`bg-[#0b1120] border ${
        highlight ? 'border-teal-500/50 shadow-teal-950/20 shadow-md' : 'border-slate-800/90'
      } rounded-xl p-4 flex flex-col justify-between transition-all duration-200`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-[13px] text-slate-400 font-medium">{title}</span>
        {badge && (
          <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-slate-800 text-cyan-300 border border-slate-700">
            {badge}
          </span>
        )}
      </div>
      <div className="my-1">
        <div className="text-2xl lg:text-3xl font-black text-sky-300 tracking-tight">
          {formattedValue}
        </div>
      </div>
      {subtitle && (
        <div className="text-[12px] text-slate-400 mt-1.5 leading-relaxed">{subtitle}</div>
      )}
    </div>
  );
}
