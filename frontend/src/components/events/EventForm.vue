<template>
  <v-card>
    <v-card-title>
      {{ isEdit ? 'Edit Event' : 'New Event' }}
    </v-card-title>
    
    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
        <v-text-field
          v-model="formData.title"
          label="Event Title"
          :rules="titleRules"
          required
          density="comfortable"
          class="mb-4"
        />

        <v-select
          v-model="formData.event_type"
          :items="eventTypes"
          item-title="label"
          item-value="value"
          label="Event Type"
          :rules="eventTypeRules"
          required
          density="comfortable"
          class="mb-4"
        />

        <v-select
          v-model="formData.status"
          :items="statusOptions"
          item-title="label"
          item-value="value"
          label="Status"
          :rules="statusRules"
          required
          density="comfortable"
          class="mb-4"
        />

        <v-text-field
          v-model="formData.event_date"
          label="Event Date & Time"
          type="datetime-local"
          :rules="eventDateRules"
          required
          density="comfortable"
          class="mb-4"
        />

        <v-textarea
          v-model="formData.notes"
          label="Notes"
          rows="4"
          density="comfortable"
          class="mb-4"
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn @click="$emit('cancel')">Cancel</v-btn>
      <v-btn
        color="primary"
        :disabled="!valid"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ isEdit ? 'Update' : 'Create' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useEventStore } from '@/stores/eventStore'

const props = defineProps({
  caseId: {
    type: Number,
    required: true,
  },
  event: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save', 'cancel'])

const eventStore = useEventStore()

// Data
const form = ref(null)
const valid = ref(false)
const loading = ref(false)

const formData = ref({
  title: '',
  event_type: 'call',
  status: 'draft',
  event_date: new Date().toISOString().slice(0, 16), // Format for datetime-local
  notes: '',
})

// Computed
const isEdit = computed(() => !!props.event)

// Form options
const eventTypes = [
  { label: 'Call', value: 'call' },
  { label: 'Counselling', value: 'counselling' },
  { label: 'Investigation', value: 'investigation' },
]

const statusOptions = [
  { label: 'Draft', value: 'draft' },
  { label: 'Final', value: 'final' },
]

// Validation rules
const titleRules = [
  (v) => !!v || 'Event title is required',
  (v) => (v && v.length >= 3) || 'Title must be at least 3 characters',
]

const eventTypeRules = [
  (v) => !!v || 'Event type is required',
]

const statusRules = [
  (v) => !!v || 'Status is required',
]

const eventDateRules = [
  (v) => !!v || 'Event date is required',
]

// Methods
async function handleSubmit() {
  if (!valid.value) return

  loading.value = true
  
  try {
    const eventData = {
      ...formData.value,
      case_id: props.caseId,
      // Convert datetime-local format to ISO string
      event_date: new Date(formData.value.event_date).toISOString(),
    }

    if (isEdit.value) {
      await eventStore.updateEvent(props.event.id, eventData)
    } else {
      await eventStore.createEvent(eventData)
    }

    emit('save')
  } catch (error) {
    console.error('Failed to save event:', error)
    // TODO: Show error message to user
  } finally {
    loading.value = false
  }
}

// Watch for event changes to populate form
watch(
  () => props.event,
  (newEvent) => {
    if (newEvent) {
      formData.value = {
        title: newEvent.title || '',
        event_type: newEvent.event_type || 'call',
        status: newEvent.status || 'draft',
        event_date: newEvent.event_date 
          ? new Date(newEvent.event_date).toISOString().slice(0, 16)
          : new Date().toISOString().slice(0, 16),
        notes: newEvent.notes || '',
      }
    } else {
      // Reset form for new event
      formData.value = {
        title: '',
        event_type: 'call',
        status: 'draft',
        event_date: new Date().toISOString().slice(0, 16),
        notes: '',
      }
    }
  },
  { immediate: true }
)
</script>