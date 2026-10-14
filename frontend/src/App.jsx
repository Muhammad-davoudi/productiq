import React, { useState, useEffect } from 'react';
import ChatWidget from './components/ChatWidget';
import SafePlot from './components/Plot';
import KPICard from './components/KPICard';
import MonitoringTab from './components/MonitoringTab';
import SimulationTab from './components/SimulationTab';
import RealWordCloud from './components/RealWordCloud';
import clusterProfilesData from './data/real_cluster_profiles.json';
import cleanNlpData from './data/clean_aspects_sentiment.json';

const CATEGORIES = [
  { value: "ALL", label: "همه دسته‌بندی‌ها" },
  { value: "clothe", label: "مد و پوشاک" },
  { value: "book & stationary & art", label: "کتاب، لوازم تحریر و هنر" },
  { value: "beauty", label: "زیبایی و سلامت" },
  { value: "toys and kids", label: "کودک و نوزاد" },
  { value: "rural goods", label: "کالاهای بومی و محلی" },
  { value: "travel", label: "ورزش و سفر" }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [loading, setLoading] = useState(false);

  const [summary, setSummary] = useState({
    total_products: 0,
    unique_categories: 0,
    unique_brands: 0,
    unique_sellers: 0,
    avg_rating: 0,
    avg_price: 0,
    median_price: 0
  });
  const [subcategories, setSubcategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [priceDist, setPriceDist] = useState({ bins: [], counts: [] });
  const [priceRating, setPriceRating] = useState([]);
  const [satisfaction, setSatisfaction] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [nlpEval, setNlpEval] = useState(null);
  const [clusterProfiles, setClusterProfiles] = useState(clusterProfilesData || []);

  const [selectedClusterId, setSelectedClusterId] = useState(null);

  const [openAspects, setOpenAspects] = useState(true);
  const [openWordCloud, setOpenWordCloud] = useState(true);
  const [openConfusion, setOpenConfusion] = useState(true);

  const toPersianNum = (num) => {
    if (num === null || num === undefined || isNaN(Number(num))) return '۰';
    return Number(num).toLocaleString('fa-IR');
  };

  const getApiUrl = (endpoint, query = '') => {
    const isViteDev = window.location.port === '5173';
    const base = isViteDev ? 'http://127.0.0.1:8000/api/analytics' : '/api/analytics';
    return `${base}/${endpoint}${query}`;
  };

  const fetchData = async () => {
    setLoading(true);
    const catQuery = selectedCategory !== 'ALL' ? `?category=${encodeURIComponent(selectedCategory)}` : '';
    
    try {
      const isDev = window.location.port === '5173';
      const clusterProfUrl = isDev ? 'http://127.0.0.1:8000/api/clustering/profiles' : '/api/clustering/profiles';

      const [
        sumRes, subRes, brandRes, priceRes, scatterRes, satRes, clusterRes, nlpRes, clusterProfRes
      ] = await Promise.all([
        fetch(getApiUrl('summary', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('subcategories', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('brands', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('price-distribution', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('price-rating', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('satisfaction', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('clustering-overview', catQuery)).then(r => r.json()).catch(() => null),
        fetch(getApiUrl('nlp-overview', catQuery)).then(r => r.json()).catch(() => null),
        fetch(clusterProfUrl).then(r => r.json()).catch(() => null)
      ]);

      if (sumRes) setSummary(sumRes);
      if (subRes && subRes.items) setSubcategories(subRes.items);
      if (brandRes && brandRes.items) setBrands(brandRes.items);
      if (priceRes && priceRes.bins) setPriceDist(priceRes);
      if (scatterRes && scatterRes.items) setPriceRating(scatterRes.items);
      if (satRes && satRes.items) setSatisfaction(satRes.items);
      if (clusterRes && clusterRes.items) setClusters(clusterRes.items);
      if (nlpRes && nlpRes.model) setNlpEval(nlpRes);
      if (clusterProfRes && Array.isArray(clusterProfRes) && clusterProfRes.length > 0) {
        setClusterProfiles(clusterProfRes);
      }
    } catch (err) {
      console.warn('API sync error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const catQuery = '';
    fetchData();
  }, [selectedCategory]);

  const defaultPlotLayout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: {
      color: '#cbd5e1',
      family: 'Vazirmatn, Tahoma, sans-serif',
      size: 13
    },
    margin: { t: 35, r: 30, b: 55, l: 65 },
    autosize: true,
    hoverlabel: {
      bgcolor: '#ffffff',
      bordercolor: '#e2e8f0',
      font: { color: '#0f172a', size: 13, family: 'Vazirmatn, Tahoma, sans-serif' }
    },
    xaxis: {
      gridcolor: '#1e293b',
      zerolinecolor: '#1e293b',
      tickfont: { size: 12, color: '#94a3b8' },
      titlefont: { size: 12, color: '#64748b' }
    },
    yaxis: {
      gridcolor: '#1e293b',
      zerolinecolor: '#1e293b',
      tickfont: { size: 12, color: '#94a3b8' },
      titlefont: { size: 12, color: '#64748b' }
    }
  };

  const selectedCategoryLabel =
    CATEGORIES.find((cat) => cat.value === selectedCategory)?.label || "همه دسته‌بندی‌ها";

  const CollapsibleSection = ({ title, isOpen, onToggle, children }) => (
    <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3.5 text-right hover:bg-slate-800/40 transition-colors"
      >
        <h2 className="text-[15px] font-semibold text-slate-100">{title}</h2>
        <span className="text-slate-400 text-lg leading-none">{isOpen ? '−' : '+'}</span>
      </button>
      {isOpen && <div className="px-4 pb-4">{children}</div>}
    </div>
  );

// clusterProfiles is managed by useState and fetched via API

    const [nlpSummary, setNlpSummary] = useState(cleanNlpData?.summary || { Positive: 0, Neutral: 0, Negative: 0, total: 1 });
  const [nlpAspects, setNlpAspects] = useState(Array.isArray(cleanNlpData?.aspects) ? cleanNlpData.aspects : []);

  // بارگذاری زنده اطلاعات NLP از بک‌اند با Fallback به فایل محلی
  useEffect(() => {
    const catQuery = '';
    fetch(getApiUrl('nlp-overview', catQuery))
      .then(res => res.json())
      .then(data => {
        if (data && data.summary) setNlpSummary(data.summary);
        if (data && Array.isArray(data.aspects)) setNlpAspects(data.aspects);
      })
      .catch(() => {
        // Fallback به داده‌های محلی در صورت بروز خطا
        if (cleanNlpData?.summary) setNlpSummary(cleanNlpData.summary);
        if (cleanNlpData?.aspects) setNlpAspects(cleanNlpData.aspects);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 p-4 lg:p-6 font-sans select-none" dir="rtl">
      <header className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-white">
              داشبورد هوش مصنوعی و تحلیل داده دیجی‌کالا
            </h1>
            {loading && (
              <span className="text-[11px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/50">
                در حال دریافت داده‌های زنده: {selectedCategoryLabel}...
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            روایت تحلیلی عملکرد بازار، کلاسترینگ کالاها و تحلیل احساسات نظرات
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-[#0d1424] px-3 py-1.5 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 font-medium">دسته‌بندی:</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-[#151e33] text-sky-200 text-xs font-semibold px-2.5 py-1 rounded-lg border border-sky-900/40 focus:outline-none focus:border-sky-500 cursor-pointer"
            >
              {CATEGORIES.map((category) => (
                <option key={category.value} value={category.value} className="bg-[#0f172a] text-white">
                  {category.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* تب‌های پنج‌گانه ناوبری */}
      <div className="flex flex-wrap border-b border-slate-800 mb-6 gap-2 text-base font-medium">
        {[
          { key: 'overview', label: 'ساختار بازار و شاخص‌های کلیدی' },
          { key: 'clustering', label: 'خوشه‌بندی کالاها و رفتار بازار' },
          { key: 'nlp', label: 'تحلیل احساسات و نظرات' },
          { key: 'monitoring', label: 'مانیتورینگ سیستم و مدل' },
          { key: 'simulation', label: 'شبیه‌سازی' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`pb-3.5 px-5 border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-cyan-400 text-cyan-300 font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* تب ۱: ساختار بازار */}
      {activeTab === 'overview' && (
        <div key={selectedCategory} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#0b1120] border border-cyan-900/40 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <h3 className="text-sm font-semibold text-cyan-200">تمرکز بازار</h3>
              </div>
              <p className="text-[13px] text-slate-300 leading-relaxed">
                {subcategories.length >= 3
                  ? (() => {
                      const total = subcategories.reduce((s, i) => s + (Number(i.count) || 0), 0) || 1;
                      const top3 = subcategories.slice(0, 3).reduce((s, i) => s + (Number(i.count) || 0), 0);
                      const pct = ((top3 / total) * 100).toFixed(0);
                      return `حدود ${pct}٪ کالاها در ۳ زیردسته اول متمرکز شده‌اند. بزرگ‌ترین زیردسته «${subcategories[0]?.name || '—'}» است.`;
                    })()
                  : subcategories.length > 0
                    ? `بزرگ‌ترین زیردسته «${subcategories[0]?.name || '—'}» با ${Number(subcategories[0]?.count || 0).toLocaleString('fa-IR')} کالا است.`
                    : 'داده‌ای برای تحلیل تمرکز بازار موجود نیست.'}
              </p>
            </div>

            <div className="bg-[#0b1120] border border-amber-900/40 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <h3 className="text-sm font-semibold text-amber-200">وضعیت رضایت</h3>
              </div>
              <p className="text-[13px] text-slate-300 leading-relaxed">
                {Number(summary.avg_rating) > 0
                  ? Number(summary.avg_rating) < 2.5
                    ? `میانگین امتیاز ${Number(summary.avg_rating).toFixed(2)} پایین‌تر از سطح مطلوب است و نیاز به بررسی کیفیت دارد.`
                    : `میانگین امتیاز ${Number(summary.avg_rating).toFixed(2)} مطلوب است و رضایت خریداران خوب ارزیابی می‌شود.`
                  : 'داده رضایت برای این دسته دریافت نشد.'}
              </p>
            </div>

            <div className="bg-[#0b1120] border border-teal-900/40 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
                <h3 className="text-sm font-semibold text-teal-200">توزیع قیمت</h3>
              </div>
              <p className="text-[13px] text-slate-300 leading-relaxed">
                {Number(summary.avg_price) > 0 && Number(summary.median_price) > 0
                  ? (() => {
                      const avg = Number(summary.avg_price);
                      const med = Number(summary.median_price);
                      const ratio = (avg / med).toFixed(1);
                      if (avg > med * 1.5) {
                        return `میانگین قیمت ${avg.toLocaleString('fa-IR')} تومان و میانه ${med.toLocaleString('fa-IR')} تومان است. اختلاف ${ratio} برابری حاکی از وجود کالاهای بسیار گران‌قیمت است.`;
                      }
                      return `میانه قیمت ${med.toLocaleString('fa-IR')} تومان و میانگین ${avg.toLocaleString('fa-IR')} تومان است. توزیع نسبتاً متوازن است.`;
                    })()
                  : 'داده قیمت برای تحلیل موجود نیست.'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard title="تعداد کل محصولات" value={summary.total_products} subtitle={`در ${toPersianNum(summary.unique_categories)} زیردسته فعال`} badge="تنوع کالا" />
            <KPICard title="میانگین و میانه قیمت (تومان)" value={summary.avg_price} subtitle={`میانه: ${toPersianNum(summary.median_price)} تومان`} badge="توزیع مالی" />
            <KPICard title="میانگین امتیاز رضایت" value={summary.avg_rating} subtitle={Number(summary.avg_rating) >= 2.5 ? "سطح رضایت مطلوب" : "نیازمند پایش کیفیت"} highlight={Number(summary.avg_rating) >= 2.5} badge="امتیاز ۱ تا ۵" />
            <KPICard title="فروشندگان فعال" value={summary.unique_sellers} subtitle={`تعداد برندها: ${toPersianNum(summary.unique_brands)}`} badge="زنجیره تامین" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-sm font-semibold text-slate-200 mb-3">
                تنوع و سهم محصولات در زیردسته‌ها: {selectedCategoryLabel}
              </h2>
              <div className="h-80">
                <SafePlot
                  key={`sub-${selectedCategory}`}
                  data={[{
                    type: 'bar',
                    orientation: 'h',
                    y: [...subcategories].reverse().map(i => i.name),
                    x: [...subcategories].reverse().map(i => i.count),
                    text: [...subcategories].reverse().map(i => toPersianNum(i.count)),
                    textposition: 'outside',
                    textfont: { size: 11, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' },
                    marker: { color: [...subcategories].reverse().map(i => i.count), colorscale: [[0, '#38bdf8'], [1, '#0369a1']], showscale: false },
                    hovertemplate: '%{y}: %{x:,} کالا<extra></extra>'
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    margin: { t: 10, r: 80, b: 30, l: 140 },
                    yaxis: { ...defaultPlotLayout.yaxis, tickfont: { size: 12, color: '#cbd5e1' } }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>

            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-sm font-semibold text-slate-200 mb-3">
                ترکیب برندهای برتر: {selectedCategoryLabel}
              </h2>
              <div className="h-80">
                <SafePlot
                  key={`brand-${selectedCategory}`}
                  data={[{
                    type: 'bar',
                    orientation: 'h',
                    y: [...brands].reverse().map(i => i.name),
                    x: [...brands].reverse().map(i => i.count),
                    text: [...brands].reverse().map(i => toPersianNum(i.count)),
                    textposition: 'outside',
                    textfont: { size: 11, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' },
                    marker: { color: [...brands].reverse().map(i => i.count), colorscale: [[0, '#c084fc'], [1, '#7e22ce']], showscale: false },
                    hovertemplate: '%{y}: %{x:,} کالا<extra></extra>'
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    margin: { t: 10, r: 80, b: 30, l: 110 },
                    yaxis: { ...defaultPlotLayout.yaxis, tickfont: { size: 12, color: '#cbd5e1' } }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-sm font-semibold text-slate-200 mb-3">
                توزیع بازه‌های قیمتی: {selectedCategoryLabel}
              </h2>
              <div className="h-80">
                <SafePlot
                  key={`dist-${selectedCategory}`}
                  data={[{
                    type: 'bar',
                    x: priceDist.bins,
                    y: priceDist.counts,
                    marker: { color: priceDist.counts, colorscale: [[0, '#38bdf8'], [1, '#6366f1']], showscale: false }
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    margin: { t: 10, r: 20, b: 50, l: 50 },
                    xaxis: { ...defaultPlotLayout.xaxis, tickfont: { size: 11, color: '#cbd5e1' } }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>

            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-sm font-semibold text-slate-200 mb-3">
                رابطه میانگین قیمت و امتیاز رضایت: {selectedCategoryLabel}
              </h2>
              <div className="h-80">
                <SafePlot
                  key={`rate-price-${selectedCategory}`}
                  data={[{
                    type: 'scatter',
                    mode: 'lines+markers',
                    x: priceRating.map(i => i.price),
                    y: priceRating.map(i => i.rate),
                    line: { dash: 'dash', width: 1.5, color: 'rgba(148, 163, 184, 0.6)' },
                    marker: { size: 9, color: '#22d3ee', symbol: 'circle' },
                    hovertemplate: 'قیمت: %{x:,.0f} تومان<br>امتیاز: %{y:.2f}<extra></extra>'
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    margin: { t: 10, r: 20, b: 45, l: 55 },
                    xaxis: {
                      ...defaultPlotLayout.xaxis,
                      title: { text: 'میانگین قیمت (تومان)', font: { size: 12, color: '#64748b' } }
                    },
                    yaxis: {
                      ...defaultPlotLayout.yaxis,
                      range: [1, 5],
                      title: { text: 'امتیاز (۱ تا ۵)', font: { size: 12, color: '#64748b' } }
                    }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>
          </div>

          <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
            <h2 className="text-sm font-semibold text-slate-200 mb-3">
              توزیع امتیاز رضایت خریداران (۱ تا ۵ ستاره): {selectedCategoryLabel}
              <span className="text-[11px] text-slate-500 font-normal mr-2">(مقیاس لگاریتمی)</span>
            </h2>
            <div className="h-56">
              <SafePlot
                key={`sat-${selectedCategory}`}
                data={[{
                  type: 'bar',
                  x: satisfaction.map(i => i.label),
                  y: satisfaction.map(i => i.count),
                  text: satisfaction.map(i => toPersianNum(i.count)),
                  textposition: 'outside',
                  textfont: { color: '#e2e8f0', size: 12 },
                  cliponaxis: false,
                  marker: { color: ['#ef4444', '#f97316', '#eab308', '#22c55e', '#14b8a6'] },
                  hovertemplate: 'امتیاز %{x}: %{y:,} نظر<extra></extra>'
                }]}
                layout={{
                  ...defaultPlotLayout,
                  margin: { t: 40, r: 25, b: 50, l: 60 },
                  xaxis: {
                    ...defaultPlotLayout.xaxis,
                    title: { text: 'امتیاز از ۱ تا ۵', font: { size: 12, color: '#64748b' } },
                    tickfont: { size: 13, color: '#cbd5e1' }
                  },
                  yaxis: {
                    ...defaultPlotLayout.yaxis,
                    type: 'log',
                    title: { text: 'تعداد نظرات (لگاریتمی)', font: { size: 12, color: '#64748b' } },
                    tickfont: { size: 12, color: '#94a3b8' }
                  }
                }}
                style={{ width: '100%', height: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>
      )}

      {/* تب ۲: خوشه‌بندی کالاها */}
      {activeTab === 'clustering' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <KPICard title="تعداد خوشه‌های کشف‌شده" value={clusters.length || clusterProfiles.length || 0} subtitle="الگوریتم K-Means کاتالوگ" badge="خوشه‌بندی" />
            <KPICard title="کالاهای بخش فعال (Active)" value={clusterProfiles.filter(c => c.group === 'Active').reduce((acc, c) => acc + (Number(c.total_products) || 0), 0)} badge="بخش فعال" highlight={true} />
            <KPICard title="کالاهای بخش دم‌بلند (Long-tail)" value={clusterProfiles.filter(c => c.group === 'Inactive').reduce((acc, c) => acc + (Number(c.total_products) || 0), 0)} badge="دم بلند" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-cyan-400"></span>سهم درصدی خوشه‌های کالا از کل کاتالوگ</h2>
              <div className="h-80">
                <SafePlot
                  data={[{
                    type: 'pie',
                    labels: clusterProfiles.map(c => c.title || `خوشه ${c.cluster}`),
                    values: clusterProfiles.map(c => Number(c.total_products) || 0),
                    hole: 0.55,
                    marker: { colors: ['#3b82f6', '#14b8a6', '#f59e0b', '#8b5cf6', '#64748b'] },
                    textinfo: 'percent',
                    textposition: 'inside',
                    insidetextfont: { size: 14, color: '#ffffff', family: 'Vazirmatn, Tahoma, sans-serif' },
                    hovertemplate: '%{label}<br>تعداد: %{value:,}<br>سهم: %{percent}<extra></extra>'
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    showlegend: true,
                    legend: { font: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' }, orientation: 'h', y: -0.15 },
                    margin: { t: 15, r: 15, b: 65, l: 15 }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>

            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-teal-400"></span>میانه قیمت در هر خوشه (تومان)</h2>
              <div className="h-80">
                <SafePlot
                  data={[{
                    type: 'bar',
                    x: clusterProfiles.map(c => c.title || `خوشه ${c.cluster}`),
                    y: clusterProfiles.map(c => Number(c.price_median) || 0),
                    marker: { color: '#0d9488' },
                    text: clusterProfiles.map(c => toPersianNum(c.price_median)),
                    textposition: 'outside',
                    textfont: { size: 13, color: '#cbd5e1', family: 'Vazirmatn, Tahoma, sans-serif' }
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    xaxis: {
                      ...defaultPlotLayout.xaxis,
                      tickfont: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' }
                    },
                    yaxis: {
                      ...defaultPlotLayout.yaxis,
                      tickfont: { size: 13, color: '#cbd5e1', family: 'Vazirmatn, Tahoma, sans-serif' }
                    },
                    margin: { t: 30, r: 20, b: 75, l: 75 }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>

            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-emerald-400"></span>میانگین امتیاز رضایت در هر خوشه</h2>
              <div className="h-80">
                <SafePlot
                  data={[{
                    type: 'bar',
                    x: clusterProfiles.map(c => c.title || `خوشه ${c.cluster}`),
                    y: clusterProfiles.map(c => Number(c.rate_mean) || 0),
                    text: clusterProfiles.map(c => Number(c.rate_mean || 0).toFixed(2)),
                    textposition: 'outside',
                    textfont: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' },
                    marker: { color: clusterProfiles.map(c => (Number(c.rate_mean) || 0) >= 3.5 ? '#22c55e' : (Number(c.rate_mean) || 0) >= 2.5 ? '#eab308' : '#ef4444') }
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    xaxis: {
                      ...defaultPlotLayout.xaxis,
                      tickfont: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' }
                    },
                    yaxis: {
                      ...defaultPlotLayout.yaxis,
                      range: [0, 5],
                      tickfont: { size: 13, color: '#cbd5e1', family: 'Vazirmatn, Tahoma, sans-serif' }
                    },
                    margin: { t: 35, r: 20, b: 75, l: 55 }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>

            <div className="bg-[#0b1120] border border-slate-800/90 rounded-xl p-4">
              <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-purple-400"></span>امضای رفتاری و مقایسه چندبعدی خوشه‌ها (Radar Chart)</h2>
              <div className="h-80">
                <SafePlot
                  data={(() => {
                    const radarColors = ['#38bdf8', '#14b8a6', '#f59e0b', '#a855f7', '#64748b'];
                    const thetaLabels = ['سطح قیمت', 'امتیاز رضایت', 'تعداد کالا', 'سهم بازار', 'پایداری'];
                    const maxPrice = Math.max(...clusterProfiles.map(c => Number(c.price_median) || 1), 1);
                    const maxProds = Math.max(...clusterProfiles.map(c => Number(c.total_products) || 1), 1);

                    return clusterProfiles.map((c, i) => {
                      const vals = [
                        Math.round(((Number(c.price_median) || 0) / maxPrice) * 100),
                        Math.round(((Number(c.rate_mean) || 0) / 5) * 100),
                        Math.round(((Number(c.total_products) || 0) / maxProds) * 100),
                        Math.min(100, Math.round((Number(c.share_pct) || 0) * 2)),
                        Math.round(((Number(c.rate_mean) || 0) / 5) * 90)
                      ];
                      return {
                        type: 'scatterpolar',
                        r: [...vals, vals[0]],
                        theta: [...thetaLabels, thetaLabels[0]],
                        fill: 'toself',
                        name: c.title || `خوشه ${c.cluster}`,
                        line: { color: radarColors[i % radarColors.length], width: 1.8 }
                      };
                    });
                  })()}
                  layout={{
                    ...defaultPlotLayout,
                    polar: {
                      bgcolor: 'rgba(15, 23, 42, 0.4)',
                      radialaxis: {
                        visible: true,
                        range: [0, 100],
                        gridcolor: '#1e293b',
                        tickfont: { size: 11, color: '#94a3b8', family: 'Vazirmatn, Tahoma, sans-serif' }
                      },
                      angularaxis: {
                        gridcolor: '#1e293b',
                        tickfont: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' }
                      }
                    },
                    legend: {
                      font: { size: 13, color: '#e2e8f0', family: 'Vazirmatn, Tahoma, sans-serif' },
                      orientation: 'h',
                      y: -0.15
                    },
                    showlegend: true,
                    margin: { t: 30, r: 40, b: 65, l: 40 }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </div>
          </div>

          {/* شناسنامه تفصیلی خوشه‌ها */}
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                  شناسنامه و رفتارشناسی تخصصی خوشه‌های کالا (Cluster Profiles)
                </h2>
                <p className="text-sm text-slate-400 mt-1">
                  تحلیل دامنه قیمتی، میانگین تعامل کاربران و نرخ وفاداری استخراج‌شده از الگوریتم دو مرحله‌ای
                </p>
              </div>
              <span className="text-xs font-mono text-cyan-300 bg-cyan-950/60 px-3 py-1 rounded-lg border border-cyan-800/50">
                {toPersianNum(clusterProfiles.length)} پروفایل فعال
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {clusterProfiles.map((cp, idx) => {
                const isActive = cp.group === 'Active';
                const rate = Number(cp.rate_mean) || 0;
                const isSelected = selectedClusterId === cp.cluster;

                return (
                  <div
                    key={idx}
                    onClick={() => setSelectedClusterId(isSelected ? null : cp.cluster)}
                    className={`cursor-pointer bg-[#0b1120] border rounded-2xl p-4 space-y-3 transition-all duration-200 hover:translate-y-[-2px] ${
                      isSelected ? 'border-cyan-400 shadow-lg shadow-cyan-950/40' : 'border-slate-800/90 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between border-b border-slate-800/60 pb-2.5">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                        <h3 className="text-base font-bold text-cyan-300">{cp.title || `خوشه شماره ${cp.cluster}`}</h3>
                      </div>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-semibold border ${
                        isActive ? 'bg-teal-950 text-teal-300 border-teal-700/60' : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {isActive ? 'بخش فعال' : 'دم‌بلند'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-[#070d1a] p-2 rounded-lg border border-slate-800/70">
                        <span className="text-slate-400 block text-xs">تعداد کالا</span>
                        <strong className="text-slate-100 text-sm">{toPersianNum(cp.total_products)}</strong>
                      </div>
                      <div className="bg-[#070d1a] p-2 rounded-lg border border-slate-800/70">
                        <span className="text-slate-400 block text-xs">سهم بازار</span>
                        <strong className="text-slate-100 text-sm">{toPersianNum(cp.share_pct)}٪</strong>
                      </div>
                      <div className="bg-[#070d1a] p-2 rounded-lg border border-slate-800/70">
                        <span className="text-slate-400 block text-xs">میانه قیمت</span>
                        <strong className="text-slate-100">{toPersianNum(cp.price_median)} <span className="text-[10px] text-slate-500">تومان</span></strong>
                      </div>
                      <div className="bg-[#070d1a] p-2 rounded-lg border border-slate-800/70">
                        <span className="text-slate-400 block text-xs">میانگین امتیاز</span>
                        <strong className={`font-mono text-sm ${rate >= 3.5 ? 'text-emerald-400' : rate >= 2 ? 'text-amber-400' : 'text-rose-400'}`}>
                          {rate.toFixed(2)} ★
                        </strong>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/60 text-xs text-slate-300 space-y-1.5">
                      <div className="flex justify-between">
                        <span>دامنه قیمت:</span>
                        <span className="text-slate-300">{toPersianNum(cp.price_min)} تا {toPersianNum(cp.price_max)} تومان</span>
                      </div>
                      <div className="flex justify-between">
                        <span>میانگین تعداد نظرات به ازای کالا:</span>
                        <span className="text-slate-300">{toPersianNum(Math.round(Number(cp.rate_cnt_mean) || 0))} نظر</span>
                      </div>
                      <div className="flex justify-between">
                        <span>نرخ توصیه خریداران:</span>
                        <span className="text-cyan-300 font-semibold">{toPersianNum((Number(cp.recommendation_ratio_mean || 0) * 100).toFixed(1))}٪</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* جدول ماتریس مشخصات خوشه‌ها */}
          <div className="bg-[#0b1120] border border-slate-800/90 rounded-2xl p-5 overflow-x-auto space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>جدول ماتریس مشخصات خوشه‌ها (Cluster Feature Matrix)</h3>
              <span className="text-xs text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700/60">منبع داده: cluster_profiles.csv</span>
            </div>
            <table className="w-full text-right text-sm text-slate-200">
              <thead className="bg-[#151e33] text-slate-400 border-b border-slate-700">
                <tr>
                  <th className="py-3 px-3">شناسه</th>
                  <th className="py-3 px-3">عنوان خوشه</th>
                  <th className="py-3 px-3">گروه</th>
                  <th className="py-3 px-3">تعداد کالا</th>
                  <th className="py-3 px-3">سهم</th>
                  <th className="py-3 px-3">میانه قیمت (تومان)</th>
                  <th className="py-3 px-3">میانگین قیمت (تومان)</th>
                  <th className="py-3 px-3">امتیاز</th>
                  <th className="py-3 px-3">تعداد نظرات</th>
                  <th className="py-3 px-3">نرخ توصیه</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {clusterProfiles.map((cp, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-mono text-slate-400">{toPersianNum(cp.cluster)}</td>
                    <td className="py-3 px-3 font-medium text-cyan-300">{cp.title || `خوشه ${cp.cluster}`}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        cp.group === 'Active' ? 'bg-teal-950 text-teal-300 border border-teal-800' : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {cp.group === 'Active' ? 'فعال' : 'دم‌بلند'}
                      </span>
                    </td>
                    <td className="py-3 px-3">{toPersianNum(cp.total_products)}</td>
                    <td className="py-3 px-3 font-semibold text-slate-200">{toPersianNum(cp.share_pct)}٪</td>
                    <td className="py-3 px-3">{toPersianNum(cp.price_median)}</td>
                    <td className="py-3 px-3 text-slate-400">{toPersianNum(Math.round(Number(cp.price_mean) || 0))}</td>
                    <td className="py-3 px-3 font-bold text-amber-400">{Number(cp.rate_mean || 0).toFixed(2)}</td>
                    <td className="py-3 px-3">{toPersianNum(Math.round(Number(cp.rate_cnt_mean) || 0))}</td>
                    <td className="py-3 px-3 text-teal-300">{toPersianNum((Number(cp.recommendation_ratio_mean || 0) * 100).toFixed(1))}٪</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* تب ۳: تحلیل احساسات و نظرات (با حضور کامل و مستقل داده‌های خنثی) */}
      {activeTab === 'nlp' && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/60 text-[13px] text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0"></span>
            پایش هوشمند نظرات، تحلیل سه‌گانه احساسات (مثبت، خنثی، منفی) به تفکیک جنبه‌ها و ابر واژگان کلیدی.
          </div>

          <CollapsibleSection
            title="شاخص سلامت جنبه‌های کالا و توزیع سه‌گانه احساسات (Aspect Sentiment: Positive / Neutral / Negative)"
            isOpen={openAspects}
            onToggle={() => setOpenAspects(!openAspects)}
          >
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-1">
              {/* ۱. نمودار دونات: توزیع سه‌گانه احساسات خریداران */}
              <div className="lg:col-span-5 bg-[#080e1c] border border-slate-800/80 rounded-2xl p-4 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-100 mb-1">توزیع سه‌گانه احساسات خریداران</h3>
                  <p className="text-[11px] text-slate-400">سهم درصدی نظرات مثبت، خنثی و منفی در کاتالوگ</p>
                </div>

                <div className="h-56">
                  <SafePlot
                    data={[{
                      type: 'pie',
                      hole: 0.65,
                      labels: ['نظرات مثبت', 'نظرات خنثی و توصیفی', 'نظرات منفی'],
                      values: [nlpSummary.Positive, nlpSummary.Neutral, nlpSummary.Negative],
                      marker: {
                        colors: ['#22c55e', '#64748b', '#ef4444']
                      },
                      textinfo: 'percent',
                      textposition: 'inside',
                      textfont: { size: 15, color: '#ffffff', family: 'Vazirmatn, Tahoma' },
                      hovertemplate: '%{label}<br>تعداد: %{value:,}<br>سهم: %{percent}<extra></extra>'
                    }]}
                    layout={{
                      ...defaultPlotLayout,
                      showlegend: true,
                      legend: {
                        orientation: 'h',
                        y: -0.18,
                        x: 0.5,
                        xanchor: 'center',
                        font: { size: 14, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' }
                      },
                      margin: { t: 10, r: 10, b: 35, l: 10 }
                    }}
                    style={{ width: '100%', height: '100%' }}
                    config={{ displayModeBar: false, responsive: true }}
                  />
                </div>

                {/* کارت‌های متنی آمار زیر دونات شامل داده خنثی */}
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/60 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-emerald-400 block font-semibold">مثبت</span>
                    <strong className="text-slate-100">{toPersianNum(nlpSummary.Positive)}</strong>
                    <span className="text-[10px] text-slate-500 block font-mono">({toPersianNum(nlpSummary.positive_pct)}٪)</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block font-semibold">خنثی / میانه</span>
                    <strong className="text-slate-100">{toPersianNum(nlpSummary.Neutral)}</strong>
                    <span className="text-[10px] text-slate-500 block font-mono">({toPersianNum(nlpSummary.neutral_pct)}٪)</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-rose-400 block font-semibold">منفی</span>
                    <strong className="text-slate-100">{toPersianNum(nlpSummary.Negative)}</strong>
                    <span className="text-[10px] text-slate-500 block font-mono">({toPersianNum(nlpSummary.negative_pct)}٪)</span>
                  </div>
                </div>
              </div>

              {/* ۲. سهم بازخورد به تفکیک جنبه‌های کالا شامل داده‌های خنثی */}
              <div className="lg:col-span-7 bg-[#080e1c] border border-slate-800/80 rounded-2xl p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-sm font-bold text-slate-100">سهم بازخورد به تفکیک جنبه‌های کالا (Aspects)</h3>
                    <span className="text-[10px] text-slate-500">منبع: nlp_aspects.csv</span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-slate-400 mb-2">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400"></span> مثبت</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-500"></span> خنثی (معمولی/توصیفی)</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span> منفی</span>
                  </div>
                </div>

                <div className="space-y-3">
                  {nlpAspects.map((asp, idx) => (
                    <div key={idx} className="bg-[#0c1424] p-2.5 rounded-xl border border-slate-800/70">
                      <div className="flex items-center justify-between text-xs mb-1.5">
                        <span className="font-bold text-cyan-300">{asp.aspect}</span>
                        <div className="flex items-center gap-2 text-[11px] font-mono">
                          <span className="text-emerald-400 font-semibold">{toPersianNum(asp.positive_pct)}٪ مثبت</span>
                          <span className="text-slate-400 font-semibold">· {toPersianNum(asp.neutral_pct)}٪ خنثی</span>
                          <span className="text-rose-400 font-semibold">· {toPersianNum(asp.negative_pct)}٪ منفی</span>
                        </div>
                      </div>

                      {/* نوار پیشرفت ۳ رنگی (سبز / طوسی خنثی / قرمز) */}
                      <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden flex">
                        <div 
                          className="bg-emerald-400 transition-all duration-500" 
                          style={{ width: `${asp.positive_pct}%` }}
                          title={`مثبت: ${asp.positive_pct}٪`}
                        ></div>
                        <div 
                          className="bg-slate-500 transition-all duration-500" 
                          style={{ width: `${asp.neutral_pct}%` }}
                          title={`خنثی: ${asp.neutral_pct}٪`}
                        ></div>
                        <div 
                          className="bg-rose-500 transition-all duration-500" 
                          style={{ width: `${asp.negative_pct}%` }}
                          title={`منفی: ${asp.negative_pct}٪`}
                        ></div>
                      </div>

                      <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                        <span>{toPersianNum(asp.positive_count)} نظر مثبت</span>
                        <span className="text-slate-400 font-medium">{toPersianNum(asp.neutral_count)} نظر خنثی</span>
                        <span>{toPersianNum(asp.negative_count)} نظر منفی</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CollapsibleSection>

          {/* ابر کلمات ۳۰ تایی واقعی */}
          <CollapsibleSection
            title="ابر کلمات استخراج‌شده از نظرات خریداران"
            isOpen={openWordCloud}
            onToggle={() => setOpenWordCloud(!openWordCloud)}
          >
            <RealWordCloud toPersianNum={toPersianNum} />
          </CollapsibleSection>

          {/* ماتریس درهم‌ریختگی مدل NLP */}
          <CollapsibleSection
            title="ماتریس درهم‌ریختگی مدل تحلیل احساسات (Confusion Matrix)"
            isOpen={openConfusion}
            onToggle={() => setOpenConfusion(!openConfusion)}
          >
            <div className="h-80">
              {nlpEval && nlpEval.confusion_matrix ? (
                <SafePlot
                  data={[{
                    type: 'heatmap',
                    z: nlpEval.confusion_matrix,
                    x: ['پیش‌بینی: منفی', 'پیش‌بینی: خنثی', 'پیش‌بینی: مثبت'],
                    y: ['واقعی: منفی', 'واقعی: خنثی', 'واقعی: مثبت'],
                    text: nlpEval.confusion_matrix.map(row => row.map(v => toPersianNum(v))),
                    texttemplate: '%{text}',
                    textfont: { size: 15, color: '#f8fafc', family: 'Vazirmatn, Tahoma' },
                    colorscale: [
                      [0, '#0b1329'],
                      [0.2, '#0f2942'],
                      [0.5, '#0e7490'],
                      [0.8, '#06b6d4'],
                      [1, '#22d3ee']
                    ],
                    showscale: true,
                    colorbar: { tickfont: { size: 11, color: '#94a3b8' }, thickness: 12 }
                  }]}
                  layout={{
                    ...defaultPlotLayout,
                    margin: { t: 30, r: 50, b: 65, l: 110 },
                    xaxis: { tickfont: { size: 14, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' }, side: 'bottom', showgrid: false },
                    yaxis: { tickfont: { size: 14, color: '#e2e8f0', family: 'Vazirmatn, Tahoma' }, showgrid: false, autorange: 'reversed' }
                  }}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              ) : (
                <div className="text-center text-slate-500 py-16 text-sm">
                  ماتریس ارزیابی برای این مدل بارگذاری نشده است.
                </div>
              )}
            </div>
          </CollapsibleSection>
        </div>
      )}

      {/* تب ۴: مانیتورینگ سیستم و مدل */}
      {activeTab === 'monitoring' && (
        <MonitoringTab
          defaultPlotLayout={defaultPlotLayout}
          nlpEval={nlpEval}
          clusters={clusters}
          toPersianNum={toPersianNum}
        />
      )}

      {/* تب ۵: شبیه‌سازی کافکا */}
      {activeTab === 'simulation' && (
        <SimulationTab />
      )}

      <ChatWidget />
    </div>
  );
}
