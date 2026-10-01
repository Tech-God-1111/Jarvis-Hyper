import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

export default function VoiceButton({ onVoiceInput, isListening, setIsListening, isSpeaking }) {
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      toast.warning('Speech recognition not supported in this browser');
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = 'en-GB';
    recognitionRef.current.interimResults = true;
    recognitionRef.current.continuous = false;

    recognitionRef.current.onresult = (event) => {
      let finalText = '';
      let interimText = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalText += event.results[i][0].transcript;
        } else {
          interimText += event.results[i][0].transcript;
        }
      }
      const text = finalText || interimText;
      setTranscript(text);
      if (finalText) {
        onVoiceInput(finalText);
        setIsListening(false);
        setTranscript('');
      }
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech error:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        toast.error('Microphone access denied, sir.');
      }
    };

    recognitionRef.current.onend = () => {
      setIsListening(false);
    };

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, []);

  const toggleListening = () => {
    if (!isSupported) {
      toast.error('Speech recognition not supported');
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.abort();
      } catch (e) {}
      setIsListening(false);
      return;
    }

    try {
      recognitionRef.current?.start();
      setIsListening(true);
      setTranscript('');
      toast.info('🎤 Listening...');
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-2 w-full h-full">
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleListening}
        className={`relative w-16 h-16 rounded-full border-2 transition-all flex items-center justify-center ${
          isListening 
            ? 'border-rose-400 bg-rose-500/10 shadow-[0_0_30px_rgba(244,63,94,0.3)]' 
            : isSpeaking 
              ? 'border-amber-400 bg-amber-500/10 shadow-[0_0_30px_rgba(251,191,36,0.2)]'
              : 'border-cyan-400/30 bg-cyan-500/5 hover:border-cyan-400/60 hover:bg-cyan-500/10'
        }`}
        disabled={!isSupported}
      >
        <AnimatePresence mode="wait">
          {isListening ? (
            <motion.div
              key="listening"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="absolute inset-0 rounded-full bg-rose-400/20 animate-ping"
            />
          ) : null}
        </AnimatePresence>

        <span className="text-2xl relative z-10">
          {isListening ? '🎤' : isSpeaking ? '🔊' : '🎙️'}
        </span>
      </motion.button>

      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="text-[8px] text-cyan-400/40 font-mono tracking-widest text-center"
          >
            {transcript || 'LISTENING...'}
          </motion.div>
        )}
        {isSpeaking && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="text-[8px] text-amber-400/40 font-mono tracking-widest"
          >
            JARVIS SPEAKING...
          </motion.div>
        )}
        {!isListening && !isSpeaking && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[7px] text-cyan-400/15 font-mono tracking-widest"
          >
            {isSupported ? 'TAP TO SPEAK' : '❌ NOT SUPPORTED'}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}