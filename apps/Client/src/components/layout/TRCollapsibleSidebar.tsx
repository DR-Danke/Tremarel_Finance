import React, { useState } from 'react'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Collapse,
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
import RepeatIcon from '@mui/icons-material/Repeat'
import SavingsIcon from '@mui/icons-material/Savings'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SettingsIcon from '@mui/icons-material/Settings'
import PeopleIcon from '@mui/icons-material/People'
import RestaurantIcon from '@mui/icons-material/Restaurant'
import DescriptionIcon from '@mui/icons-material/Description'
import EventIcon from '@mui/icons-material/Event'
import InventoryIcon from '@mui/icons-material/Inventory'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import GavelIcon from '@mui/icons-material/Gavel'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import PersonSearchIcon from '@mui/icons-material/PersonSearch'
import GroupsIcon from '@mui/icons-material/Groups'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import ExpandLess from '@mui/icons-material/ExpandLess'
import ExpandMore from '@mui/icons-material/ExpandMore'
import { useEntity } from '@/hooks/useEntity'
import { useAuth } from '@/hooks/useAuth'
import { TRRestaurantSelector } from './TRRestaurantSelector'

export const DRAWER_WIDTH_EXPANDED = 240
export const DRAWER_WIDTH_COLLAPSED = 56

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
}

interface NavSection {
  label: string
  collapsible?: boolean
  defaultOpen?: boolean
  items: NavItem[]
  subsections?: NavSection[]
}

const financeSection: NavSection = {
  label: 'Finance',
  collapsible: false,
  items: [
    { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
    { label: 'Transactions', path: '/transactions', icon: <AccountBalanceWalletIcon /> },
    { label: 'Recurring', path: '/recurring', icon: <RepeatIcon /> },
    { label: 'Categories', path: '/categories', icon: <CategoryIcon /> },
    { label: 'Budgets', path: '/budgets', icon: <SavingsIcon /> },
    { label: 'Prospects', path: '/prospects', icon: <PeopleIcon /> },
    { label: 'Reports', path: '/reports', icon: <AssessmentIcon /> },
  ],
}

const pocSection: NavSection = {
  label: 'POCs',
  collapsible: true,
  defaultOpen: false,
  items: [],
  subsections: [
    {
      label: 'RestaurantOS',
      items: [
        { label: 'Dashboard', path: '/poc/restaurant-os/dashboard', icon: <RestaurantIcon /> },
        { label: 'Personas', path: '/poc/restaurant-os/persons', icon: <PeopleIcon /> },
        { label: 'Documentos', path: '/poc/restaurant-os/documents', icon: <DescriptionIcon /> },
        { label: 'Eventos / Tareas', path: '/poc/restaurant-os/events', icon: <EventIcon /> },
        { label: 'Recursos / Inventario', path: '/poc/restaurant-os/resources', icon: <InventoryIcon /> },
        { label: 'Recetas', path: '/poc/restaurant-os/recipes', icon: <MenuBookIcon /> },
      ],
    },
    {
      label: 'Legal Desk',
      items: [
        { label: 'Dashboard', path: '/poc/legal-desk/dashboard', icon: <GavelIcon /> },
        { label: 'Cases', path: '/poc/legal-desk/cases', icon: <BusinessCenterIcon /> },
        { label: 'Specialists', path: '/poc/legal-desk/specialists', icon: <PersonSearchIcon /> },
        { label: 'Clients', path: '/poc/legal-desk/clients', icon: <GroupsIcon /> },
        { label: 'Analytics', path: '/poc/legal-desk/analytics', icon: <AnalyticsIcon /> },
      ],
    },
  ],
}

const settingsSection: NavSection = {
  label: '',
  items: [
    { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
  ],
}

const MODULE_SUBSECTION_MAP: Record<string, string> = {
  legaldesk: 'Legal Desk',
  'restaurant-os': 'RestaurantOS',
}

const buildNavigationSections = (hasEntities: boolean, allowedModules?: string[] | null): NavSection[] => {
  // When allowed_modules is set, show only those modules
  if (allowedModules && allowedModules.length > 0) {
    const sections: NavSection[] = []

    if (allowedModules.includes('finance')) {
      sections.push(financeSection)
    }

    // Filter POC subsections to only allowed modules
    const allowedSubsections = pocSection.subsections?.filter((sub) => {
      return allowedModules.some((mod) => MODULE_SUBSECTION_MAP[mod] === sub.label)
    })

    if (allowedSubsections && allowedSubsections.length > 0) {
      if (allowedSubsections.length === 1) {
        // Single POC module: show as flat section (no collapsible wrapper)
        sections.push({
          label: allowedSubsections[0].label,
          collapsible: false,
          items: allowedSubsections[0].items,
        })
      } else {
        sections.push({ ...pocSection, subsections: allowedSubsections })
      }
    }

    sections.push(settingsSection)
    return sections
  }

  // Default behavior: all modules based on entity status
  if (hasEntities) {
    return [financeSection, pocSection, settingsSection]
  }
  // Users without entities only see RestaurantOS (non-collapsible) + Settings
  return [
    { ...pocSection, label: 'RestaurantOS', collapsible: false, subsections: undefined, items: pocSection.subsections?.[0]?.items ?? [] },
    settingsSection,
  ]
}

const SIDEBAR_SECTIONS_KEY = 'sidebarSectionState'

const getInitialSectionState = (): Record<string, boolean> => {
  try {
    const stored = localStorage.getItem(SIDEBAR_SECTIONS_KEY)
    if (stored) {
      return JSON.parse(stored) as Record<string, boolean>
    }
  } catch {
    // localStorage unavailable or corrupted — fall back to defaults
  }
  // Default collapsible section state
  return { 'POCs': pocSection.defaultOpen ?? false }
}

interface TRCollapsibleSidebarProps {
  open: boolean
  onToggle: () => void
}

export const TRCollapsibleSidebar: React.FC<TRCollapsibleSidebarProps> = ({
  open,
}) => {
  const location = useLocation()
  const { user } = useAuth()
  const { currentEntity, entities, switchEntity } = useEntity()
  const hasEntities = entities.length > 0
  const allowedModules = user?.allowed_modules ?? null
  const navigationSections = buildNavigationSections(hasEntities, allowedModules)
  const [sectionState, setSectionState] = useState<Record<string, boolean>>(getInitialSectionState)

  const handleEntityChange = (event: SelectChangeEvent) => {
    switchEntity(event.target.value)
  }

  const handleSectionToggle = (sectionLabel: string) => {
    setSectionState((prev) => {
      const next = { ...prev, [sectionLabel]: !prev[sectionLabel] }
      try {
        localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(next))
      } catch {
        // localStorage unavailable — state remains in memory only
      }
      return next
    })
  }

  const drawerWidth = open ? DRAWER_WIDTH_EXPANDED : DRAWER_WIDTH_COLLAPSED

  const renderNavItem = (item: NavItem, indentLevel: number = 0) => {
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
            pl: open ? 2.5 + indentLevel * 2 : 2.5,
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
  }

  const renderSection = (section: NavSection, index: number) => {
    const isOpen = section.label ? (sectionState[section.label] ?? true) : true
    const isCollapsible = section.collapsible !== false && !!section.label
    const hasLabel = !!section.label

    // Collapsed sidebar (icon-only mode)
    if (!open) {
      return (
        <React.Fragment key={section.label || `section-${index}`}>
          {index > 0 && <Divider />}
          {section.items.map((item) => renderNavItem(item))}
          {section.subsections?.map((sub) =>
            sub.items.map((item) => renderNavItem(item))
          )}
        </React.Fragment>
      )
    }

    // Expanded sidebar
    return (
      <React.Fragment key={section.label || `section-${index}`}>
        {/* Bottom section (no label) gets a divider */}
        {!hasLabel && <Divider sx={{ my: 1 }} />}

        {/* Section header */}
        {hasLabel && (
          <ListSubheader
            component="div"
            sx={{
              lineHeight: '36px',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'text.secondary',
              backgroundColor: 'transparent',
              cursor: isCollapsible ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              userSelect: 'none',
            }}
            onClick={isCollapsible ? () => handleSectionToggle(section.label) : undefined}
          >
            {section.label}
            {isCollapsible && (isOpen ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />)}
          </ListSubheader>
        )}

        {/* Section content */}
        {isCollapsible ? (
          <Collapse in={isOpen} timeout="auto" unmountOnExit>
            {section.items.map((item) => renderNavItem(item))}
            {section.subsections?.map((sub) => (
              <React.Fragment key={sub.label}>
                <Typography
                  variant="caption"
                  sx={{
                    pl: 4,
                    py: 0.5,
                    display: 'block',
                    color: 'text.disabled',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    fontSize: '0.65rem',
                    letterSpacing: '0.05em',
                  }}
                >
                  {sub.label}
                </Typography>
                {sub.items.map((item) => renderNavItem(item, 1))}
              </React.Fragment>
            ))}
          </Collapse>
        ) : (
          <>
            {section.items.map((item) => renderNavItem(item))}
            {section.subsections?.map((sub) => (
              <React.Fragment key={sub.label}>
                <Typography
                  variant="caption"
                  sx={{
                    pl: 4,
                    py: 0.5,
                    display: 'block',
                    color: 'text.disabled',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    fontSize: '0.65rem',
                    letterSpacing: '0.05em',
                  }}
                >
                  {sub.label}
                </Typography>
                {sub.items.map((item) => renderNavItem(item, 1))}
              </React.Fragment>
            ))}
          </>
        )}
      </React.Fragment>
    )
  }

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

      {/* Entity Switcher — only visible when user has entities and no module restriction */}
      {entities.length > 0 && !allowedModules && (
        <>
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
        </>
      )}

      {/* Restaurant Selector — only visible on RestaurantOS routes */}
      {location.pathname.startsWith('/poc/restaurant-os') && (
        <>
          <TRRestaurantSelector open={open} />
          <Divider />
        </>
      )}

      {/* Navigation Links */}
      <List sx={{ overflowY: 'auto', flex: 1 }}>
        {navigationSections.map((section, index) => renderSection(section, index))}
      </List>
    </Drawer>
  )
}

export default TRCollapsibleSidebar
