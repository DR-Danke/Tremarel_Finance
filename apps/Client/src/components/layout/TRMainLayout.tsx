import React, { useState, useEffect, useCallback } from 'react'
import { Box, Toolbar, useMediaQuery, useTheme } from '@mui/material'
import { TRTopNavbar } from './TRTopNavbar'
import { TRCollapsibleSidebar, DRAWER_WIDTH_EXPANDED, DRAWER_WIDTH_COLLAPSED } from './TRCollapsibleSidebar'

interface TRMainLayoutProps {
  children: React.ReactNode
}

export const TRMainLayout: React.FC<TRMainLayoutProps> = ({ children }) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile)

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false)
      console.log('INFO [TRMainLayout]: Auto-collapsed sidebar for mobile view')
    } else {
      setSidebarOpen(true)
      console.log('INFO [TRMainLayout]: Auto-expanded sidebar for desktop view')
    }
  }, [isMobile])

  const handleToggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => {
      const newState = !prev
      console.log('INFO [TRMainLayout]: Sidebar toggled', newState ? 'open' : 'closed')
      return newState
    })
  }, [])

  const drawerWidth = sidebarOpen ? DRAWER_WIDTH_EXPANDED : DRAWER_WIDTH_COLLAPSED

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Top Navigation Bar */}
      <TRTopNavbar onMenuToggle={handleToggleSidebar} isSidebarOpen={sidebarOpen} />

      {/* Collapsible Sidebar */}
      <TRCollapsibleSidebar open={sidebarOpen} onToggle={handleToggleSidebar} />

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          backgroundColor: 'background.default',
        }}
      >
        {/* Spacer for fixed AppBar */}
        <Toolbar />

        {/* Page Content */}
        {children}
      </Box>
    </Box>
  )
}

export default TRMainLayout
