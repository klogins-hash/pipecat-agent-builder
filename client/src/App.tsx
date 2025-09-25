import { useState } from 'react'
import { PipecatClient } from '@pipecat-ai/client-js'
import { PipecatClientProvider, PipecatClientAudio } from '@pipecat-ai/client-react'
import { DailyTransport } from '@pipecat-ai/daily-transport'
import { VoiceInterface } from './components/VoiceInterface'
import { AgentBuilder } from './components/AgentBuilder'

// Create the Pipecat client
const client = new PipecatClient({
  transport: new DailyTransport(),
  enableMic: true,
  enableCam: false,
})

function App() {
  const [mode, setMode] = useState<'voice' | 'builder'>('voice')

  return (
    <PipecatClientProvider client={client}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              🤖 Pipecat Agent Builder
            </h1>
            <p className="text-xl text-slate-300 mb-6">
              Build sophisticated voice AI agents through natural conversation
            </p>
            
            {/* Mode Toggle */}
            <div className="flex justify-center mb-8">
              <div className="bg-slate-800 rounded-lg p-1 flex">
                <button
                  onClick={() => setMode('voice')}
                  className={`px-6 py-2 rounded-md transition-all ${
                    mode === 'voice'
                      ? 'bg-purple-600 text-white'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  🎤 Voice Interface
                </button>
                <button
                  onClick={() => setMode('builder')}
                  className={`px-6 py-2 rounded-md transition-all ${
                    mode === 'builder'
                      ? 'bg-purple-600 text-white'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  📝 Form Builder
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="max-w-4xl mx-auto">
            {mode === 'voice' ? (
              <VoiceInterface />
            ) : (
              <AgentBuilder />
            )}
          </div>
        </div>
        
        {/* Audio component for Pipecat */}
        <PipecatClientAudio />
      </div>
    </PipecatClientProvider>
  )
}

export default App
