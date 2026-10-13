import React, { useState, useEffect } from 'react';
import SafePlot from './Plot';
import KPICard from './KPICard';
import clusteringEval from '../data/clustering_evaluation.json';

export default function MonitoringTab({ defaultPlotLayout, nlpEval, clusters, toPersianNum }) {
  const [stats, setStats] = useState({
    version: 'Active-Model',
    cpu: 18,
    ram: 32,
    runs: [
      { version: 'NLP-LinearSVC', accuracy: 0.708, f1_score: 0.709 },
      { version: 'KMeans-k5', accuracy: 0.0, f1_score: 0.635 },
      { version: 'Hybrid-Recommender', accuracy: 0.0, f1_score: 0.0 }
    ]
  });
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState('پیش‌فرض');

  const getApiUrl = (endpoint) => {
    const isViteDev = window.location.port === '5173';
    const base = isViteDev ? 'http://127.0.0.1:8000' : '';
    return `${base}${endpoint}`;
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const res = await fetch(getApiUrl('/api/monitoring/stats'));
        if (!res.ok) throw new Error('bad status');
        const data = await res.json();
        const list = Array.isArray(data) ? data : [data];
        const item = list[0] || {};
        if (cancelled) return;

        // فقط اگر داده معنادار آمد جایگزین کن
        const hasReal =
          list.length > 0 &&
          (Number(item.cpu) > 0 || Number(item.ram) > 0 || item.version);

        if (hasReal) {
          setStats({
            version: item.version || item.model_version || 'Active-Model',
            cpu: Number(item.cpu) || 18,
            ram: Number(item.ram) || 32,
            runs: list.map(r => ({
              version: r.version || r.model_version || 'Run',
              accuracy: Number(r.accuracy) || 0,
              f1_score: Number(r.f1_score) || 0
            }))
          });
          setSource('API / MLflow');
        } else {
          setSource('پیش‌فرض محلی');
        }
      } catch {
        if (!cancelled) setSource('پیش‌فرض محلی (API در دسترس نیست)');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, []);

  // ——— NLP ———
  const f1 = nlpEval?.f1_per_class || { Negative: 0.6923, Neutral: 0.6258, Positive: 0.8075 };
  const acc = nlpEval?.accuracy ?? 0.7083;
  const macroF1 = nlpEval?.macro_f1 ?? 0.7085;
  const modelName = nlpEval?.model || 'TF-IDF + LinearSVC';
  const dataset = nlpEval?.dataset || 'labeling_sample_1200';

  // ——— Clustering ———
  const selectedK = clusteringEval?.selected_k ?? 5;
  const evalMetrics = Array.isArray(clusteringEval?.evaluation_metrics)
    ? clusteringEval.evaluation_metrics
    : [];
  const best = evalMetrics.find(m => m.k === selectedK) || evalMetrics[evalMetrics.length - 1] || {};
  const silhouette = Number(best.silhouette_score) || 0.635;
  const davies = Number(best.davies_bouldin_score) || 0.46;
  const inertia = Number(best.inertia) || 35174;
  const featuresUsed = clusteringEval?.features_used || [];

  const clusterList = Array.isArray(clusters) ? clusters : [];
  const activeCount = clusterList
    .filter(c => c.group === 'Active')
    .reduce((s, c) => s + (Number(c.total_products) || 0), 0);
  const inactiveCount = clusterList
    .filter(c => c.group === 'Inactive')
    .reduce((s, c) => s + (Number(c.total_products) || 0), 0);
  const totalClusterProducts = activeCount + inactiveCount || 1;
  const fmt = typeof toPersianNum === 'function'
    ? toPersianNum
    : (n) => Number(n || 0).toLocaleString('fa-IR');

  // فونت‌های بزرگ‌تر مخصوص این تب
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-300 text-base">
        <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping ml-2.5"></span>
        در حال دریافت مشخصات سیستم و MLflow...
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* ========== سخت‌افزار + MLflow ========== */}
      <section>
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <h2 className="text-lg font-bold text-white">وضعیت سخت‌افزار و نسخه‌های ثبت‌شده در MLflow</h2>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-400 border border-slate-700">
            منبع: {source}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            <KPICard title="آخرین نسخه / Run" value={stats.version} subtitle="نسخه عملیاتی یا mlflow.runName" badge="MLflow" />
            <KPICard
              title="بار پردازشی"
              value={`CPU ${stats.cpu}٪`}
              subtitle={`RAM: ${stats.ram}٪`}
              badge="سیستم"
              highlight={stats.cpu > 80 || stats.ram > 80}
            />
          </div>
          <div className="lg:col-span-2 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">مصرف منابع سرور استنتاج</h3>
            <div className="h-52">
              <SafePlot
                data={[{
                  type: 'bar',
                  x: ['پردازنده (CPU)', 'حافظه رم (RAM)'],
                  y: [stats.cpu, stats.ram],
                  marker: {
                    color: [
                      stats.cpu > 80 ? '#ef4444' : '#06b6d4',
                      stats.ram > 80 ? '#ef4444' : '#8b5cf6'
                    ]
                  },
                  text: [`${stats.cpu}٪`, `${stats.ram}٪`],
                  textposition: 'outside',
                  textfont: { size: 15, color: '#f1f5f9', family: 'Vazirmatn, Tahoma' }
                }]}
                layout={{
                  ...plotFont,
                  margin: { t: 35, r: 20, b: 45, l: 55 },
                  yaxis: {
                    ...plotFont.yaxis,
                    range: [0, 100],
                    title: { text: 'درصد اشغال', font: { size: 13, color: '#94a3b8' } }
                  }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>

        <div className="mt-4 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4 overflow-x-auto">
          <h3 className="text-[15px] font-semibold text-slate-100 mb-3">Runهای ثبت‌شده</h3>
          <table className="w-full text-right text-sm text-slate-300">
            <thead className="bg-[#151e33] text-slate-300 border-b border-slate-700">
              <tr>
                <th className="py-3 px-3 font-semibold">نام Run / مدل</th>
                <th className="py-3 px-3 font-semibold">Accuracy</th>
                <th className="py-3 px-3 font-semibold">F1 / Silhouette</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {(stats.runs || []).map((r, i) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="py-3 px-3 text-cyan-300 font-medium text-[14px]">{r.version || '—'}</td>
                  <td className="py-3 px-3 text-[14px]">
                    {r.accuracy ? `${(Number(r.accuracy) * 100).toFixed(1)}٪` : '—'}
                  </td>
                  <td className="py-3 px-3 text-[14px]">
                    {r.f1_score ? Number(r.f1_score).toFixed(3) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ========== NLP ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">مدل تحلیل احساسات (NLP)</h2>
        <p className="text-sm text-slate-400 mb-3">منبع: nlp_evaluation.json</p>
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
                  y: [f1.Negative, f1.Neutral, f1.Positive],
                  text: [f1.Negative, f1.Neutral, f1.Positive].map(
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

      {/* ========== Clustering ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">مدل خوشه‌بندی کالاها (K-Means)</h2>
        <p className="text-sm text-slate-400 mb-3">منبع: clustering_evaluation.json · k={selectedK}</p>
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

      {/* ========== Recommender ========== */}
      <section>
        <h2 className="text-lg font-bold text-white mb-1">سیستم توصیه‌گر هوشمند</h2>
        <p className="text-sm text-slate-400 mb-3">معماری هیبریدی · Embedding + Clustering + Intent</p>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-4">
            <KPICard title="معماری" value="Hybrid" subtitle="چندلایه امتیازدهی" badge="Recommender" />
            <KPICard title="ورودی‌ها" value="۳ منبع" subtitle="متن · خوشه · رفتار" badge="سیگنال" />
            <KPICard title="وضعیت" value="فعال" subtitle="دستیار گفتگویی آنلاین" badge="Status" highlight />
          </div>
          <div className="lg:col-span-2 bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h3 className="text-[15px] font-semibold text-slate-100 mb-3">وزن نسبی لایه‌های امتیازدهی</h3>
            <div className="h-52">
              <SafePlot
                data={[{
                  type: 'bar',
                  x: ['شباهت معنایی', 'خوشه کالا', 'تعامل کاربر', 'فیلتر دسته'],
                  y: [0.92, 0.85, 0.78, 0.70],
                  text: ['۹۲٪', '۸۵٪', '۷۸٪', '۷۰٪'],
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
