import React, { useRef, useState } from 'react';
import { toast } from 'sonner';

export default function DataPanel({ onAttach }) {
  const fileRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [filename, setFilename] = useState('');
  const [output, setOutput] = useState('');
  const [busy, setBusy] = useState(false);

  const handleFile = async (file) => {
    if (!file) return;
    if (file.size > 800_000) {
      toast.error('File exceeds 800KB, sir.');
      return;
    }

    setFilename(file.name);
    setOutput('');
    setBusy(true);

    try {
      const text = await file.text();

      // Show quick stats
      const lines = text.split('\n').length;
      const words = text.split(/\s+/).length;
      setOutput(
        `📊 FILE ANALYSIS\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `📁 Name: ${file.name}\n` +
        `📏 Size: ${(file.size / 1024).toFixed(1)} KB\n` +
        `📄 Lines: ${lines}\n` +
        `📝 Words: ${words}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `✅ Attached to next chat message.`
      );

      // 🔥 SEND THE FILE TO THE PARENT (HyperPage)
      if (onAttach) {
        onAttach({
          name: file.name,
          mime: file.type || 'text/plain',
          content: text,     // ← actual file contents!
        });
      }
      toast.success(`${file.name} attached`);
    } catch (err) {
      toast.error('Could not read file');
    } finally {
      setBusy(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="p-3 h-full flex flex-col gap-2 font-mono text-[10px]">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        className={`cursor-pointer border-2 border-dashed p-4 text-center transition-all ${
          dragOver
            ? 'border-amber-400 bg-amber-400/5 text-amber-300'
            : 'border-cyan-500/20 bg-cyan-500/5 text-cyan-300/60 hover:border-cyan-400/40'
        }`}
      >
        <div className="text-cyan-300 mb-1">⌬ DROP DATA</div>
        <div className="text-cyan-400/40 text-[8px] tracking-widest">
          CSV · JSON · TXT · LOG · XML · MD
        </div>
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          accept=".csv,.json,.txt,.md,.log,.xml,.yaml,.yml"
          onChange={(e) => e.target.files.length && handleFile(e.target.files[0])}
        />
      </div>

      <div className="text-[8px] text-cyan-400/40 tracking-widest">
        {filename ? `FILE: ${filename}` : 'AWAITING INPUT'}
        {busy && <span className="text-amber-400 animate-pulse ml-2">⌬ ANALYZING</span>}
      </div>

      <div className="flex-1 min-h-0 border border-cyan-500/5 bg-black/40 p-2 overflow-auto whitespace-pre-wrap text-cyan-200/70 text-[9px]">
        {output || <span className="text-cyan-400/20">// drop a file...</span>}
      </div>
    </div>
  );
}