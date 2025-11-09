import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Add error boundary for unhandled errors
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
  const rootElement = document.getElementById('root')
  if (rootElement && !rootElement.querySelector('.error-message')) {
    rootElement.innerHTML = `
      <div class="error-message" style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
        <h1 style="color: #d32f2f;">Error loading application</h1>
        <p style="color: #666;">${event.error?.message || 'Unknown error'}</p>
        <p style="color: #999; font-size: 12px;">Please check the browser console for more details.</p>
        <button onclick="window.location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">Reload Page</button>
      </div>
    `
  }
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
})

const rootElement = document.getElementById('root')
if (!rootElement) {
  console.error('Failed to find root element')
  document.body.innerHTML = '<div style="padding: 20px; text-align: center;"><h1>Error: Root element not found</h1></div>'
} else {
  try {
    console.log('Initializing React app...')
    const root = ReactDOM.createRoot(rootElement)
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    )
    console.log('React app initialized successfully')
  } catch (error) {
    console.error('Failed to render React app:', error)
    rootElement.innerHTML = `
      <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">
        <h1 style="color: #d32f2f;">Error loading application</h1>
        <p style="color: #666;">${error instanceof Error ? error.message : 'Unknown error'}</p>
        <p style="color: #999; font-size: 12px;">Please check the browser console for more details.</p>
        <button onclick="window.location.reload()" style="margin-top: 20px; padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">Reload Page</button>
      </div>
    `
  }
}
