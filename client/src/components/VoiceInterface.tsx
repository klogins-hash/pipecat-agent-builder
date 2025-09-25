import { useState } from 'react'
import { usePipecatClient } from '@pipecat-ai/client-react'
import { 
  VoiceVisualizer,
  ConnectionStatus,
  MicrophoneButton,
  TranscriptDisplay,
} from '@pipecat-ai/voice-ui-kit'

export function VoiceInterface() {
  const client = usePipecatClient()
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [transcript, setTranscript] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([])

  const handleConnect = async () => {
    if (isConnected) {
      await client.disconnect()
      setIsConnected(false)
      return
    }

    setIsConnecting(true)
    try {
      await client.startBotAndConnect({
        endpoint: `${import.meta.env.VITE_API_URL || '/api'}/connect`
      })
      setIsConnected(true)
    } catch (error) {
      console.error('Failed to connect:', error)
    } finally {
      setIsConnecting(false)
    }
  }

  // Listen for transcript updates
  client.on('userTranscript', (text: string) => {
    setTranscript(prev => [...prev, { role: 'user', content: text }])
  })

  client.on('botTranscript', (text: string) => {
    setTranscript(prev => [...prev, { role: 'assistant', content: text }])
  })

  return (
    <div className="bg-slate-800 rounded-2xl p-8 shadow-2xl">
      {/* Connection Status */}
      <div className="text-center mb-8">
        <ConnectionStatus 
          status={isConnecting ? 'connecting' : isConnected ? 'connected' : 'disconnected'}
          className="mb-4"
        />
        
        {!isConnected && (
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-white mb-2">
              Talk to Your Agent Builder
            </h2>
            <p className="text-slate-300">
              Describe the voice AI agent you want to build. I'll help you create it step by step.
            </p>
          </div>
        )}
      </div>

      {/* Voice Visualizer */}
      <div className="flex justify-center mb-8">
        <div className="relative">
          <VoiceVisualizer 
            isActive={isConnected}
            className="w-32 h-32"
          />
          
          {/* Connect/Disconnect Button */}
          <div className="absolute inset-0 flex items-center justify-center">
            <button
              onClick={handleConnect}
              disabled={isConnecting}
              className={`w-20 h-20 rounded-full border-4 transition-all duration-300 ${
                isConnected
                  ? 'bg-red-500 border-red-400 hover:bg-red-600'
                  : 'bg-green-500 border-green-400 hover:bg-green-600'
              } ${isConnecting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isConnecting ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto" />
              ) : isConnected ? (
                <span className="text-white text-2xl">⏹️</span>
              ) : (
                <span className="text-white text-2xl">🎤</span>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Microphone Button */}
      {isConnected && (
        <div className="flex justify-center mb-8">
          <MicrophoneButton 
            client={client}
            className="bg-purple-600 hover:bg-purple-700"
          />
        </div>
      )}

      {/* Instructions */}
      {!isConnected && (
        <div className="bg-slate-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">
            💡 How to Use
          </h3>
          <ul className="text-slate-300 space-y-2">
            <li>• Click the microphone to start a conversation</li>
            <li>• Describe your agent: "I want a customer service bot for my restaurant"</li>
            <li>• I'll ask follow-up questions about channels, languages, and features</li>
            <li>• Once complete, I'll generate your agent code and deployment files</li>
          </ul>
        </div>
      )}

      {/* Conversation Transcript */}
      {transcript.length > 0 && (
        <div className="bg-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            💬 Conversation
          </h3>
          <TranscriptDisplay 
            transcript={transcript}
            className="max-h-64 overflow-y-auto"
          />
        </div>
      )}

      {/* Example Prompts */}
      {!isConnected && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-white mb-4 text-center">
            🎯 Example Requests
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-slate-700 rounded-lg p-4">
              <h4 className="font-semibold text-purple-300 mb-2">Customer Service</h4>
              <p className="text-sm text-slate-300">
                "Build a customer service agent for my e-commerce store that can handle returns, 
                track orders, and answer product questions."
              </p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <h4 className="font-semibold text-purple-300 mb-2">Sales Assistant</h4>
              <p className="text-sm text-slate-300">
                "Create a sales bot that can qualify leads, schedule demos, 
                and answer questions about our SaaS pricing."
              </p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <h4 className="font-semibold text-purple-300 mb-2">Restaurant Host</h4>
              <p className="text-sm text-slate-300">
                "I need a phone agent for my restaurant that takes reservations, 
                answers menu questions, and handles takeout orders."
              </p>
            </div>
            <div className="bg-slate-700 rounded-lg p-4">
              <h4 className="font-semibold text-purple-300 mb-2">Personal Assistant</h4>
              <p className="text-sm text-slate-300">
                "Build a personal assistant that can manage my calendar, 
                send reminders, and help with daily tasks."
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
