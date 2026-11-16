import { useState, useEffect, useRef, useCallback } from 'react'

export type VoiceErrorType =
  | 'permission-denied'
  | 'no-speech'
  | 'audio-capture'
  | 'network'
  | 'unsupported'
  | 'unknown'

interface UseVoiceRecognitionOptions {
  lang?: string
  onResult?: (transcript: string, isFinal: boolean) => void
  onFinalResult?: (transcript: string) => void
}

export function useVoiceRecognition({
  lang = 'en-IN',
  onResult,
  onFinalResult,
}: UseVoiceRecognitionOptions = {}) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [error, setError] = useState<VoiceErrorType | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const recognitionRef = useRef<any>(null)
  const onResultRef = useRef(onResult)
  const onFinalResultRef = useRef(onFinalResult)

  useEffect(() => {
    onResultRef.current = onResult
    onFinalResultRef.current = onFinalResult
  }, [onResult, onFinalResult])
  const isSupported = typeof window !== 'undefined' && Boolean(
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  )

  // Initialize SpeechRecognition instance
  useEffect(() => {
    if (!isSupported) return

    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    try {
      const recognition = new SpeechRecognitionAPI()
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = lang
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setIsListening(true)
        setError(null)
        setErrorMessage(null)
      }

      recognition.onresult = (event: any) => {
        let currentInterim = ''
        let currentFinal = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const item = event.results[i]
          const text = item[0]?.transcript || ''
          if (item.isFinal) {
            currentFinal += text
          } else {
            currentInterim += text
          }
        }

        if (currentInterim) {
          setInterimTranscript(currentInterim)
          onResultRef.current?.(currentInterim, false)
        }

        if (currentFinal) {
          const trimmed = currentFinal.trim()
          setTranscript(trimmed)
          setInterimTranscript('')
          onResultRef.current?.(trimmed, true)
          onFinalResultRef.current?.(trimmed)
        }
      }

      recognition.onerror = (event: any) => {
        setIsListening(false)
        const eventError = event?.error || 'unknown'

        if (eventError === 'not-allowed' || eventError === 'service-not-allowed') {
          setError('permission-denied')
          setErrorMessage('Microphone access was denied. Please allow microphone permissions in your browser settings to use voice search.')
        } else if (eventError === 'no-speech') {
          setError('no-speech')
          setErrorMessage('No speech was detected. Please try speaking closer to the microphone.')
        } else if (eventError === 'audio-capture') {
          setError('audio-capture')
          setErrorMessage('No microphone was found or microphone is in use by another app.')
        } else if (eventError === 'network') {
          setError('network')
          setErrorMessage('Speech recognition network service error. Please check your internet connection.')
        } else if (eventError !== 'aborted') {
          setError('unknown')
          setErrorMessage('Speech recognition encountered an unexpected issue. Please try again.')
        }
      }

      recognition.onend = () => {
        setIsListening(false)
        setInterimTranscript('')
      }

      recognitionRef.current = recognition
    } catch (err) {
      console.warn('Failed to construct SpeechRecognition instance:', err)
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch {
          // ignore cleanup abort errors
        }
      }
    }
  }, [isSupported, lang])

  const startListening = useCallback(() => {
    setError(null)
    setErrorMessage(null)
    setTranscript('')
    setInterimTranscript('')

    if (!isSupported) {
      setError('unsupported')
      setErrorMessage('Voice search is not supported in this browser. Please try Google Chrome, Microsoft Edge, or Safari.')
      return
    }

    if (!recognitionRef.current) return

    try {
      recognitionRef.current.abort()
      recognitionRef.current.start()
    } catch (err: any) {
      // If already started, restart
      try {
        recognitionRef.current.stop()
        recognitionRef.current.start()
      } catch (innerErr) {
        console.warn('Error starting speech recognition:', innerErr)
      }
    }
  }, [isSupported])

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop()
      } catch (err) {
        console.warn('Error stopping speech recognition:', err)
      }
    }
    setIsListening(false)
  }, [isListening])

  const resetError = useCallback(() => {
    setError(null)
    setErrorMessage(null)
  }, [])

  return {
    isListening,
    isSupported,
    transcript,
    interimTranscript,
    error,
    errorMessage,
    startListening,
    stopListening,
    resetError,
  }
}

