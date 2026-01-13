import { useState, useCallback } from 'react'
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Collapse,
  IconButton,
  Typography,
  Box,
  Chip,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import FolderIcon from '@mui/icons-material/Folder'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'
import type { CategoryTree } from '@/types'

interface TRCategoryTreeProps {
  categories: CategoryTree[]
  onEdit?: (category: CategoryTree) => void
  onDelete?: (category: CategoryTree) => void
  selectedId?: string
}

interface CategoryNodeProps {
  category: CategoryTree
  level: number
  onEdit?: (category: CategoryTree) => void
  onDelete?: (category: CategoryTree) => void
  selectedId?: string
  expandedIds: Set<string>
  toggleExpanded: (id: string) => void
}

/**
 * Individual category node component for the tree.
 */
const CategoryNode: React.FC<CategoryNodeProps> = ({
  category,
  level,
  onEdit,
  onDelete,
  selectedId,
  expandedIds,
  toggleExpanded,
}) => {
  const hasChildren = category.children && category.children.length > 0
  const isExpanded = expandedIds.has(category.id)
  const isSelected = selectedId === category.id

  const handleToggle = () => {
    if (hasChildren) {
      toggleExpanded(category.id)
      console.log(`INFO [TRCategoryTree]: ${isExpanded ? 'Collapsed' : 'Expanded'} category ${category.name}`)
    }
  }

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onEdit) {
      console.log(`INFO [TRCategoryTree]: Edit clicked for category ${category.name}`)
      onEdit(category)
    }
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onDelete) {
      console.log(`INFO [TRCategoryTree]: Delete clicked for category ${category.name}`)
      onDelete(category)
    }
  }

  return (
    <>
      <ListItem
        onClick={handleToggle}
        sx={{
          pl: 2 + level * 3,
          cursor: hasChildren ? 'pointer' : 'default',
          bgcolor: isSelected ? 'action.selected' : 'transparent',
          '&:hover': {
            bgcolor: 'action.hover',
          },
        }}
      >
        <ListItemIcon sx={{ minWidth: 36 }}>
          {hasChildren ? (
            isExpanded ? (
              <FolderOpenIcon color="action" />
            ) : (
              <FolderIcon color="action" />
            )
          ) : (
            <Box sx={{ width: 24 }} />
          )}
        </ListItemIcon>
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body1">{category.name}</Typography>
              <Chip
                label={category.type}
                size="small"
                color={category.type === 'income' ? 'success' : 'error'}
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            </Box>
          }
          secondary={category.description}
        />
        {hasChildren && (
          <IconButton size="small" onClick={handleToggle} sx={{ mr: 1 }}>
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        )}
        <ListItemSecondaryAction>
          {onEdit && (
            <IconButton edge="end" size="small" onClick={handleEdit} sx={{ mr: 1 }}>
              <EditIcon fontSize="small" />
            </IconButton>
          )}
          {onDelete && (
            <IconButton edge="end" size="small" onClick={handleDelete}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          )}
        </ListItemSecondaryAction>
      </ListItem>

      {hasChildren && (
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {category.children.map((child) => (
              <CategoryNode
                key={child.id}
                category={child}
                level={level + 1}
                onEdit={onEdit}
                onDelete={onDelete}
                selectedId={selectedId}
                expandedIds={expandedIds}
                toggleExpanded={toggleExpanded}
              />
            ))}
          </List>
        </Collapse>
      )}
    </>
  )
}

/**
 * Tree component for displaying hierarchical categories.
 * Supports expand/collapse, edit, and delete actions.
 */
export const TRCategoryTree: React.FC<TRCategoryTreeProps> = ({
  categories,
  onEdit,
  onDelete,
  selectedId,
}) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const toggleExpanded = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  if (categories.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No categories yet. Create your first category to get started.
        </Typography>
      </Box>
    )
  }

  console.log(`INFO [TRCategoryTree]: Rendering tree with ${categories.length} root categories`)

  return (
    <List component="nav" aria-label="category tree">
      {categories.map((category) => (
        <CategoryNode
          key={category.id}
          category={category}
          level={0}
          onEdit={onEdit}
          onDelete={onDelete}
          selectedId={selectedId}
          expandedIds={expandedIds}
          toggleExpanded={toggleExpanded}
        />
      ))}
    </List>
  )
}

export default TRCategoryTree
