import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for voice functionality
 */
export function useVoice() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);

  // Check support on mount
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynth = window.speechSynthesis;

    if (!SpeechRecognition || !speechSynth) {
      setIsSupported(false);
      console.warn('⚠️ Speech recognition/synthesis not supported in this browser');
    }
  }, []);

  // Initialize speech recognition
  const initRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-GB';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onresult = (event) => {
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
        setIsListening(false);
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    return recognition;
  }, []);

  // Start listening
  const startListening = useCallback((onResult) => {
    if (!isSupported) {
      console.warn('Speech recognition not supported');
      return false;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {}
    }

    const recognition = initRecognition();
    if (!recognition) return false;

    recognitionRef.current = recognition;

    // Override the onresult to include callback
    recognition.onresult = (event) => {
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
      if (finalText && onResult) {
        onResult(finalText);
        setIsListening(false);
      }
    };

    try {
      recognition.start();
      setIsListening(true);
      setTranscript('');
      return true;
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
      return false;
    }
  }, [isSupported, initRecognition]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {}
    }
    setIsListening(false);
  }, []);

  // Speak text with British voice
  const speak = useCallback((text, options = {}) => {
    const synth = window.speechSynthesis;
    if (!synth || !text) return;

    // Cancel any ongoing speech
    if (synth.speaking) {
      synth.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);

    // Find a British voice
    const voices = synth.getVoices();
    const britishVoice = voices.find(v =>
      /en-GB/i.test(v.lang) &&
      /male|Daniel|Oliver|Arthur|George|Google UK English Male|Microsoft George/i.test(v.name)
    ) || voices.find(v => /en-GB/i.test(v.lang));

    if (britishVoice) {
      utterance.voice = britishVoice;
    }

    utterance.lang = 'en-GB';
    utterance.rate = options.rate || 0.92;
    utterance.pitch = options.pitch || 0.9;
    utterance.volume = options.volume || 1;

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
    };

    utteranceRef.current = utterance;

    setTimeout(() => {
      synth.speak(utterance);
    }, 100);
  }, []);

  // Cancel speech
  const cancelSpeech = useCallback(() => {
    const synth = window.speechSynthesis;
    if (synth) {
      synth.cancel();
    }
    setIsSpeaking(false);
  }, []);

  return {
    isListening,
    isSpeaking,
    transcript,
    isSupported,
    startListening,
    stopListening,
    speak,
    cancelSpeech,
  };
}