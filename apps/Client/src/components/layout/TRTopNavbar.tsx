import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Button,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import LogoutIcon from '@mui/icons-material/Logout'
import { useAuth } from '@/hooks/useAuth'
import { useNavigate } from 'react-router-dom'

const DRAWER_WIDTH_EXPANDED = 240
const DRAWER_WIDTH_COLLAPSED = 56

interface TRTopNavbarProps {
  onMenuToggle: () => void
  isSidebarOpen: boolean
}

export const TRTopNavbar: React.FC<TRTopNavbarProps> = ({
  onMenuToggle,
  isSidebarOpen,
}) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    console.log('INFO [TRTopNavbar]: User initiated logout')
    logout()
    navigate('/login')
  }

  // Get display name from user data
  const displayName = user?.first_name
    ? `${user.first_name}${user.last_name ? ` ${user.last_name}` : ''}`
    : user?.email

  return (
    <AppBar
      position="fixed"
      sx={{
        width: {
          sm: `calc(100% - ${isSidebarOpen ? DRAWER_WIDTH_EXPANDED : DRAWER_WIDTH_COLLAPSED}px)`,
        },
        ml: {
          sm: `${isSidebarOpen ? DRAWER_WIDTH_EXPANDED : DRAWER_WIDTH_COLLAPSED}px`,
        },
        transition: (theme) =>
          theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="toggle sidebar"
          edge="start"
          onClick={onMenuToggle}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          Finance Tracker
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {displayName && (
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              {displayName}
            </Typography>
          )}
          <Button
            color="inherit"
            onClick={handleLogout}
            startIcon={<LogoutIcon />}
            sx={{ textTransform: 'none' }}
          >
            Logout
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default TRTopNavbar
