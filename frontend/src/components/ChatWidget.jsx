import React, { useState, useEffect, useRef } from 'react';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'سلام! من دستیار هوشمند دیجی‌کالا هستم. در جستجو و پیشنهاد محصولات چطور می‌توانم کمکتان کنم؟'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(() => {
    return localStorage.getItem('assistant_conversation_id') || '';
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (e) => {
    e?.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    const newMessages = [...messages, { sender: 'user', text: query }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const isViteDev = window.location.port === '5173';
      const baseUrl = isViteDev ? 'http://127.0.0.1:8000/api' : '/api';
      const headers = { 'Content-Type': 'application/json' };
      if (conversationId) {
        headers['conversation-id'] = conversationId;
      }

      const res = await fetch(`${baseUrl}/assistant/recommend`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query })
      });

      if (!res.ok) throw new Error(`خطای سرور: ${res.status}`);

      const data = await res.json();

      if (data.conversation_id && data.conversation_id !== conversationId) {
        setConversationId(data.conversation_id);
        localStorage.setItem('assistant_conversation_id', data.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: data.reply || 'پاسخی دریافت نشد.' }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: 'متأسفانه در برقراری ارتباط با دستیار خطایی رخ داد. لطفاً اتصال بک‌اند و Redis را بررسی کنید.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 left-5 z-50 font-sans" dir="rtl">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-3 px-5 py-3.5 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white rounded-full shadow-xl shadow-cyan-950/50 border border-cyan-400/30 transition-all transform hover:scale-105 active:scale-95"
          aria-label="گفتگو با دستیار هوشمند"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="text-base font-bold">دستیار هوشمند</span>
        </button>
      )}

      {isOpen && (
        <div className="w-[480px] sm:w-[520px] h-[75vh] max-h-[720px] bg-[#0b1120] border border-cyan-900/50 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
          {/* Header */}
          <div className="px-5 py-4 bg-[#0d1629] border-b border-slate-800 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
              <div>
                <h3 className="text-base font-bold text-white">دستیار هوشمند دیجی‌کالا</h3>
                <p className="text-xs text-cyan-400/90">پاسخ‌گوی آنلاین پیشنهاد محصول</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition"
              aria-label="بستن"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-[#070b14]/80">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[90%] text-[15px] leading-7 px-4 py-3 rounded-2xl whitespace-pre-line shadow ${
                    msg.sender === 'user'
                      ? 'bg-cyan-600 text-white rounded-br-md'
                      : 'bg-[#151e33] border border-slate-800 text-slate-100 rounded-bl-md'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-sm text-cyan-400 bg-[#151e33] border border-slate-800 px-4 py-3 rounded-2xl w-fit">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]"></span>
                <span className="mr-1">در حال بررسی و پیشنهاد...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSend} className="p-4 bg-[#0d1629] border-t border-slate-800 flex gap-3 shrink-0">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="مثلاً: یک هدفون خوب برای بازی پیشنهاد بده..."
              className="flex-1 bg-[#151e33] text-[15px] text-slate-100 placeholder-slate-500 px-4 py-3 rounded-xl border border-slate-700/80 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-white px-5 py-3 rounded-xl text-[15px] font-semibold transition"
            >
              ارسال
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
