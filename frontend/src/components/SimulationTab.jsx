import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

// رنگ‌بندی تفکیک‌شده ۶ خوشه
const CLUSTER_COLORS = {
  0: "#3B82F6", // آبی
  1: "#EF4444", // قرمز (کالاهای فعال خاص / پرت)
  2: "#10B981", // سبز زمردی
  3: "#F59E0B", // کهربایی
  4: "#8B5CF6", // بنفش
  5: "#EC4899"  // صورتی
};

const CLUSTER_TITLES = {
  0: "کالاهای فعال (تعامل بالا/متوسط)",
  1: "کالاهای خاص/پرت (پربازدید یا لوکس)",
  2: "کالاهای استاندارد و پایدار",
  3: "کالاهای پرفروش و رضایت بالا",
  4: "کالاهای متوسط با پتانسیل رشد",
  5: "کالاهای کم‌بازدید یا تخصصی"
};

const SENTIMENT_COLORS = {
  positive: "#10B981", // سبز
  neutral: "#F59E0B",  // زرد/نارنجی
  negative: "#EF4444"  // قرمز
};

const SENTIMENT_TITLES = {
  positive: "مثبت (Positive)",
  neutral: "خنثی (Neutral)",
  negative: "منفی (Negative)"
};

export default function SimulationTab() {
  const [evalId, setEvalId] = useState(() => {
    const saved = localStorage.getItem("kafka_eval_id");
    return saved ? parseInt(saved, 10) : null;
  });
  const [status, setStatus] = useState("idle");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const pollTimerRef = useRef(null);

  // بررسی وضعیت فعال در لود اولیه
  useEffect(() => {
    const checkActive = async () => {
      try {
        const res = await axios.get("/api/kafka_evaluation/active");
        if (res.data.eval_id && res.data.status === "running") {
          setEvalId(res.data.eval_id);
          setStatus("running");
          localStorage.setItem("kafka_eval_id", res.data.eval_id.toString());
        } else {
          setStatus("idle");
        }
      } catch (err) {
        console.error("Error checking active simulation:", err);
      }
    };
    checkActive();
  }, []);

  // مکانیسم Polling
  useEffect(() => {
    if (!evalId) return;

    const fetchStatus = async () => {
      try {
        const res = await axios.get(`/api/kafka_evaluation/status/${evalId}`);
        setData(res.data);
        if (res.data.status) {
          setStatus(res.data.status);
        }
        if (res.data.status === "stopped") {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
        }
      } catch (err) {
        console.error("Error fetching simulation status:", err);
      }
    };

    fetchStatus();
    pollTimerRef.current = setInterval(fetchStatus, 2000);

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [evalId]);

  const handleStart = async () => {
    setLoading(true);
    // صفر کردن UI قبل از شروع run جدید
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    setData(null);
    setStatus("idle");
    try {
      const res = await axios.post("http://localhost:8000/api/kafka_evaluation/start");
      setEvalId(res.data.eval_id);
      setStatus("running");
      localStorage.setItem("kafka_eval_id", res.data.eval_id.toString());
    } catch (err) {
      console.error("Error starting simulation:", err);
      alert("خطا در شروع شبیه‌سازی کافکا.");
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    if (!evalId && status !== "running") return;
    setLoading(true);
    try {
      if (evalId) {
        await axios.post(`http://localhost:8000/api/kafka_evaluation/stop/${evalId}`);
      }
    } catch (err) {
      console.error("Error stopping simulation:", err);
    } finally {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
      setData(null);
      setStatus("stopped");
      setLoading(false);
    }
  };

  // داده‌های نمودار احساسات
  const sentimentDistribution = data?.sentiment_distribution || [];
  const sentLabels = sentimentDistribution.map(d => {
    const key = String(d.sentiment || "").toLowerCase();
    return SENTIMENT_TITLES[key] || d.sentiment;
  });
  const sentValues = sentimentDistribution.map(d => Number(d.count) || 0);
  const sentColors = sentimentDistribution.map(d => {
    const key = String(d.sentiment || "").toLowerCase();
    return SENTIMENT_COLORS[key] || "#6B7280";
  });

  // داده‌های نمودار خوشه‌بندی
  const clusteringDistribution = data?.clustering_distribution || [];
  const clusterLabels = clusteringDistribution.map(d => CLUSTER_TITLES[d.cluster] || `خوشه ${d.cluster}`);
  const clusterValues = clusteringDistribution.map(d => d.count);
  const clusterColors = clusteringDistribution.map(d => CLUSTER_COLORS[d.cluster] || "#94A3B8");

  const sentMsgs = data?.sentiment_stats?.messages || 0;
  const clustMsgs = data?.clustering_stats?.messages || 0;

  return (
    <div className="space-y-8 p-6 bg-slate-950 min-h-screen text-slate-100" dir="rtl">

      {/* هدر کنترل شبیه‌سازی */}
      <div className="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl gap-4">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <span></span> (Kafka Stream)</h2>
        </div>

        {/* دکمه‌های کنترل */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleStart}
            disabled={loading || status === "running"}
            className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 shadow-lg flex items-center gap-2 ${
              status === "running"
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                : "bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white shadow-emerald-950/50"
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse"></span>
            Start Simulated
          </button>

          <button
            onClick={handleStop}
            disabled={loading || (status !== "running" && !evalId)}
            className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 shadow-lg flex items-center gap-2 ${
              status !== "running"
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                : "bg-rose-600 hover:bg-rose-500 active:scale-95 text-white shadow-rose-950/50"
            }`}
          >
            <span>⏹</span>
            Stop Simulated
          </button>

          <button
            type="button"
            onClick={async (e) => {
              e.preventDefault();
              console.log("RESET 1 CLICKED");
              setLoading(true);
              try {
                if (evalId) {
                  try {
                    await axios.post(`http://localhost:8000/api/kafka_evaluation/stop/${evalId}`);
                  } catch (e) {
                    console.warn("stop before reset:", e);
                  }
                }
                await axios.post("http://localhost:8000/api/kafka_evaluation/reset");
              } catch (err) {
                console.error("reset error:", err);
              } finally {
                if (pollTimerRef.current) {
                  clearInterval(pollTimerRef.current);
                  pollTimerRef.current = null;
                }
                setData(null);
                setEvalId(null);
                setStatus("idle");
                localStorage.removeItem("kafka_eval_id");
                setLoading(false);
                console.log("Reset completed successfully");
              }
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg shadow transition flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Reset Simulation
          </button>

          <button
            type="button"
            onClick={async (e) => {
              e.preventDefault();
              console.log("RESET 2 CLICKED");
              setLoading(true);
              try {
                if (evalId) {
                  try {
                    await axios.post(`http://localhost:8000/api/kafka_evaluation/stop/${evalId}`);
                  } catch (e) {
                    console.warn("stop before reset:", e);
                  }
                }
                await axios.post("http://localhost:8000/api/kafka_evaluation/reset");
              } catch (err) {
                console.error("reset error:", err);
              } finally {
                if (pollTimerRef.current) {
                  clearInterval(pollTimerRef.current);
                  pollTimerRef.current = null;
                }
                setData(null);
                setEvalId(null);
                setStatus("idle");
                localStorage.removeItem("kafka_eval_id");
                setLoading(false);
                console.log("Reset completed successfully");
              }
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg shadow transition flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Reset Simulation
          </button>
        </div>
      </div>

      {/* وضعیت فعلی */}
      <div className="flex items-center justify-between px-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">وضعیت فرآیند:</span>
          {status === "running" && (
            <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              در حال اجرای شبیه‌سازی (Running)
            </span>
          )}
          {status === "stopped" && (
            <span className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-3 py-1 rounded-full font-semibold">
              متوقف شده (Stopped)
            </span>
          )}
          {status === "idle" && (
            <span className="bg-slate-800 border border-slate-700 text-slate-400 px-3 py-1 rounded-full font-semibold">
              آماده شروع (Idle)
            </span>
          )}
        </div>
        {evalId && (
          <span className="text-slate-500 font-mono text-xs">Run ID: #{evalId}</span>
        )}
      </div>

      {/* ========================================================= */}
      {/* بخش اول: تحلیل احساسات نظرات */}
      {/* ========================================================= */}
      <section className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="text-lg font-extrabold text-emerald-400 flex items-center gap-2">
                <span></span> (Sentiment Streaming)</h3>
            </div>
            <div className="bg-slate-900 border border-slate-800 px-6 py-3 rounded-xl text-center self-stretch sm:self-auto min-w-[180px]">
              <span className="text-xs text-slate-400 font-medium block">تعداد کل پیام‌های احساسات</span>
              <span className="text-2xl font-black text-emerald-400 font-mono mt-0.5 block">
                {sentMsgs.toLocaleString("fa-IR")}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-slate-950 border border-slate-800/90 rounded-2xl p-4 shadow-inner">
          <Plot
            data={[
              {
                x: sentLabels,
                y: sentValues,
                type: "bar",
                marker: {
                  color: sentColors,
                  line: { color: "#1E293B", width: 1.5 }
                },
                text: sentValues.map(v => v.toLocaleString("fa-IR")),
                textposition: "outside",
                textfont: { size: 14, color: "#F8FAFC", family: "Vazirmatn, Tahoma, sans-serif" }
              }
            ]}
            layout={{
              autosize: true,
              height: 380,
              paper_bgcolor: "transparent",
              plot_bgcolor: "transparent",
              margin: { t: 30, r: 25, l: 45, b: 50 },
              xaxis: {
                tickfont: { size: 13, color: "#CBD5E1", family: "Vazirmatn, Tahoma, sans-serif" },
                gridcolor: "#1E293B"
              },
              yaxis: {
                tickfont: { size: 12, color: "#94A3B8" },
                gridcolor: "#334155",
                zerolinecolor: "#475569"
              }
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: "100%" }}
          />
        </div>
      </section>

      {/* ========================================================= */}
      {/* بخش دوم: خوشه‌بندی برخط کالاها */}
      {/* ========================================================= */}
      <section className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="text-lg font-extrabold text-blue-400 flex items-center gap-2">
                <span></span> (Online Clustering 6-Cluster)</h3>
            </div>
            <div className="bg-slate-900 border border-slate-800 px-6 py-3 rounded-xl text-center self-stretch sm:self-auto min-w-[180px]">
              <span className="text-xs text-slate-400 font-medium block">تعداد کل کالاهای پردازش‌شده</span>
              <span className="text-2xl font-black text-blue-400 font-mono mt-0.5 block">
                {clustMsgs.toLocaleString("fa-IR")}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-slate-950 border border-slate-800/90 rounded-2xl p-4 shadow-inner">
          <Plot
            data={[
              {
                x: clusterLabels,
                y: clusterValues,
                type: "bar",
                marker: {
                  color: clusterColors,
                  line: { color: "#1E293B", width: 1.5 }
                },
                text: clusterValues.map(v => v.toLocaleString("fa-IR")),
                textposition: "outside",
                textfont: { size: 14, color: "#F8FAFC", family: "Vazirmatn, Tahoma, sans-serif" }
              }
            ]}
            layout={{
              autosize: true,
              height: 420,
              paper_bgcolor: "transparent",
              plot_bgcolor: "transparent",
              margin: { t: 30, r: 25, l: 45, b: 85 },
              xaxis: {
                tickfont: { size: 12, color: "#CBD5E1", family: "Vazirmatn, Tahoma, sans-serif" },
                tickangle: -15,
                gridcolor: "#1E293B"
              },
              yaxis: {
                tickfont: { size: 12, color: "#94A3B8" },
                gridcolor: "#334155",
                zerolinecolor: "#475569"
              }
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: "100%" }}
          />
        </div>
      </section>

    </div>
  );
}
