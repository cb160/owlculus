<template>
  <v-card variant="outlined">
    <v-card-title class="d-flex align-center">
      <v-icon start>mdi-heart-pulse</v-icon>
      Wellbeing Records
      <v-spacer />
      <v-chip 
        v-if="records.length > 0"
        color="primary" 
        size="small" 
        variant="tonal"
      >
        {{ records.length }} Record{{ records.length !== 1 ? 's' : '' }}
      </v-chip>
    </v-card-title>
    
    <v-divider />

    <!-- Records Table -->
    <v-data-table
      :headers="headers"
      :items="records"
      :loading="loading"
      :items-per-page="10"
      class="elevation-0"
      hover
    >
      <template #[`item.client_entity`]="{ item }">
        <div v-if="item.client_entity">
          <div class="font-weight-medium">
            {{ getClientDisplayName(item.client_entity) }}
          </div>
          <div class="text-caption text-medium-emphasis">
            ID: {{ item.client_entity.id }}
          </div>
        </div>
        <span v-else class="text-medium-emphasis">Unknown</span>
      </template>

      <template #[`item.current_status`]="{ item }">
        <v-chip
          :color="getStatusColor(item.current_status)"
          size="small"
          variant="flat"
        >
          {{ item.current_status }}
        </v-chip>
      </template>

      <template #[`item.assessment_date`]="{ item }">
        {{ formatDate(item.assessment_date) }}
      </template>

      <template #[`item.created_at`]="{ item }">
        {{ formatDate(item.created_at) }}
      </template>

      <template #[`item.treatment_plan`]="{ item }">
        <div v-if="item.treatment_plan" class="text-truncate" style="max-width: 200px;">
          {{ item.treatment_plan }}
        </div>
        <span v-else class="text-medium-emphasis">No plan</span>
      </template>

      <template #[`item.actions`]="{ item }">
        <div class="d-flex ga-1">
          <v-btn
            icon="mdi-eye"
            size="small"
            variant="text"
            @click="$emit('view', item)"
          />
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click="$emit('edit', item)"
          />
          <v-btn
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click="confirmDelete(item)"
          />
        </div>
      </template>

      <template #no-data>
        <div class="text-center pa-8">
          <v-icon class="mb-4" color="grey" icon="mdi-heart-pulse" size="64" />
          <div class="text-h6 mb-2">No Wellbeing Records</div>
          <div class="text-body-2 text-medium-emphasis mb-4">
            Create wellbeing records to track client treatment plans and progress
          </div>
          <v-btn 
            v-if="clientEntities.length > 0"
            color="primary" 
            @click="$emit('refresh')"
          >
            Refresh Records
          </v-btn>
        </div>
      </template>
    </v-data-table>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon color="error" start>mdi-alert</v-icon>
          Confirm Deletion
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-1 mb-4">
            Are you sure you want to delete this wellbeing record?
          </p>
          
          <v-alert type="warning" variant="tonal" class="mb-4">
            This action cannot be undone. All associated treatment actions will remain but will no longer be linked to this wellbeing record.
          </v-alert>
          
          <div v-if="recordToDelete" class="text-body-2">
            <strong>Client:</strong> {{ getClientDisplayName(recordToDelete.client_entity) }}<br>
            <strong>Status:</strong> {{ recordToDelete.current_status }}<br>
            <strong>Assessment Date:</strong> {{ formatDate(recordToDelete.assessment_date) }}
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">
            Cancel
          </v-btn>
          <v-btn 
            color="error" 
            variant="flat"
            :loading="deleting"
            @click="handleDelete"
          >
            Delete Record
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { format } from 'date-fns'

defineProps({
  caseId: {
    type: Number,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  records: {
    type: Array,
    default: () => [],
  },
  clientEntities: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['refresh', 'view', 'edit', 'delete'])

// Data
const showDeleteDialog = ref(false)
const recordToDelete = ref(null)
const deleting = ref(false)

// Table headers
const headers = [
  { title: 'Client', key: 'client_entity', sortable: false },
  { title: 'Status', key: 'current_status', sortable: true },
  { title: 'Treatment Plan', key: 'treatment_plan', sortable: false },
  { title: 'Assessment Date', key: 'assessment_date', sortable: true },
  { title: 'Created', key: 'created_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, width: 120 },
]

// Methods
function getClientDisplayName(clientEntity) {
  if (!clientEntity || !clientEntity.data) return 'Unknown Client'
  
  const data = clientEntity.data
  if (data.first_name || data.last_name) {
    return `${data.first_name || ''} ${data.last_name || ''}`.trim()
  }
  
  return data.email || data.phone || 'Unnamed Client'
}

function getStatusColor(status) {
  const colors = {
    'Active': 'success',
    'On Hold': 'warning', 
    'Completed': 'primary',
    'Discontinued': 'error'
  }
  return colors[status] || 'grey'
}

function formatDate(dateString) {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch {
    return 'Invalid date'
  }
}

function confirmDelete(record) {
  recordToDelete.value = record
  showDeleteDialog.value = true
}

async function handleDelete() {
  if (!recordToDelete.value) return
  
  try {
    deleting.value = true
    emit('delete', recordToDelete.value)
    showDeleteDialog.value = false
    recordToDelete.value = null
  } catch (error) {
    console.error('Delete failed:', error)
  } finally {
    deleting.value = false
  }
}
</script>