import React from 'react'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
} from '@mui/material'
import type { SelectChangeEvent } from '@mui/material'
import { NavLink, useLocation } from 'react-router-dom'
import DashboardIcon from '@mui/icons-material/Dashboard'
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet'
import CategoryIcon from '@mui/icons-material/Category'
import SavingsIcon from '@mui/icons-material/Savings'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SettingsIcon from '@mui/icons-material/Settings'
import { useEntity } from '@/hooks/useEntity'

export const DRAWER_WIDTH_EXPANDED = 240
export const DRAWER_WIDTH_COLLAPSED = 56

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
}

const navigationItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Transactions', path: '/transactions', icon: <AccountBalanceWalletIcon /> },
  { label: 'Categories', path: '/categories', icon: <CategoryIcon /> },
  { label: 'Budgets', path: '/budgets', icon: <SavingsIcon /> },
  { label: 'Reports', path: '/reports', icon: <AssessmentIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
]

interface TRCollapsibleSidebarProps {
  open: boolean
  onToggle: () => void
}

export const TRCollapsibleSidebar: React.FC<TRCollapsibleSidebarProps> = ({
  open,
}) => {
  const location = useLocation()
  const { currentEntity, entities, switchEntity } = useEntity()

  const handleEntityChange = (event: SelectChangeEvent) => {
    switchEntity(event.target.value)
  }

  const drawerWidth = open ? DRAWER_WIDTH_EXPANDED : DRAWER_WIDTH_COLLAPSED

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          overflowX: 'hidden',
          transition: (theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
        },
      }}
    >
      {/* Header with app name */}
      <Box
        sx={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'flex-start' : 'center',
          px: open ? 2 : 0,
        }}
      >
        {open && (
          <Typography variant="h6" noWrap>
            Finance Tracker
          </Typography>
        )}
      </Box>

      <Divider />

      {/* Entity Switcher */}
      {open && (
        <Box sx={{ p: 2 }}>
          <FormControl fullWidth size="small">
            <InputLabel id="entity-select-label">Entity</InputLabel>
            <Select
              labelId="entity-select-label"
              id="entity-select"
              value={currentEntity?.id || ''}
              label="Entity"
              onChange={handleEntityChange}
            >
              {entities.map((entity) => (
                <MenuItem key={entity.id} value={entity.id}>
                  {entity.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}

      {!open && currentEntity && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            py: 1,
          }}
        >
          <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
            {currentEntity.name.charAt(0)}
          </Typography>
        </Box>
      )}

      <Divider />

      {/* Navigation Links */}
      <List>
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path

          return (
            <ListItem key={item.path} disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                component={NavLink}
                to={item.path}
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  backgroundColor: isActive ? 'action.selected' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: isActive ? 'primary.main' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary={item.label}
                    sx={{
                      '& .MuiListItemText-primary': {
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? 'primary.main' : 'inherit',
                      },
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </Drawer>
  )
}

export default TRCollapsibleSidebar
