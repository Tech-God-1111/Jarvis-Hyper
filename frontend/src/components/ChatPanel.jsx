import React, { useEffect, useRef } from 'react';

export default function ChatPanel({
  messages,
  input,
  setInput,
  sendMessage,
  busy,
  isListening
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden">
      <div
        className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-2"
        style={{
          height: '100%',
          maxHeight: '100%',
          minHeight: 0,
          overflowY: 'auto',
          scrollBehavior: 'smooth',
        }}
      >
        {messages.length === 0 && (
          <div className="text-cyan-400/10 text-center text-[10px] font-mono mt-20">
            <div className="text-4xl mb-2">🤖</div>
            <div>JARVIS-HYPER ready</div>
            <div className="text-[8px] text-cyan-400/5 mt-1">Speak or type a command</div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-message flex items-start gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}
          >
            <div className={`max-w-[90%] px-3 py-1.5 font-mono text-[10px] leading-relaxed break-words ${
              msg.role === 'user' 
                ? 'bg-amber-500/5 border border-amber-500/10 text-amber-300/60' 
                : 'bg-cyan-500/5 border border-cyan-500/10 text-cyan-300/70'
            }`}>
              {msg.streaming ? (
                <span>
                  {msg.content}
                  <span className="term-caret" />
                </span>
              ) : (
                msg.content || '...'
              )}
            </div>
          </div>
        ))}

        {busy && !messages.some(m => m.streaming) && (
          <div className="text-cyan-400/20 text-[8px] font-mono animate-pulse pl-2">JARVIS is thinking...</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-cyan-500/5 p-2 flex items-center gap-2 bg-[#050810]">
        <div className="flex-1 flex items-center bg-black/50 border border-cyan-500/5 px-2">
          <span className="text-cyan-500/20 text-[10px] mr-1">›</span>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isListening ? '🎤 listening...' : busy ? '...' : 'input...'}
            disabled={busy}
            className="flex-1 bg-transparent outline-none py-1 text-cyan-100/50 placeholder:text-cyan-400/10 font-mono text-[10px]"
          />
        </div>
        <button
          onClick={() => sendMessage(input)}
          disabled={busy || !input.trim()}
          className="px-3 py-1 border border-cyan-400/20 bg-cyan-500/5 hover:bg-cyan-500/10 disabled:opacity-20 text-cyan-300/50 text-[8px] tracking-widest font-mono transition-all"
        >
          SEND
        </button>
      </div>
    </div>
  );
}