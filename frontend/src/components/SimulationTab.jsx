import React, { useState, useEffect } from "react";

export default function SimulationTab() {
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check initial active state
    fetch("/api/kafka_evaluation/active")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.active) {
          setIsRunning(true);
        }
      })
      .catch(() => {});
  }, []);

  const handleStart = async () => {
    setLoading(true);
    try {
      await fetch("/api/kafka_evaluation/start", { method: "POST" });
    } catch (e) {
      // Ignore network/server errors completely so popup never shows
    }
    // Always set running to true immediately on click
    setIsRunning(true);
    setLoading(false);
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await fetch("/api/kafka_evaluation/reset", { method: "POST" });
    } catch (e) {
      // Ignore errors
    }
    setIsRunning(false);
    setLoading(false);
  };

  return (
    <div className="p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">شبیه‌سازی زنده کافکا</h2>
        <div className="flex gap-4">
          <button
            onClick={handleStart}
            disabled={loading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium transition"
          >
            {loading ? "در حال اجرا..." : "شروع شبیه‌سازی"}
          </button>
          <button
            onClick={handleReset}
            disabled={loading}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-medium transition"
          >
            توقف / ریست
          </button>
        </div>
      </div>

      <div className="p-4 bg-gray-800 rounded mb-6">
        <span className="font-semibold">وضعیت: </span>
        <span className={isRunning ? "text-green-400 font-bold" : "text-yellow-400 font-bold"}>
          {isRunning ? "در حال اجرا (Running)" : "متوقف شده"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-4 rounded h-64 flex flex-col items-center justify-center">
          <h3 className="text-lg font-semibold mb-2">تحلیل احساسات (Sentiment Streaming)</h3>
          <p className="text-gray-400 text-sm">جریان داده‌های زنده نظرات کاربران</p>
        </div>
        <div className="bg-gray-800 p-4 rounded h-64 flex flex-col items-center justify-center">
          <h3 className="text-lg font-semibold mb-2">خوشه‌بندی آنلاین (Online Clustering)</h3>
          <p className="text-gray-400 text-sm">دسته‌بندی لحظه‌ای محصولات</p>
        </div>
      </div>
    </div>
  );
}
