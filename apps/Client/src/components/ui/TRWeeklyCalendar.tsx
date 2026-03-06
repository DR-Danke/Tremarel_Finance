import React, { useMemo } from 'react'
import { Box, Card, CardContent, Typography, IconButton } from '@mui/material'
import { CheckCircle } from '@mui/icons-material'
import type { Event } from '@/types/event'

interface TRWeeklyCalendarProps {
  events: Event[]
  personsMap: Record<string, string>
  onQuickComplete?: (eventId: string) => void
}

const getDayLabel = (date: Date): string =>
  date.toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short' })

const getWeekDays = (): Date[] => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const monday = new Date(today)
  monday.setDate(today.getDate() - ((dayOfWeek + 6) % 7))
  monday.setHours(0, 0, 0, 0)

  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    return d
  })
}

const isToday = (date: Date): boolean => {
  const now = new Date()
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  )
}

export const TRWeeklyCalendar: React.FC<TRWeeklyCalendarProps> = ({
  events,
  personsMap,
  onQuickComplete,
}) => {
  const weekDays = useMemo(() => getWeekDays(), [])

  const eventsByDay = useMemo(() => {
    const map = new Map<string, Event[]>()
    for (const day of weekDays) {
      map.set(day.toISOString().slice(0, 10), [])
    }
    for (const event of events) {
      const key = event.date.slice(0, 10)
      const bucket = map.get(key)
      if (bucket) bucket.push(event)
    }
    return map
  }, [events, weekDays])

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
      {weekDays.map((day) => {
        const key = day.toISOString().slice(0, 10)
        const dayEvents = eventsByDay.get(key) || []
        const today = isToday(day)

        return (
          <Card
            key={key}
            variant={today ? 'elevation' : 'outlined'}
            elevation={today ? 3 : 0}
            sx={{
              minHeight: 140,
              ...(today && { borderLeft: 3, borderColor: 'primary.main' }),
            }}
          >
            <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
              <Typography
                variant="caption"
                fontWeight={today ? 700 : 400}
                color={today ? 'primary.main' : 'text.secondary'}
                sx={{ textTransform: 'capitalize', display: 'block', mb: 0.5 }}
              >
                {getDayLabel(day)}
              </Typography>
              {dayEvents.length === 0 ? (
                <Typography variant="caption" color="text.disabled">
                  Sin eventos
                </Typography>
              ) : (
                dayEvents.map((event) => (
                  <Box
                    key={event.id}
                    sx={{
                      p: 0.5,
                      mb: 0.5,
                      borderRadius: 1,
                      bgcolor: event.status === 'completed'
                        ? 'success.light'
                        : event.is_overdue
                          ? 'error.light'
                          : 'action.hover',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                    }}
                  >
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="caption" noWrap display="block">
                        {event.description || event.type}
                      </Typography>
                      {event.responsible_id && (
                        <Typography variant="caption" color="text.secondary" noWrap display="block">
                          {personsMap[event.responsible_id] || ''}
                        </Typography>
                      )}
                    </Box>
                    {event.status === 'pending' && onQuickComplete && (
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => onQuickComplete(event.id)}
                        sx={{ p: 0.25 }}
                      >
                        <CheckCircle sx={{ fontSize: 16 }} />
                      </IconButton>
                    )}
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        )
      })}
    </Box>
  )
}
