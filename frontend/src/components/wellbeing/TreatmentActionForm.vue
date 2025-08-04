<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon start>mdi-clipboard-plus</v-icon>
      Create Treatment Action
    </v-card-title>
    
    <v-divider />
    
    <v-form ref="formRef" @submit.prevent="handleSubmit">
      <v-card-text class="pa-6">
        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="text-body-2">
            Treatment actions are tasks that will be automatically linked to this wellbeing record.
            They can be managed through the regular task system.
          </div>
        </v-alert>

        <v-row>
          <!-- Title -->
          <v-col cols="12">
            <v-text-field
              v-model="form.title"
              :rules="[rules.required]"
              label="Action Title"
              placeholder="e.g., Initial assessment session"
              variant="outlined"
              prepend-inner-icon="mdi-format-title"
            />
          </v-col>

          <!-- Description -->
          <v-col cols="12">
            <v-textarea
              v-model="form.description"
              label="Description"
              placeholder="Detailed description of the treatment action..."
              variant="outlined"
              prepend-inner-icon="mdi-text"
              rows="3"
              auto-grow
            />
          </v-col>

          <!-- Priority and Status -->
          <v-col cols="12" sm="6">
            <v-select
              v-model="form.priority"
              :items="priorityOptions"
              :rules="[rules.required]"
              label="Priority"
              variant="outlined"
              prepend-inner-icon="mdi-flag"
            />
          </v-col>

          <v-col cols="12" sm="6">
            <v-select
              v-model="form.status"
              :items="statusOptions"
              :rules="[rules.required]"
              label="Status"
              variant="outlined"
              prepend-inner-icon="mdi-circle-slice-3"
            />
          </v-col>

          <!-- Due Date -->
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.due_date"
              label="Due Date (Optional)"
              type="date"
              variant="outlined"
              prepend-inner-icon="mdi-calendar"
              clearable
            />
          </v-col>

          <!-- Assigned To -->
          <v-col cols="12" sm="6">
            <v-select
              v-model="form.assigned_to_id"
              :items="userOptions"
              :loading="loadingUsers"
              label="Assign To (Optional)"
              placeholder="Select a user"
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
                    <div class="text-caption">{{ item.raw.role }}</div>
                  </template>
                </v-list-item>
              </template>
            </v-select>
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
          type="submit"
        >
          Create Action
        </v-btn>
      </v-card-actions>
    </v-form>
  </v-card>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/user'
import { wellbeingService } from '@/services/wellbeing'

const props = defineProps({
  record: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['cancel', 'save'])

const authStore = useAuthStore()

// Data
const formRef = ref(null)
const saving = ref(false)
const loadingUsers = ref(false)
const users = ref([])

// Form data
const form = ref({
  title: '',
  description: '',
  priority: 'Medium',
  status: 'Open',
  due_date: '',
  assigned_to_id: null,
})

// Options
const priorityOptions = ['Low', 'Medium', 'High', 'Critical']
const statusOptions = ['Open', 'In Progress', 'Completed', 'Cancelled']

// Computed
const userOptions = computed(() => {
  return users.value.map(user => ({
    title: `${user.first_name} ${user.last_name}`,
    value: user.id,
    raw: user
  }))
})

// Validation rules
const rules = {
  required: (value) => !!value || 'This field is required',
}

// Methods
async function loadUsers() {
  try {
    loadingUsers.value = true
    // Load case users - we'll need to add this method to user service
    const response = await userService.getCaseUsers(props.record.case_id)
    users.value = response
  } catch (error) {
    console.error('Failed to load users:', error)
    // Fallback to current user
    users.value = [authStore.user]
  } finally {
    loadingUsers.value = false
  }
}

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  try {
    saving.value = true
    
    const taskData = {
      case_id: props.record.case_id,
      title: form.value.title,
      description: form.value.description,
      priority: form.value.priority,
      status: form.value.status,
      due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null,
      assigned_to_id: form.value.assigned_to_id,
    }

    // Remove empty strings and null values
    Object.keys(taskData).forEach(key => {
      if (taskData[key] === '' || taskData[key] === null) {
        delete taskData[key]
      }
    })

    await wellbeingService.createTreatmentAction(props.record.id, taskData)
    emit('save')
  } catch (error) {
    console.error('Failed to create treatment action:', error)
    throw error
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadUsers()
})
</script>