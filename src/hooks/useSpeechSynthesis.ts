import { useState, useEffect, useCallback, useRef } from 'react'

export function useSpeechSynthesis() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Clean up synthesis on unmount
  useEffect(() => {
    return () => {
      if (isSupported) {
        try {
          window.speechSynthesis.cancel()
        } catch {
          // ignore
        }
      }
    }
  }, [isSupported])

  const speak = useCallback(
    (text: string, onFinish?: () => void) => {
      if (!isSupported || !text.trim()) return

      try {
        window.speechSynthesis.cancel() // Stop any ongoing speech

        const utterance = new SpeechSynthesisUtterance(text.trim())
        utterance.rate = 1.0
        utterance.pitch = 1.0
        utterance.lang = 'en-US'

        // Select a natural English voice if available
        const voices = window.speechSynthesis.getVoices()
        const englishVoice = voices.find(
          (v) => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('English'))
        ) || voices.find((v) => v.lang.startsWith('en'))

        if (englishVoice) {
          utterance.voice = englishVoice
        }

        utterance.onstart = () => {
          setIsSpeaking(true)
        }

        utterance.onend = () => {
          setIsSpeaking(false)
          onFinish?.()
        }

        utterance.onerror = (event) => {
          // 'canceled' / 'interrupted' is expected when stopping intentionally
          if (event.error !== 'canceled' && event.error !== 'interrupted') {
            console.warn('Speech synthesis error:', event.error)
          }
          setIsSpeaking(false)
        }

        utteranceRef.current = utterance
        window.speechSynthesis.speak(utterance)
      } catch (err) {
        console.warn('Error invoking SpeechSynthesis:', err)
        setIsSpeaking(false)
      }
    },
    [isSupported]
  )

  const stop = useCallback(() => {
    if (isSupported) {
      try {
        window.speechSynthesis.cancel()
      } catch {
        // ignore
      }
    }
    setIsSpeaking(false)
  }, [isSupported])

  return {
    isSpeaking,
    isSupported,
    speak,
    stop,
  }
}
