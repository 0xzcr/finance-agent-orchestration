import { useState } from 'react'
import './InvestmentForm.css'

const PRESETS = [
  { label: '🤖 AI & Tech Stocks', prompt: 'Invest in AI and technology companies with strong growth potential' },
  { label: '🏦 Banking & Finance', prompt: 'Blue-chip banking and financial services stocks in India' },
  { label: '⚡ Energy & Green', prompt: 'Renewable energy and green infrastructure companies' },
  { label: '💊 Pharma & Health', prompt: 'Pharmaceutical and healthcare sector stocks' },
  { label: '🏗️ Infrastructure', prompt: 'Infrastructure and construction companies benefiting from govt spending' },
]

function InvestmentForm({ onSubmit, loading }) {
  const [prompt, setPrompt] = useState('')
  const [amount, setAmount] = useState('100000')
  const [risk, setRisk] = useState('moderate')
  const [market, setMarket] = useState('india')

  function handleSubmit(e) {
    e.preventDefault()
    if (!prompt.trim()) return

    onSubmit({
      prompt: prompt.trim(),
      investment_amount: amount,
      risk_tolerance: risk,
      market,
    })
  }

  function handlePreset(presetPrompt) {
    setPrompt(presetPrompt)
  }

  return (
    <form className="investment-form" onSubmit={handleSubmit}>
      <h2 className="form-title">What do you want to invest in?</h2>

      <div className="presets">
        {PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            className={`preset-btn ${prompt === p.prompt ? 'active' : ''}`}
            onClick={() => handlePreset(p.prompt)}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="form-group">
        <label htmlFor="prompt">Investment Goal</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe what you want to invest in... e.g., 'I want to invest in AI companies that are profitable and have strong moat'"
          rows={4}
          required
          minLength={5}
          maxLength={500}
        />
        <span className="char-count">{prompt.length}/500</span>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="amount">Amount (₹)</label>
          <input
            id="amount"
            type="text"
            value={amount}
            onChange={(e) => setAmount(e.target.value.replace(/[^0-9]/g, ''))}
            placeholder="100000"
          />
        </div>

        <div className="form-group">
          <label htmlFor="risk">Risk Tolerance</label>
          <select id="risk" value={risk} onChange={(e) => setRisk(e.target.value)}>
            <option value="conservative">🛡️ Conservative</option>
            <option value="moderate">⚖️ Moderate</option>
            <option value="aggressive">🚀 Aggressive</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="market">Market</label>
        <select id="market" value={market} onChange={(e) => setMarket(e.target.value)}>
          <option value="india">🇮🇳 India (NSE/BSE via Zerodha)</option>
          <option value="global">🌍 Global (US Markets)</option>
        </select>
      </div>

      <button type="submit" className="submit-btn" disabled={loading || !prompt.trim()}>
        {loading ? (
          <>
            <span className="spinner" />
            Agents Working...
          </>
        ) : (
          <>Generate Investment Plan</>
        )}
      </button>

      {loading && (
        <div className="loading-info">
          <p>🤖 4 AI agents are analyzing markets for you:</p>
          <ol>
            <li>Market Researcher — gathering live data</li>
            <li>Strategy Planner — building your plan</li>
            <li>Risk Analyst — stress-testing</li>
            <li>Portfolio Advisor — finalizing recommendation</li>
          </ol>
          <p className="loading-note">This may take 1-3 minutes...</p>
        </div>
      )}
    </form>
  )
}

export default InvestmentForm
