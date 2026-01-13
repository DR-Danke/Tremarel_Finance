import React from 'react'
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Typography,
  Box,
  Chip,
} from '@mui/material'
import BusinessIcon from '@mui/icons-material/Business'
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom'
import { useEntity } from '@/hooks/useEntity'

interface TREntitySelectorProps {
  fullWidth?: boolean
  size?: 'small' | 'medium'
}

/**
 * Entity selector dropdown component for switching between entities.
 * Displays current entity and allows user to switch between available entities.
 */
export const TREntitySelector: React.FC<TREntitySelectorProps> = ({
  fullWidth = false,
  size = 'small',
}) => {
  const { entities, currentEntity, isLoading, switchEntity } = useEntity()

  const handleChange = (event: SelectChangeEvent<string>) => {
    const entityId = event.target.value
    console.log('INFO [TREntitySelector]: User selected entity:', entityId)
    switchEntity(entityId)
  }

  const getEntityIcon = (type: 'family' | 'startup') => {
    return type === 'family' ? (
      <FamilyRestroomIcon fontSize="small" />
    ) : (
      <BusinessIcon fontSize="small" />
    )
  }

  if (isLoading) {
    return (
      <Box sx={{ minWidth: 150 }}>
        <Typography variant="body2" color="text.secondary">
          Loading entities...
        </Typography>
      </Box>
    )
  }

  if (entities.length === 0) {
    return (
      <Box sx={{ minWidth: 150 }}>
        <Typography variant="body2" color="text.secondary">
          No entities
        </Typography>
      </Box>
    )
  }

  return (
    <FormControl fullWidth={fullWidth} size={size} sx={{ minWidth: 200 }}>
      <InputLabel id="entity-selector-label">Entity</InputLabel>
      <Select
        labelId="entity-selector-label"
        id="entity-selector"
        value={currentEntity?.id || ''}
        label="Entity"
        onChange={handleChange}
        renderValue={(selected) => {
          const entity = entities.find((e) => e.id === selected)
          if (!entity) return null
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getEntityIcon(entity.type)}
              <Typography variant="body2">{entity.name}</Typography>
              <Chip
                label={entity.type}
                size="small"
                color={entity.type === 'family' ? 'primary' : 'secondary'}
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            </Box>
          )
        }}
      >
        {entities.map((entity) => (
          <MenuItem key={entity.id} value={entity.id}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getEntityIcon(entity.type)}
              <Typography variant="body2">{entity.name}</Typography>
              <Chip
                label={entity.type}
                size="small"
                color={entity.type === 'family' ? 'primary' : 'secondary'}
                sx={{ height: 20, fontSize: '0.7rem', ml: 'auto' }}
              />
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}

export default TREntitySelector
