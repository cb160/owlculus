/**
 * Event management store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

export const useEventStore = defineStore('events', () => {
  // State
  const events = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const getEventById = computed(() => {
    return (id) => events.value.find((event) => event.id === id)
  })

  const getEventsByCase = computed(() => {
    return (caseId) => events.value.filter((event) => event.case_id === caseId)
  })

  // Actions
  async function fetchEvents(filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value)
        }
      })

      const response = await api.get(`/api/events?${params}`)
      events.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEvent(id) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/api/events/${id}`)
      const event = response.data
      
      // Update or add event to the store
      const index = events.value.findIndex((e) => e.id === event.id)
      if (index >= 0) {
        events.value[index] = event
      } else {
        events.value.push(event)
      }
      
      return event
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createEvent(eventData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/events', eventData)
      const newEvent = response.data
      events.value.push(newEvent)
      return newEvent
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateEvent(id, eventData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put(`/api/events/${id}`, eventData)
      const updatedEvent = response.data
      
      const index = events.value.findIndex((e) => e.id === id)
      if (index >= 0) {
        events.value[index] = updatedEvent
      }
      
      return updatedEvent
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteEvent(id) {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/api/events/${id}`)
      events.value = events.value.filter((e) => e.id !== id)
      return true
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAuditLogs(eventId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/api/events/${eventId}/audit-logs`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearEvents() {
    events.value = []
  }

  return {
    // State
    events,
    loading,
    error,
    
    // Getters
    getEventById,
    getEventsByCase,
    
    // Actions
    fetchEvents,
    fetchEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    fetchAuditLogs,
    clearError,
    clearEvents,
  }
})