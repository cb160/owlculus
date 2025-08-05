<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon start>{{ isEdit ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
      {{ isEdit ? 'Edit Wellbeing Record' : 'Create Wellbeing Record' }}
    </v-card-title>
    
    <v-divider />
    
    <v-form ref="formRef" @submit.prevent="handleSubmit">
      <v-card-text class="pa-6">
        <v-row>
          <!-- Client Selection -->
          <v-col cols="12">
            <v-select
              v-model="form.client_entity_id"
              :items="clientEntityOptions"
              :rules="[rules.required]"
              :disabled="isEdit"
              label="Client"
              placeholder="Select a client"
              variant="outlined"
              prepend-inner-icon="mdi-account"
              clearable
            >
              <template #item="{ props: itemProps, item }">
                <v-list-item v-bind="itemProps">
                  <template #title>
                    <div class="font-weight-medium">{{ item.title }}</div>
                  </template>
                  <template #subtitle>
                    <div class="text-caption">ID: {{ item.value }} • {{ item.raw.entity_type }}</div>
                  </template>
                </v-list-item>
              </template>
            </v-select>
            <div v-if="clientEntities.length === 0" class="text-caption text-medium-emphasis mt-1">
              No client entities found. Create person entities and mark them as clients first.
            </div>
          </v-col>

          <!-- Assessment Date -->
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.assessment_date"
              :rules="[rules.required]"
              label="Assessment Date"
              type="date"
              variant="outlined"
              prepend-inner-icon="mdi-calendar"
            />
          </v-col>

          <!-- Current Status -->
          <v-col cols="12" sm="6">
            <v-select
              v-model="form.current_status"
              :items="statusOptions"
              :rules="[rules.required]"
              label="Current Status"
              variant="outlined"
              prepend-inner-icon="mdi-flag"
            />
          </v-col>

          <!-- Treatment Plan -->
          <v-col cols="12">
            <v-textarea
              v-model="form.treatment_plan"
              label="Treatment Plan"
              placeholder="Describe the treatment plan, goals, and approach..."
              variant="outlined"
              prepend-inner-icon="mdi-clipboard-text"
              rows="4"
              auto-grow
            />
          </v-col>

          <!-- Notes -->
          <v-col cols="12">
            <v-textarea
              v-model="form.notes"
              label="Notes"
              placeholder="Additional notes and observations..."
              variant="outlined"
              prepend-inner-icon="mdi-note-text"
              rows="3"
              auto-grow
            />
          </v-col>
        </v-row>
      </v-card-text>
      
      <v-divider />
      
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="$emit('cancel')">
          Cancel
        </v-btn>
        <v-btn 
          color="primary" 
          variant="flat"
          :loading="saving"
          :disabled="!form.client_entity_id || clientEntities.length === 0"
          type="submit"
        >
          {{ isEdit ? 'Update Record' : 'Create Record' }}
        </v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { format } from 'date-fns'

const props = defineProps({
  caseId: {
    type: Number,
    required: true,
  },
  clientEntities: {
    type: Array,
    default: () => [],
  },
  record: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['cancel', 'save'])

// Data
const formRef = ref(null)
const saving = ref(false)

// Form data
const form = ref({
  client_entity_id: null,
  assessment_date: format(new Date(), 'yyyy-MM-dd'),
  current_status: 'Active',
  treatment_plan: '',
  notes: '',
})

// Computed
const isEdit = computed(() => !!props.record)

const statusOptions = [
  'Active',
  'On Hold', 
  'Completed',
  'Discontinued'
]

const clientEntityOptions = computed(() => {
  return props.clientEntities.map(entity => ({
    title: getClientDisplayName(entity),
    value: entity.id,
    entity_type: entity.entity_type,
    raw: entity
  }))
})

// Validation rules
const rules = {
  required: (value) => !!value || 'This field is required',
}

// Methods
function getClientDisplayName(clientEntity) {
  if (!clientEntity || !clientEntity.data) return 'Unknown Client'
  
  const data = clientEntity.data
  if (data.first_name || data.last_name) {
    return `${data.first_name || ''} ${data.last_name || ''}`.trim()
  }
  
  return data.email || data.phone || 'Unnamed Client'
}

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  try {
    saving.value = true
    
    const recordData = {
      case_id: props.caseId,
      client_entity_id: form.value.client_entity_id,
      assessment_date: new Date(form.value.assessment_date).toISOString(),
      current_status: form.value.current_status,
      treatment_plan: form.value.treatment_plan,
      notes: form.value.notes,
    }

    // Remove empty strings
    Object.keys(recordData).forEach(key => {
      if (recordData[key] === '') {
        recordData[key] = null
      }
    })

    emit('save', recordData)
  } catch (error) {
    console.error('Form submission error:', error)
  } finally {
    saving.value = false
  }
}

// Watch for record changes to populate form in edit mode
watch(
  () => props.record,
  (newRecord) => {
    if (newRecord) {
      form.value = {
        client_entity_id: newRecord.client_entity_id,
        assessment_date: format(new Date(newRecord.assessment_date), 'yyyy-MM-dd'),
        current_status: newRecord.current_status,
        treatment_plan: newRecord.treatment_plan || '',
        notes: newRecord.notes || '',
      }
    }
  },
  { immediate: true }
)
</script>