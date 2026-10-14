import React, { useState, useEffect } from 'react';
import SafePlot from './Plot';
import KPICard from './KPICard';

export default function MonitoringTab({ defaultPlotLayout, nlpEval: initialNlpEval, clusters, toPersianNum }) {
  const [monitoringData, setMonitoringData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchMonitoringData = async () => {
      try {
        const res = await fetch('/api/monitoring/stats');
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        if (isMounted) {
          setMonitoringData(data);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Failed to fetch monitoring data:", err);
          setError(err.message);
          setLoading(false);
        }
      }
    };

    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 15000); // به روز رسانی خودکار هر ۱۵ ثانیه

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const fmt = typeof toPersianNum === 'function'
    ? toPersianNum
    : (n) => Number(n || 0).toLocaleString('fa-IR');

  // داده‌های NLP (ترجیح با دیتای زنده‌ی بک‌اند، سپس prop پاس‌داده‌شده)
  const nlp = monitoringData?.nlp || initialNlpEval || {};
  const f1 = nlp?.f1_per_class || { Negative: 0, Neutral: 0, Positive: 0 };
  const acc = Number(nlp?.accuracy) || 0;
  const macroF1 = Number(nlp?.macro_f1) || 0;
  const modelName = nlp?.model || 'TF-IDF + LinearSVC';
  const dataset = nlp?.dataset || 'labeling_sample_1200';

  // داده‌های خوشه‌بندی
  const clusteringEval = monitoringData?.clustering || {};
  const selectedK = clusteringEval?.selected_k ?? 5;
  const evalMetrics = Array.isArray(clusteringEval?.evaluation_metrics)
    ? clusteringEval.evaluation_metrics
    : [];
  const best = evalMetrics.find(m => m.k === selectedK) || evalMetrics[evalMetrics.length - 1] || {};
  const silhouette = Number(best.silhouette_score) || 0;
  const davies = Number(best.davies_bouldin_score) || 0;
  const inertia = Number(best.inertia) || 0;
  const featuresUsed = clusteringEval?.features_used || [];

  // سیستم توصیه‌گر
  const recommender = monitoringData?.recommender || {};
  const recLayers = recommender?.scoring_layers || [
    { name: 'شباهت معنایی', weight: 0.92 },
    { name: 'خوشه کالا', weight: 0.85 },
    { name: 'تعامل کاربر', weight: 0.78 },
    { name: 'فیلتر دسته', weight: 0.70 }
  ];

  // منابع سرور
  const sys = monitoringData?.system || { cpu_percent: 0, ram_percent: 0, ram_used_gb: 0, ram_total_gb: 8 };

  const clusterList = Array.isArray(clusters) ? clusters : [];
  const activeCount = clusterList
    .filter(c => c.group === 'Active')
    .reduce((s, c) => s + (Number(c.total_products) || 0), 0);
  const inactiveCount = clusterList
    .filter(c => c.group === 'Inactive')
    .reduce((s, c) => s + (Number(c.total_products) || 0), 0);
  const totalClusterProducts = activeCount + inactiveCount || 1;

  const plotFont = {
    ...defaultPlotLayout,
    font: {
      ...(defaultPlotLayout?.font || {}),
      size: 14,
      color: '#e2e8f0',
      family: 'Vazirmatn, Tahoma, sans-serif'
    },
    xaxis: {
      ...(defaultPlotLayout?.xaxis || {}),
      tickfont: { size: 13, color: '#cbd5e1', family: 'Vazirmatn, Tahoma' },
      titlefont: { size: 13, color: '#94a3b8' }
    },
    yaxis: {
      ...(defaultPlotLayout?.yaxis || {}),
      tickfont: { size: 13, color: '#cbd5e1', family: 'Vazirmatn, Tahoma' },
      titlefont: { size: 13, color: '#94a3b8' }
    },
    legend: {
      font: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' }
    },
    hoverlabel: {
      bgcolor: '#ffffff',
      bordercolor: '#e2e8f0',
      font: { color: '#0f172a', size: 14, family: 'Vazirmatn, Tahoma, sans-serif' }
    }
  };

  return (
    <div className="space-y-10">
      {/* ========== وضعیت زیرساخت و منابع سرور ========== */}
      <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">مانیتورینگ منابع سرور و زیرساخت</h2>
            <p className="text-xs text-slate-400 mt-0.5">دریافت زنده از API بک‌اند (/api/monitoring/stats)</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`inline-block w-2.5 h-2.5 rounded-full ${loading ? 'bg-amber-400 animate-pulse' : error ? 'bg-rose-500' : 'bg-emerald-400'}`}></span>
            <span className="text-xs text-slate-300">{loading ? 'در حال همگام‌سازی...' : error ? 'خطای شبکه' : 'آنلاین و همگام'}</span>
          </div>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="مصرف پردازنده (CPU)" value={`${sys.cpu_percent}٪`} subtitle="بار پردازشی جاری" badge="System" />
          <KPICard title="مصرف حافظه (RAM)" value={`${sys.ram_percent}٪`} subtitle={`${sys.ram_used_gb} / ${sys.ram_total_gb} GB`} badge="Memory" highlight={sys.ram_percent > 85} />
          <KPICard title="وضعیت MLflow" value={monitoringData?.mlflow?.status || 'Active'} subtitle={`آخرین Run: ${monitoringData?.mlflow?.latest_run_id || 'N/A'}`} badge="Registry" />
          <KPICard title="وضعیت سرویس توصیه‌گر" value={recommender.status || 'Active'} subtitle={recommender.architecture ? 'هیبریدی' : 'آنلاین'} badge="Service" highlight />
        </div>
      </section>

      {/* ========== فرآیند مدل‌سازی تحلیل احساسات ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">فرآیند مدل‌سازی تحلیل احساسات</h2>
        <p className="text-sm text-slate-400 mb-3">منبع: بک‌اند و nlp_evaluation.json</p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            <KPICard title="معماری" value={modelName} subtitle={dataset} badge="NLP" />
            <KPICard
              title="Accuracy"
              value={`${(acc * 100).toFixed(1)}٪`}
              subtitle="مجموعه آزمون ۲۰٪"
              badge="ارزیابی"
              highlight={acc >= 0.7}
            />
            <KPICard title="Macro F1" value={`${(macroF1 * 100).toFixed(1)}٪`} subtitle="توازن سه کلاس" badge="F1" />
          </div>
          <div className="lg:col-span-2 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">F1-Score به تفکیک کلاس</h3>
            <div className="h-60">
              <SafePlot
                data={[{
                  type: 'bar',
                  x: ['منفی', 'خنثی', 'مثبت'],
                  y: [f1.Negative || 0, f1.Neutral || 0, f1.Positive || 0],
                  text: [f1.Negative || 0, f1.Neutral || 0, f1.Positive || 0].map(
                    v => `${(Number(v) * 100).toFixed(1)}٪`
                  ),
                  textposition: 'outside',
                  textfont: { size: 15, color: '#f1f5f9', family: 'Vazirmatn, Tahoma' },
                  marker: { color: ['#ef4444', '#94a3b8', '#22c55e'] }
                }]}
                layout={{
                  ...plotFont,
                  margin: { t: 40, r: 20, b: 45, l: 55 },
                  yaxis: { ...plotFont.yaxis, range: [0, 1.2], tickformat: '.0%' }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* ========== مدل خوشه‌بندی کالاها ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">مدل خوشه‌بندی کالاها (K-Means)</h2>
        <p className="text-sm text-slate-400 mb-3">منبع: بک‌اند و clustering_evaluation.json · k={selectedK}</p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            <KPICard title="k انتخاب‌شده" value={selectedK} subtitle="بر اساس Silhouette" badge="Clustering" />
            <KPICard
              title="Silhouette"
              value={silhouette.toFixed(3)}
              subtitle="هرچه بالاتر بهتر"
              badge="کیفیت"
              highlight={silhouette >= 0.5}
            />
            <KPICard title="Davies-Bouldin" value={davies.toFixed(3)} subtitle="هرچه پایین‌تر بهتر" badge="فشردگی" />
          </div>
          <div className="lg:col-span-2 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">مقایسه k: Silhouette و Davies-Bouldin</h3>
            <div className="h-60">
              <SafePlot
                data={[
                  {
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Silhouette',
                    x: evalMetrics.map(m => m.k),
                    y: evalMetrics.map(m => m.silhouette_score),
                    line: { color: '#22c55e', width: 2.5 },
                    marker: { size: 9 }
                  },
                  {
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Davies-Bouldin',
                    x: evalMetrics.map(m => m.k),
                    y: evalMetrics.map(m => m.davies_bouldin_score),
                    line: { color: '#f59e0b', width: 2.5 },
                    marker: { size: 9 },
                    yaxis: 'y2'
                  }
                ]}
                layout={{
                  ...plotFont,
                  margin: { t: 40, r: 60, b: 50, l: 55 },
                  xaxis: {
                    ...plotFont.xaxis,
                    title: { text: 'تعداد خوشه (k)', font: { size: 13, color: '#94a3b8' } },
                    dtick: 1
                  },
                  yaxis: {
                    ...plotFont.yaxis,
                    title: { text: 'Silhouette', font: { size: 13, color: '#22c55e' } },
                    range: [0, 1]
                  },
                  yaxis2: {
                    title: { text: 'Davies-Bouldin', font: { size: 13, color: '#f59e0b' } },
                    overlaying: 'y',
                    side: 'right',
                    showgrid: false,
                    tickfont: { size: 13, color: '#f59e0b' }
                  },
                  legend: {
                    orientation: 'h',
                    y: 1.14,
                    x: 0.5,
                    xanchor: 'center',
                    font: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' }
                  }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
          <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">Inertia به ازای k (Elbow)</h3>
            <div className="h-52">
              <SafePlot
                data={[{
                  type: 'scatter',
                  mode: 'lines+markers',
                  x: evalMetrics.map(m => m.k),
                  y: evalMetrics.map(m => m.inertia),
                  line: { color: '#38bdf8', width: 2.5 },
                  marker: {
                    size: evalMetrics.map(m => (m.k === selectedK ? 12 : 8)),
                    color: evalMetrics.map(m => (m.k === selectedK ? '#22c55e' : '#38bdf8'))
                  }
                }]}
                layout={{
                  ...plotFont,
                  margin: { t: 25, r: 20, b: 50, l: 65 },
                  xaxis: {
                    ...plotFont.xaxis,
                    title: { text: 'k', font: { size: 13, color: '#94a3b8' } },
                    dtick: 1
                  },
                  yaxis: {
                    ...plotFont.yaxis,
                    title: { text: 'Inertia', font: { size: 13, color: '#94a3b8' } }
                  }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
            <p className="text-xs text-slate-400 mt-2">
              نقطه سبز = k نهایی · Inertia در k={selectedK}: {fmt(Math.round(inertia))}
            </p>
          </div>

          <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">ویژگی‌های خوشه‌بندی</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {featuresUsed.map((f, i) => (
                <span
                  key={i}
                  className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 text-cyan-300 border border-slate-700 font-mono"
                >
                  {f}
                </span>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[#070d1a] p-3 rounded-lg border border-slate-800">
                <span className="text-slate-400 block mb-1 text-sm">سهم Active</span>
                <strong className="text-teal-300 text-xl">
                  {((activeCount / totalClusterProducts) * 100).toFixed(0)}٪
                </strong>
                <span className="text-slate-500 block text-xs mt-1">{fmt(activeCount)} کالا</span>
              </div>
              <div className="bg-[#070d1a] p-3 rounded-lg border border-slate-800">
                <span className="text-slate-400 block mb-1 text-sm">سهم Long-tail</span>
                <strong className="text-slate-300 text-xl">
                  {((inactiveCount / totalClusterProducts) * 100).toFixed(0)}٪
                </strong>
                <span className="text-slate-500 block text-xs mt-1">{fmt(inactiveCount)} کالا</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== سیستم توصیه گر هوشمند ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">سیستم توصیه گر هوشمند</h2>
        <p className="text-sm text-slate-400 mb-3">معماری هیبریدی · {recommender.architecture || 'Embedding + Clustering + Intent'}</p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            <KPICard title="معماری" value="Hybrid" subtitle="چندلایه امتیازدهی" badge="Recommender" />
            <KPICard title="ورودی‌ها" value="۳ منبع" subtitle="متن · خوشه · رفتار" badge="سیگنال" />
            <KPICard title="وضعیت" value={recommender.status || "فعال"} subtitle="دستیار گفتگویی آنلاین" badge="Status" highlight />
          </div>
          <div className="lg:col-span-2 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">وزن نسبی لایه‌های امتیازدهی (دریافت پویا از بک‌اند)</h3>
            <div className="h-52">
              <SafePlot
                data={[{
                  type: 'bar',
                  x: recLayers.map(l => l.name),
                  y: recLayers.map(l => l.weight),
                  text: recLayers.map(l => `${(l.weight * 100).toFixed(0)}٪`),
                  textposition: 'outside',
                  textfont: { size: 15, color: '#f1f5f9', family: 'Vazirmatn, Tahoma' },
                  marker: { color: ['#06b6d4', '#14b8a6', '#8b5cf6', '#f59e0b'] }
                }]}
                layout={{
                  ...plotFont,
                  margin: { t: 40, r: 20, b: 55, l: 55 },
                  yaxis: { ...plotFont.yaxis, range: [0, 1.2], tickformat: '.0%' }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
