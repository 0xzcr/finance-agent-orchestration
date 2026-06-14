import { useEffect, useState } from 'react'

/**
 * Handles the Zerodha OAuth callback.
 * Zerodha redirects here with ?request_token=xxx&status=success
 */
function ZerodhaCallback() {
  const [status, setStatus] = useState('processing')
  const [message, setMessage] = useState('Connecting to Zerodha...')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const requestToken = params.get('request_token')
    const loginStatus = params.get('status')

    if (loginStatus !== 'success' || !requestToken) {
      setStatus('error')
      setMessage('Zerodha login failed or was cancelled.')
      return
    }

    // Exchange request_token for access_token
    fetch('/api/zerodha/callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request_token: requestToken }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setStatus('success')
          setMessage(`Connected! Welcome ${data.user_id || 'back'}.`)
          // Redirect to home after 2 seconds
          setTimeout(() => {
            window.location.href = '/'
          }, 2000)
        } else {
          setStatus('error')
          setMessage(data.detail || 'Failed to connect to Zerodha.')
        }
      })
      .catch((err) => {
        setStatus('error')
        setMessage(`Error: ${err.message}`)
      })
  }, [])

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      textAlign: 'center',
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '3rem',
        maxWidth: '400px',
      }}>
        {status === 'processing' && <div style={{ fontSize: '2rem' }}>⏳</div>}
        {status === 'success' && <div style={{ fontSize: '2rem' }}>✅</div>}
        {status === 'error' && <div style={{ fontSize: '2rem' }}>❌</div>}
        <h2 style={{ margin: '1rem 0 0.5rem', color: 'var(--text-primary)' }}>
          {status === 'processing' && 'Connecting...'}
          {status === 'success' && 'Connected!'}
          {status === 'error' && 'Connection Failed'}
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>{message}</p>
      </div>
    </div>
  )
}

export default ZerodhaCallback
