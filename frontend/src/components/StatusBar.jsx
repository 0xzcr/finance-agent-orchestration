import './StatusBar.css'

function StatusBar({ health }) {
  if (!health) {
    return (
      <div className="status-bar status-disconnected">
        <span className="status-dot red" />
        <span>Backend not connected — start the API server</span>
      </div>
    )
  }

  return (
    <div className="status-bar status-connected">
      <div className="status-items">
        <div className="status-item">
          <span className={`status-dot ${health.cerebras_configured ? 'green' : 'red'}`} />
          <span>Cerebras</span>
        </div>
        <div className="status-item">
          <span className={`status-dot ${health.zerodha_configured ? 'green' : 'yellow'}`} />
          <span>Zerodha</span>
        </div>
        <div className="status-item">
          <span className={`status-dot ${health.alpha_vantage_configured ? 'green' : 'yellow'}`} />
          <span>Alpha Vantage</span>
        </div>
      </div>
    </div>
  )
}

export default StatusBar
