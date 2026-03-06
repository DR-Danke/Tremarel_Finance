import React from 'react'
import { Breadcrumbs, Link, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'

interface TRBreadcrumbsProps {
  module: string
  moduleHref: string
  restaurantName?: string
  currentPage: string
}

export const TRBreadcrumbs: React.FC<TRBreadcrumbsProps> = ({
  module,
  moduleHref,
  restaurantName,
  currentPage,
}) => {
  return (
    <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} sx={{ mb: 1 }}>
      <Link component={RouterLink} to={moduleHref} underline="hover" color="inherit">
        {module}
      </Link>
      {restaurantName && (
        <Typography color="text.secondary" variant="body2">
          {restaurantName}
        </Typography>
      )}
      <Typography color="text.primary" variant="body2" fontWeight={500}>
        {currentPage}
      </Typography>
    </Breadcrumbs>
  )
}
