import { useState } from 'react'

interface AgentRequest {
  name: string
  description: string
  use_case: string
  channels: string[]
  languages: string[]
  personality: string
}

export function AgentBuilder() {
  const [formData, setFormData] = useState<AgentRequest>({
    name: '',
    description: '',
    use_case: '',
    channels: ['web'],
    languages: ['en'],
    personality: 'helpful and professional'
  })
  const [isBuilding, setIsBuilding] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsBuilding(true)
    setError(null)

    try {
      const response = await fetch('/api/build-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.success) {
        setResult(data)
      } else {
        throw new Error(data.message || 'Failed to build agent')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setIsBuilding(false)
    }
  }

  const handleChannelChange = (channel: string, checked: boolean) => {
    if (checked) {
      setFormData(prev => ({
        ...prev,
        channels: [...prev.channels, channel]
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        channels: prev.channels.filter(c => c !== channel)
      }))
    }
  }

  const handleLanguageChange = (language: string, checked: boolean) => {
    if (checked) {
      setFormData(prev => ({
        ...prev,
        languages: [...prev.languages, language]
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        languages: prev.languages.filter(l => l !== language)
      }))
    }
  }

  if (result) {
    return (
      <div className="bg-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-green-400 mb-2">
            🎉 Agent Built Successfully!
          </h2>
          <p className="text-slate-300">{result.message}</p>
        </div>

        <div className="bg-slate-700 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">Agent Details</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-400">Name:</span>
              <span className="text-white ml-2">{result.agent_name}</span>
            </div>
            <div>
              <span className="text-slate-400">Files Generated:</span>
              <span className="text-white ml-2">{result.files_generated.length}</span>
            </div>
          </div>
        </div>

        <div className="flex justify-center space-x-4">
          <a
            href={result.download_url}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            📥 Download Agent Files
          </a>
          <button
            onClick={() => setResult(null)}
            className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            🔄 Build Another Agent
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-800 rounded-2xl p-8 shadow-2xl">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">
          📝 Build Your Agent
        </h2>
        <p className="text-slate-300">
          Fill out the form below to create your voice AI agent
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Agent Name */}
        <div>
          <label className="block text-sm font-semibold text-white mb-2">
            Agent Name *
          </label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., Customer Service Bot"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-semibold text-white mb-2">
            Description *
          </label>
          <textarea
            required
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe what your agent does..."
            rows={3}
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-purple-500 resize-vertical"
          />
        </div>

        {/* Use Case */}
        <div>
          <label className="block text-sm font-semibold text-white mb-2">
            Use Case *
          </label>
          <select
            required
            value={formData.use_case}
            onChange={(e) => setFormData(prev => ({ ...prev, use_case: e.target.value }))}
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="">Select a use case</option>
            <option value="customer_service">Customer Service</option>
            <option value="sales_assistant">Sales Assistant</option>
            <option value="personal_assistant">Personal Assistant</option>
            <option value="support_bot">Support Bot</option>
            <option value="educational">Educational</option>
            <option value="entertainment">Entertainment</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Channels */}
        <div>
          <label className="block text-sm font-semibold text-white mb-3">
            Channels
          </label>
          <div className="grid grid-cols-3 gap-3">
            {['web', 'phone', 'mobile'].map((channel) => (
              <label key={channel} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.channels.includes(channel)}
                  onChange={(e) => handleChannelChange(channel, e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-slate-700 border-slate-600 rounded focus:ring-purple-500"
                />
                <span className="text-white capitalize">{channel}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Languages */}
        <div>
          <label className="block text-sm font-semibold text-white mb-3">
            Languages
          </label>
          <div className="grid grid-cols-4 gap-3">
            {[
              { code: 'en', name: 'English' },
              { code: 'es', name: 'Spanish' },
              { code: 'fr', name: 'French' },
              { code: 'de', name: 'German' }
            ].map((lang) => (
              <label key={lang.code} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.languages.includes(lang.code)}
                  onChange={(e) => handleLanguageChange(lang.code, e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-slate-700 border-slate-600 rounded focus:ring-purple-500"
                />
                <span className="text-white">{lang.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Personality */}
        <div>
          <label className="block text-sm font-semibold text-white mb-2">
            Personality
          </label>
          <input
            type="text"
            value={formData.personality}
            onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
            placeholder="e.g., professional, friendly, empathetic"
            className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-4">
            <p className="text-red-300">❌ {error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isBuilding}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-lg transition-colors"
        >
          {isBuilding ? (
            <span className="flex items-center justify-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Building Agent...
            </span>
          ) : (
            '🚀 Build My Agent'
          )}
        </button>
      </form>
    </div>
  )
}
