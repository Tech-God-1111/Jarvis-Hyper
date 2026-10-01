import React from 'react';

export default function Layout({ children }) {
  return (
    <div className="flex flex-col h-full w-full bg-[#050810] overflow-hidden">
      {/* Scanlines overlay */}
      <div className="scanlines" />

      {/* Ambient glow */}
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Top Bar - template.html style */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-cyan-500/5 bg-[#0a0e1a]/80 z-10 min-h-[44px]">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_12px_#00F0FF]" />
          <span className="text-cyan-400 text-sm tracking-[0.3em] font-bold" style={{ fontFamily: "'Orbitron', monospace" }}>
            JARVIS-HYPER
          </span>
          <span className="text-[8px] text-cyan-400/20 tracking-widest">v1.0</span>
        </div>
        <div className="flex items-center gap-4 text-[8px] text-cyan-400/30 font-mono tracking-widest">
          <span className="text-emerald-400/50">● ONLINE</span>
          <span>|</span>
          <span>ELEVENLABS</span>
          <span>|</span>
          <span>GROQ</span>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {children}
      </div>

      {/* Bottom Bar - template.html style */}
      <footer className="flex-shrink-0 border-t border-cyan-500/5 bg-[#0a0e1a]/80 px-4 py-1 flex items-center justify-between z-10">
        <span className="text-[7px] text-cyan-400/15 font-mono tracking-widest">◤ ALL SYSTEMS NOMINAL ◢</span>
        <span className="text-[7px] text-cyan-400/10 font-mono">JARVIS-HYPER v1.0 • STARK INDUSTRIES</span>
      </footer>
    </div>
  );
}