<template>
  <v-card min-height="600">
    <v-card-title class="d-flex align-center">
      <v-icon start>mdi-heart-pulse</v-icon>
      Wellbeing Record Details
      <v-spacer />
      <v-btn
        icon="mdi-pencil"
        size="small"   
        variant="text"
        @click="$emit('edit')"
      />
      <v-btn 
        icon="mdi-close" 
        size="small"
        variant="text" 
        @click="$emit('close')"
      />
    </v-card-title>
    
    <v-divider />
    
    <v-card-text class="pa-0">
      <v-row no-gutters>
        <!-- Record Details -->
        <v-col cols="12" md="7" class="pa-6">
          <div class="mb-6">
            <div class="text-h6 mb-4">Record Information</div>
            
            <!-- Client Info -->
            <div class="mb-4">
              <div class="text-subtitle-2 text-medium-emphasis mb-1">Client</div>
              <div v-if="record.client_entity" class="d-flex align-center">
                <v-avatar size="32" class="mr-3">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">
                    {{ getClientDisplayName(record.client_entity) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ record.client_entity.entity_type }} • ID: {{ record.client_entity.id }}
                  </div>
                </div>
              </div>
              <div v-else class="text-medium-emphasis">No client information</div>
            </div>

            <!-- Status and Dates -->
            <v-row class="mb-4">
              <v-col cols="6">
                <div class="text-subtitle-2 text-medium-emphasis mb-1">Status</div>
                <v-chip
                  :color="getStatusColor(record.current_status)"
                  size="small"
                  variant="flat"
                >
                  {{ record.current_status }}
                </v-chip>
              </v-col>
              <v-col cols="6">
                <div class="text-subtitle-2 text-medium-emphasis mb-1">Assessment Date</div>
                <div>{{ formatDate(record.assessment_date) }}</div>
              </v-col>
            </v-row>

            <!-- Treatment Plan -->
            <div class="mb-4">
              <div class="text-subtitle-2 text-medium-emphasis mb-2">Treatment Plan</div>
              <div v-if="record.treatment_plan" class="text-body-2">
                <div class="bg-grey-lighten-4 pa-3 rounded">
                  {{ record.treatment_plan }}
                </div>
              </div>
              <div v-else class="text-medium-emphasis">No treatment plan specified</div>
            </div>

            <!-- Notes -->
            <div class="mb-4">
              <div class="text-subtitle-2 text-medium-emphasis mb-2">Notes</div>
              <div v-if="record.notes" class="text-body-2">
                <div class="bg-grey-lighten-4 pa-3 rounded">
                  {{ record.notes }}
                </div>
              </div>
              <div v-else class="text-medium-emphasis">No notes</div>
            </div>

            <!-- Metadata -->
            <div class="text-caption text-medium-emphasis">
              <div>Created: {{ formatDateTime(record.created_at) }}</div>
              <div>Updated: {{ formatDateTime(record.updated_at) }}</div>
              <div v-if="record.creator">
                By: {{ record.creator.first_name }} {{ record.creator.last_name }}
              </div>
            </div>
          </div>
        </v-col>

        <!-- Treatment Actions -->
        <v-col cols="12" md="5" class="border-s-md">
          <div class="pa-6">
            <div class="d-flex align-center justify-space-between mb-4">
              <div>
                <div class="text-h6">Treatment Actions</div>
                <div class="text-body-2 text-medium-emphasis">
                  Tasks linked to this wellbeing record
                </div>
              </div>
              <v-btn
                color="primary"
                size="small"
                prepend-icon="mdi-plus"
                @click="showCreateActionDialog = true"
              >
                Add Action
              </v-btn>
            </div>

            <!-- Treatment Actions List -->
            <div v-if="record.treatment_actions && record.treatment_actions.length > 0">
              <v-list class="pa-0">
                <v-list-item
                  v-for="action in record.treatment_actions"
                  :key="action.id"
                  class="px-0 mb-2"
                >
                  <template #prepend>
                    <v-avatar size="32" :color="getTaskStatusColor(action.status)">
                      <v-icon color="white" size="16">
                        {{ getTaskStatusIcon(action.status) }}
                      </v-icon>
                    </v-avatar>
                  </template>

                  <v-list-item-title class="text-body-2 font-weight-medium">
                    {{ action.title }}
                  </v-list-item-title>

                  <v-list-item-subtitle class="text-caption">
                    <div>{{ action.status }} • {{ action.priority }}</div>
                    <div v-if="action.due_date">
                      Due: {{ formatDate(action.due_date) }}
                    </div>
                    <div v-if="action.assigned_to">
                      Assigned: {{ action.assigned_to.first_name }} {{ action.assigned_to.last_name }}
                    </div>
                  </v-list-item-subtitle>

                  <template #append>
                    <v-btn
                      icon="mdi-open-in-new"
                      size="small"
                      variant="text"
                      @click="openTask(action.id)"
                    />
                  </template>
                </v-list-item>
              </v-list>
            </div>

            <!-- Empty State -->
            <div v-else class="text-center pa-4">
              <v-icon class="mb-2" color="grey" icon="mdi-clipboard-list" size="48" />
              <div class="text-body-2 text-medium-emphasis mb-3">
                No treatment actions yet
              </div>
              <v-btn
                color="primary"
                size="small"
                prepend-icon="mdi-plus"
                @click="showCreateActionDialog = true"
              >
                Create First Action
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>

    <!-- Create Treatment Action Dialog -->
    <v-dialog v-model="showCreateActionDialog" max-width="600" persistent>
      <TreatmentActionForm
        :record="record"
        @cancel="showCreateActionDialog = false"
        @save="handleActionCreated"
      />
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { format } from 'date-fns'
import TreatmentActionForm from './TreatmentActionForm.vue'

defineProps({
  record: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'edit', 'treatment-action-created'])

const router = useRouter()

// Data
const showCreateActionDialog = ref(false)

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

function getTaskStatusColor(status) {
  const colors = {
    'Open': 'info',
    'In Progress': 'warning',
    'Completed': 'success',
    'Cancelled': 'error'
  }
  return colors[status] || 'grey'
}

function getTaskStatusIcon(status) {
  const icons = {
    'Open': 'mdi-clock-outline',
    'In Progress': 'mdi-progress-clock',
    'Completed': 'mdi-check-circle',
    'Cancelled': 'mdi-cancel'
  }
  return icons[status] || 'mdi-help-circle'
}

function formatDate(dateString) {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch {
    return 'Invalid date'
  }
}

function formatDateTime(dateString) {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
  } catch {
    return 'Invalid date'
  }
}

function openTask(taskId) {
  router.push(`/tasks/${taskId}`)
}

function handleActionCreated() {
  showCreateActionDialog.value = false
  emit('treatment-action-created')
}
</script>