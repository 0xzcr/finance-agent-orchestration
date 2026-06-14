import { useState, useEffect } from 'react'
import InvestmentForm from './components/InvestmentForm'
import ResultPanel from './components/ResultPanel'
import StatusBar from './components/StatusBar'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHealth()
  }, [])

  async function fetchHealth() {
    try {
      const res = await fetch('/api/health')
      const data = await res.json()
      setHealth(data)
    } catch {
      setHealth(null)
    }
  }

  async function handleSubmit(formData) {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('/api/invest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      const data = await res.json()

      if (data.success) {
        setResult(data.recommendation)
      } else {
        setError(data.error || 'Something went wrong')
      }
    } catch (err) {
      setError(`Network error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">📈</span>
            <h1>Finance Agent</h1>
          </div>
          <p className="tagline">AI-Powered Investment Planning</p>
        </div>
      </header>

      <StatusBar health={health} />

      <main className="app-main">
        <div className="container">
          <div className="layout">
            <section className="form-section">
              <InvestmentForm onSubmit={handleSubmit} loading={loading} />
            </section>

            <section className="result-section">
              <ResultPanel result={result} error={error} loading={loading} />
            </section>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Powered by <strong>CrewAI</strong> + <strong>Cerebras</strong> + <strong>Zerodha</strong>
        </p>
        <p className="disclaimer">
          ⚠️ This is an AI-generated analysis for educational purposes only. Not financial advice.
        </p>
      </footer>
    </div>
  )
}

export default App
