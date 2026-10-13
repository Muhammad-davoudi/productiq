import React, { useMemo, useState } from 'react';
import SafePlot from './Plot';
import rawData from '../data/sentiment_wordcloud_top30.json';

const TAB_CONFIG = [
  {
    key: 'positive',
    label: 'مثبت',
    activeClass: 'bg-emerald-600 text-white border-emerald-500',
    idleClass: 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60 hover:bg-emerald-900/50'
  },
  {
    key: 'neutral',
    label: 'خنثی',
    activeClass: 'bg-slate-500 text-white border-slate-400',
    idleClass: 'bg-slate-800/60 text-slate-400 border-slate-600 hover:bg-slate-700/60'
  },
  {
    key: 'negative',
    label: 'منفی',
    activeClass: 'bg-rose-600 text-white border-rose-500',
    idleClass: 'bg-rose-950/40 text-rose-400 border-rose-800/60 hover:bg-rose-900/50'
  }
];

const COLORS = {
  positive: ['#22c55e', '#4ade80', '#16a34a', '#86efac', '#34d399', '#10b981', '#6ee7b7', '#a7f3d0'],
  neutral: ['#94a3b8', '#64748b', '#cbd5e1', '#78869c', '#a1a1aa', '#71717a', '#9ca3af', '#b0b8c4'],
  negative: ['#ef4444', '#f87171', '#dc2626', '#fb7185', '#f43f5e', '#e11d48', '#fda4af', '#ff6b6b']
};

// داده واقعی فایل
const BY_SENTIMENT = rawData?.wordcloud_by_sentiment || {};

function getWords(sentimentKey) {
  const list = BY_SENTIMENT[sentimentKey] || [];
  return list
    .map(item => ({
      text: item.word || item.text || '',
      // اولویت با tfidf_score برای اندازه، count برای نمایش hover
      value: Number(item.tfidf_score ?? item.count ?? 1) || 1,
      count: Number(item.count ?? 0)
    }))
    .filter(w => w.text)
    .sort((a, b) => b.value - a.value)
    .slice(0, 30);
}

export default function RealWordCloud({ toPersianNum }) {
  const [activeTab, setActiveTab] = useState('positive');

  const lists = useMemo(() => ({
    positive: getWords('positive'),
    neutral: getWords('neutral'),
    negative: getWords('negative')
  }), []);

  const plotData = useMemo(() => {
    const list = lists[activeTab] || [];

    if (list.length === 0) {
      return [{
        type: 'scatter',
        mode: 'text',
        x: [0.5],
        y: [0.5],
        text: ['کلمه‌ای برای این دسته نیست'],
        textfont: { size: 15, color: '#64748b', family: 'Vazirmatn, Tahoma' },
        hoverinfo: 'skip'
      }];
    }

    const max = Math.max(...list.map(w => w.value), 1);
    const palette = COLORS[activeTab] || COLORS.neutral;

    const positioned = list.map((w, i) => {
      const angle = (i * 2.35) + (i % 3) * 0.35;
      const radius = 0.12 + (i / Math.max(list.length, 1)) * 0.78;
      const x = 0.5 + Math.cos(angle) * radius * (0.55 + (i % 5) * 0.05);
      const y = 0.5 + Math.sin(angle) * radius * (0.48 + (i % 4) * 0.07);
      const size = 15 + (w.value / max) * 24;
      return { ...w, x, y, size, color: palette[i % palette.length] };
    });

    return [{
      type: 'scatter',
      mode: 'text',
      x: positioned.map(p => p.x),
      y: positioned.map(p => p.y),
      text: positioned.map(p => p.text),
      textfont: {
        size: positioned.map(p => p.size),
        color: positioned.map(p => p.color),
        family: 'Vazirmatn, Tahoma, sans-serif'
      },
      hovertext: positioned.map(p => {
        const c = typeof toPersianNum === 'function' ? toPersianNum(p.count) : p.count;
        const s = p.value.toFixed(2);
        return `${p.text}\nتعداد: ${c}\nTF-IDF: ${s}`;
      }),
      hoverinfo: 'text',
      cliponaxis: false
    }];
  }, [activeTab, lists, toPersianNum]);

  return (
    <div className="bg-[#080e1c] border border-slate-800/80 rounded-2xl overflow-hidden">
      <div className="flex flex-wrap items-center gap-2 px-4 pt-4 pb-2">
        {TAB_CONFIG.map(tab => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-bold border transition-all ${
              activeTab === tab.key ? tab.activeClass : tab.idleClass
            }`}
          >
            {tab.label}
            <span className="mr-1.5 text-[11px] opacity-80 font-normal">
              (
              {typeof toPersianNum === 'function'
                ? toPersianNum((lists[tab.key] || []).length)
                : (lists[tab.key] || []).length}
              )
            </span>
          </button>
        ))}
        <span className="mr-auto text-[11px] text-slate-500 hidden sm:inline">
          منبع: sentiment_wordcloud_top30.json
        </span>
      </div>

      <div className="h-72 sm:h-80 px-2">
        <SafePlot
          key={activeTab}
          data={plotData}
          layout={{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { t: 8, r: 8, b: 8, l: 8 },
            xaxis: { visible: false, range: [0, 1], fixedrange: true },
            yaxis: { visible: false, range: [0, 1], fixedrange: true },
            hoverlabel: {
              bgcolor: '#ffffff',
              bordercolor: '#e2e8f0',
              font: { color: '#0f172a', size: 13, family: 'Vazirmatn, Tahoma, sans-serif' }
            }
          }}
          style={{ width: '100%', height: '100%' }}
          config={{ displayModeBar: false, responsive: true }}
        />
      </div>

      <p className="text-xs text-slate-500 text-center pb-3">
        {activeTab === 'positive' && '۳۰ کلمه برتر نظرات مثبت (بر اساس TF-IDF)'}
        {activeTab === 'neutral' && '۳۰ کلمه برتر نظرات خنثی (بر اساس TF-IDF)'}
        {activeTab === 'negative' && '۳۰ کلمه برتر نظرات منفی (بر اساس TF-IDF)'}
      </p>
    </div>
  );
}
