import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Box,
  IconButton,
  Chip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Checkbox,
  ListItemButton,
  Divider,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import LogoutIcon from '@mui/icons-material/Logout'
import DeleteIcon from '@mui/icons-material/Delete'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { getTasks, createTask, deleteTask, updateSubTask, deleteSubTask } from '../api/client'
import { Task, SubTask } from '../types'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [openModal, setOpenModal] = useState<boolean>(false)

  // Form state for tasks
  const [title, setTitle] = useState<string>('')
  const [description, setDescription] = useState<string>('')
  const [status, setStatus] = useState<'pending' | 'is_completed'>('pending')
  const [category, setCategory] = useState<'work' | 'personal' | 'urgent'>('work')

  // Fetch tasks with useQuery
  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks', user?.id],
    queryFn: async () => {
      if (!user) return []
      const response = await getTasks(user.id)
      return (response.data.tasks || response.data) as Task[]
    },
    enabled: !!user,
  })

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] })
      handleCloseModal()
    },
  })

  // Delete task mutation
  const deleteTaskMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] })
    },
  })

  // Update subtask mutation (toggle completion)
  const updateSubTaskMutation = useMutation({
    mutationFn: ({ subtaskId, data }: { subtaskId: number; data: { is_completed: boolean } }) =>
      updateSubTask(subtaskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] })
    },
  })

  // Delete subtask mutation
  const deleteSubTaskMutation = useMutation({
    mutationFn: deleteSubTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] })
    },
  })

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleOpenModal = () => {
    setOpenModal(true)
  }

  const handleCloseModal = () => {
    setOpenModal(false)
    resetForm()
  }

  const resetForm = () => {
    setTitle('')
    setDescription('')
    setStatus('pending')
    setCategory('work')
  }

  const handleSubmit = () => {
    if (!user) return
    createTaskMutation.mutate({
      user: user.id,
      title,
      description,
      status,
      category,
    })
  }

  const handleDeleteTask = (taskId: number) => {
    deleteTaskMutation.mutate(taskId)
  }

  const handleToggleSubTask = (subtaskId: number, isCompleted: boolean) => {
    updateSubTaskMutation.mutate({
      subtaskId,
      data: { is_completed: !isCompleted },
    })
  }

  const handleDeleteSubTask = (subtaskId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    deleteSubTaskMutation.mutate(subtaskId)
  }

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'work':
        return 'primary'
      case 'personal':
        return 'secondary'
      case 'urgent':
        return 'error'
      default:
        return 'default'
    }
  }

  const getStatusColor = (stat: string) => {
    return stat === 'is_completed' ? 'success' : 'warning'
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Mis Tareas
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            {user?.email}
          </Typography>
          <Button color="inherit" onClick={handleLogout} startIcon={<LogoutIcon />}>
            Salir
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {tasks.length === 0 ? (
            <Typography variant="h6" color="text.secondary" align="center" sx={{ mt: 4 }}>
              No tienes tareas. Crea una nueva con el botón +
            </Typography>
          ) : (
            tasks.map((task) => (
              <Accordion key={task.id}>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls={`panel-${task.id}-content`}
                  id={`panel-${task.id}-header`}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6">{task.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {task.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        <Chip
                          label={task.category}
                          color={getCategoryColor(task.category) as any}
                          size="small"
                        />
                        <Chip
                          label={task.status === 'is_completed' ? 'Completada' : 'Pendiente'}
                          color={getStatusColor(task.status) as any}
                          size="small"
                        />
                        {task.subtasks && task.subtasks.length > 0 && (
                          <Chip
                            label={`${task.completed_subtasks_count}/${task.subtasks_count} subtareas`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>
                    <IconButton
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation()
                        task.id && handleDeleteTask(task.id)
                      }}
                      disabled={deleteTaskMutation.isPending}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {task.subtasks && task.subtasks.length > 0 ? (
                    <>
                      <Divider sx={{ mb: 2 }} />
                      <Typography variant="subtitle1" gutterBottom>
                        Subtareas (generadas por IA)
                      </Typography>
                      <List>
                        {task.subtasks.map((subtask: SubTask) => (
                          <ListItem
                            key={subtask.id}
                            secondaryAction={
                              <IconButton
                                edge="end"
                                aria-label="delete"
                                onClick={(e) => subtask.id && handleDeleteSubTask(subtask.id, e)}
                                disabled={deleteSubTaskMutation.isPending}
                              >
                                <DeleteIcon />
                              </IconButton>
                            }
                            disablePadding
                          >
                            <ListItemButton
                              onClick={() => subtask.id && handleToggleSubTask(subtask.id, subtask.is_completed)}
                              dense
                            >
                              <Checkbox
                                edge="start"
                                checked={subtask.is_completed}
                                tabIndex={-1}
                                disableRipple
                              />
                              <ListItemText
                                primary={subtask.title}
                                sx={{
                                  textDecoration: subtask.is_completed ? 'line-through' : 'none',
                                  color: subtask.is_completed ? 'text.secondary' : 'text.primary',
                                }}
                              />
                            </ListItemButton>
                          </ListItem>
                        ))}
                      </List>
                    </>
                  ) : (
                    <Typography variant="body2" color="text.secondary" align="center">
                      Esta tarea no tiene subtareas generadas
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
            ))
          )}
        </Box>
      </Container>

      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleOpenModal}
      >
        <AddIcon />
      </Fab>

      {/* Modal para crear tarea */}
      <Dialog open={openModal} onClose={handleCloseModal} maxWidth="sm" fullWidth>
        <DialogTitle>Nueva Tarea</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Título"
              fullWidth
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            <TextField
              label="Descripción"
              fullWidth
              multiline
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />

            <TextField
              label="Estado"
              select
              fullWidth
              value={status}
              onChange={(e) => setStatus(e.target.value as 'pending' | 'is_completed')}
            >
              <MenuItem value="pending">Pendiente</MenuItem>
              <MenuItem value="is_completed">Completada</MenuItem>
            </TextField>

            <TextField
              label="Categoría"
              select
              fullWidth
              value={category}
              onChange={(e) => setCategory(e.target.value as 'work' | 'personal' | 'urgent')}
            >
              <MenuItem value="work">Trabajo</MenuItem>
              <MenuItem value="personal">Personal</MenuItem>
              <MenuItem value="urgent">Urgente</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModal}>Cancelar</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={createTaskMutation.isPending || !title || !description}
          >
            {createTaskMutation.isPending ? 'Creando...' : 'Crear Tarea'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
