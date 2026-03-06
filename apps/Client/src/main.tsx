import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import App from './App'
import theme from './theme'
import { AuthProvider } from '@/contexts/AuthContext'
import { EntityProvider } from '@/contexts/EntityContext'
import { RestaurantProvider } from '@/contexts/RestaurantContext'
import { SnackbarProvider } from '@/contexts/SnackbarContext'

console.log('INFO [Main]: Initializing Finance Tracker application')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <EntityProvider>
          <RestaurantProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <SnackbarProvider>
                <App />
              </SnackbarProvider>
            </ThemeProvider>
          </RestaurantProvider>
        </EntityProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)

console.log('INFO [Main]: Finance Tracker application mounted')
