import React, { createContext, useState, useCallback } from 'react'
import { Snackbar, Alert, type AlertColor } from '@mui/material'

interface SnackbarState {
  open: boolean
  message: string
  severity: AlertColor
}

interface SnackbarContextValue {
  showSnackbar: (message: string, severity?: AlertColor) => void
}

export const SnackbarContext = createContext<SnackbarContextValue>({
  showSnackbar: () => {},
})

export const SnackbarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'success',
  })

  const showSnackbar = useCallback((message: string, severity: AlertColor = 'success') => {
    console.log(`INFO [SnackbarContext]: Showing snackbar: ${severity} - ${message}`)
    setState({ open: true, message, severity })
  }, [])

  const handleClose = useCallback((_event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return
    setState((prev) => ({ ...prev, open: false }))
  }, [])

  return (
    <SnackbarContext.Provider value={{ showSnackbar }}>
      {children}
      <Snackbar
        open={state.open}
        autoHideDuration={4000}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity={state.severity} variant="filled" sx={{ width: '100%' }}>
          {state.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  )
}
