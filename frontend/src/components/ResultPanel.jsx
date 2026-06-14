import ReactMarkdown from 'react-markdown'
import './ResultPanel.css'

function ResultPanel({ result, error, loading }) {
  if (loading) {
    return (
      <div className="result-panel result-loading">
        <div className="result-placeholder">
          <div className="pulse-bar" />
          <div className="pulse-bar short" />
          <div className="pulse-bar" />
          <div className="pulse-bar medium" />
          <div className="pulse-bar short" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result-panel result-error">
        <div className="error-icon">❌</div>
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="result-panel result-empty">
        <div className="empty-icon">🎯</div>
        <h3>Your Investment Plan Will Appear Here</h3>
        <p>
          Tell our AI agents what you want to invest in, set your budget and
          risk tolerance, and they'll create a personalized investment plan.
        </p>
        <div className="features">
          <div className="feature">
            <span>📊</span>
            <span>Live market data</span>
          </div>
          <div className="feature">
            <span>🧠</span>
            <span>4 specialized AI agents</span>
          </div>
          <div className="feature">
            <span>⚡</span>
            <span>Powered by Cerebras</span>
          </div>
          <div className="feature">
            <span>🇮🇳</span>
            <span>Indian & global markets</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="result-panel result-success">
      <div className="result-header">
        <h3>📋 Investment Recommendation</h3>
        <button
          className="copy-btn"
          onClick={() => navigator.clipboard.writeText(result)}
          title="Copy to clipboard"
        >
          📋 Copy
        </button>
      </div>
      <div className="result-content">
        <ReactMarkdown>{result}</ReactMarkdown>
      </div>
    </div>
  )
}

export default ResultPanel
