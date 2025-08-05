<template>
  <div>
    <!-- Header -->
    <div class="d-flex align-center justify-space-between mb-4">
      <div>
        <div class="text-h6">Events</div>
        <div class="text-body-2 text-medium-emphasis">Track case events and activities</div>
      </div>
      <v-btn color="primary" @click="showCreateDialog = true">
        <v-icon start>mdi-plus</v-icon>
        New Event
      </v-btn>
    </div>

    <!-- Events Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="events"
        :loading="loading"
        :items-per-page="25"
        class="elevation-1"
      >
        <template #item.event_type="{ item }">
          <v-chip
            :color="getEventTypeColor(item.event_type)"
            size="small"
            variant="tonal"
          >
            {{ formatEventType(item.event_type) }}
          </v-chip>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="tonal"
          >
            {{ formatStatus(item.status) }}
          </v-chip>
        </template>

        <template #item.event_date="{ item }">
          {{ formatDate(item.event_date) }}
        </template>

        <template #item.creator="{ item }">
          {{ item.creator?.username || 'Unknown' }}
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click="editEvent(item)"
          />
          <v-btn
            icon="mdi-history"
            size="small"
            variant="text"
            @click="showAuditLog(item)"
          />
          <v-btn
            icon="mdi-task"
            size="small"
            variant="text"
            @click="createTaskFromEvent(item)"
            title="Create Task from Event"
          />
        </template>
      </v-data-table>
    </v-card>

    <!-- Create/Edit Event Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="600">
      <EventForm
        :case-id="caseId"
        :event="selectedEvent"
        @cancel="closeDialog"
        @save="handleSaveEvent"
      />
    </v-dialog>

    <!-- Audit Log Dialog -->
    <v-dialog v-model="showAuditDialog" max-width="600">
      <v-card>
        <v-card-title>Event Audit Log</v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="log in auditLogs"
              :key="log.id"
              :subtitle="`by ${log.changed_by?.username} at ${formatDate(log.changed_at)}`"
            >
              <v-list-item-title>{{ formatAction(log.action) }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAuditDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useEventStore } from '@/stores/eventStore'
import EventForm from '@/components/events/EventForm.vue'

const props = defineProps({
  caseId: {
    type: Number,
    required: true,
  },
})

const eventStore = useEventStore()

// Data
const showCreateDialog = ref(false)
const showAuditDialog = ref(false)
const selectedEvent = ref(null)
const auditLogs = ref([])

// Computed
const loading = computed(() => eventStore.loading)
const events = computed(() => eventStore.events.filter((e) => e.case_id === props.caseId))

// Table headers
const headers = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Event Type', key: 'event_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Event Date', key: 'event_date', sortable: true },
  { title: 'Created By', key: 'creator', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false },
]

// Methods
async function loadEvents() {
  await eventStore.fetchEvents({ case_id: props.caseId })
}

function closeDialog() {
  showCreateDialog.value = false
  selectedEvent.value = null
}

async function handleSaveEvent() {
  await loadEvents()
  closeDialog()
}

function editEvent(event) {
  selectedEvent.value = event
  showCreateDialog.value = true
}

async function showAuditLog(event) {
  try {
    auditLogs.value = await eventStore.fetchAuditLogs(event.id)
    showAuditDialog.value = true
  } catch (error) {
    console.error('Failed to load audit logs:', error)
  }
}

function createTaskFromEvent(event) {
  // This would integrate with the task system
  // For now, just show a placeholder
  console.log('Create task from event:', event)
  // TODO: Implement task creation from event
}

// Utility functions
function getEventTypeColor(type) {
  const colors = {
    call: 'blue',
    counselling: 'green',
    investigation: 'orange',
  }
  return colors[type] || 'grey'
}

function getStatusColor(status) {
  const colors = {
    draft: 'orange',
    final: 'green',
  }
  return colors[status] || 'grey'
}

function formatEventType(type) {
  const types = {
    call: 'Call',
    counselling: 'Counselling',
    investigation: 'Investigation',
  }
  return types[type] || type
}

function formatStatus(status) {
  const statuses = {
    draft: 'Draft',
    final: 'Final',
  }
  return statuses[status] || status
}

function formatAction(action) {
  const actions = {
    created: 'Event Created',
    updated: 'Event Updated',
    deleted: 'Event Deleted',
  }
  return actions[action] || action
}

function formatDate(date) {
  return new Date(date).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadEvents()
})
</script>