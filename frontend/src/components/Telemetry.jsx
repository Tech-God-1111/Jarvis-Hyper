import React, { useState, useEffect } from 'react';

export default function Telemetry() {
  const [stats, setStats] = useState({ cpu: 12, memory: 34, uptime: '00:00' });

  useEffect(() => {
    const interval = setInterval(() => {
      setStats({
        cpu: Math.floor(Math.random() * 30) + 10,
        memory: Math.floor(Math.random() * 40) + 30,
        uptime: new Date().toLocaleTimeString('en-GB', { hour12: false })
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const metrics = [
    { label: 'CPU', value: `${stats.cpu}%`, color: 'cyan' },
    { label: 'MEM', value: `${stats.memory}%`, color: 'cyan' },
    { label: 'UPTIME', value: stats.uptime, color: 'cyan' },
  ];

  return (
    <div className="p-3 h-full flex flex-col gap-2">
      <div className="grid grid-cols-3 gap-1">
        {metrics.map((m, i) => (
          <div key={i} className="border border-cyan-500/5 bg-cyan-500/3 px-2 py-1.5 text-center">
            <div className="text-[6px] text-cyan-400/20 uppercase tracking-widest">{m.label}</div>
            <div className={`text-[11px] font-bold text-${m.color}-300/60`}>{m.value}</div>
          </div>
        ))}
      </div>

      <div className="flex-1 border-t border-cyan-500/5 pt-2 space-y-1">
        {[
          { label: 'UPLINK', value: 'STABLE' },
          { label: 'VOICE', value: 'READY' },
          { label: 'MODEL', value: 'GROQ' },
        ].map((item, i) => (
          <div key={i} className="flex items-center justify-between text-[7px] font-mono tracking-widest border-b border-cyan-500/5 py-0.5">
            <span className="text-cyan-400/20">{item.label}</span>
            <span className="text-cyan-300/40">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}