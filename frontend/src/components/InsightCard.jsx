import React from 'react';

export default function InsightCard({ title, detail, tag = 'بینش تحلیلی' }) {
  return (
    <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4 hover:border-cyan-800/60 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-cyan-200 flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 rounded-full bg-cyan-400"></span>
          {title}
        </h3>
        <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60">
          {tag}
        </span>
      </div>
      <p className="text-xs text-slate-300 leading-relaxed">{detail}</p>
    </div>
  );
}
