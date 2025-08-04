<template>
  <div>
    <!-- Header -->
    <div class="d-flex align-center justify-space-between mb-4">
      <div>
        <div class="text-h6">Client Wellbeing</div>
        <div class="text-body-2 text-medium-emphasis">
          Manage wellbeing records and treatment plans for clients
        </div>
      </div>
      <v-btn 
        v-if="canManageWellbeing" 
        color="primary" 
        prepend-icon="mdi-plus"
        @click="showCreateDialog = true"
      >
        New Wellbeing Record
      </v-btn>
    </div>

    <!-- Client Entities Info -->
    <v-alert 
      v-if="clientEntities.length === 0 && !loadingClientEntities" 
      type="info" 
      variant="tonal" 
      class="mb-4"
    >
      <div class="text-body-2">
        No client entities found in this case. To create wellbeing records, first mark person entities as clients in the Entities tab.
      </div>
    </v-alert>

    <!-- Wellbeing Records Table -->
    <WellbeingRecordTable 
      :case-id="caseId"
      :loading="loading" 
      :records="wellbeingRecords"
      :client-entities="clientEntities"
      @refresh="loadWellbeingRecords"
      @view="handleViewRecord"
      @edit="handleEditRecord"
      @delete="handleDeleteRecord"
    />

    <!-- Create Wellbeing Record Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="800" persistent>
      <WellbeingRecordForm
        :case-id="caseId"
        :client-entities="clientEntities"
        @cancel="showCreateDialog = false"
        @save="handleCreateRecord"
      />
    </v-dialog>

    <!-- Edit Wellbeing Record Dialog -->
    <v-dialog v-model="showEditDialog" max-width="800" persistent>
      <WellbeingRecordForm
        v-if="selectedRecord"
        :case-id="caseId"
        :client-entities="clientEntities"
        :record="selectedRecord"
        @cancel="showEditDialog = false"
        @save="handleUpdateRecord"
      />
    </v-dialog>

    <!-- View Wellbeing Record Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="1000" persistent>
      <WellbeingRecordDetails
        v-if="selectedRecord"
        :record="selectedRecord"
        @close="showDetailsDialog = false"
        @edit="handleEditFromDetails"
        @treatment-action-created="handleTreatmentActionCreated"
      />
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import WellbeingRecordTable from '@/components/wellbeing/WellbeingRecordTable.vue'
import WellbeingRecordForm from '@/components/wellbeing/WellbeingRecordForm.vue'
import WellbeingRecordDetails from '@/components/wellbeing/WellbeingRecordDetails.vue'
import { wellbeingService } from '@/services/wellbeing'

const props = defineProps({
  caseId: {
    type: Number,
    required: true,
  },
})

const authStore = useAuthStore()

// Data
const loading = ref(false)
const loadingClientEntities = ref(false)
const wellbeingRecords = ref([])
const clientEntities = ref([])
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedRecord = ref(null)

// Computed
const canManageWellbeing = computed(() => {
  return authStore.user?.role !== 'Analyst'
})

// Methods
async function loadWellbeingRecords() {
  try {
    loading.value = true
    const records = await wellbeingService.getWellbeingRecords({ 
      case_id: props.caseId 
    })
    wellbeingRecords.value = records
  } catch (error) {
    console.error('Failed to load wellbeing records:', error)
  } finally {
    loading.value = false
  }
}

async function loadClientEntities() {
  try {
    loadingClientEntities.value = true
    const entities = await wellbeingService.getCaseClientEntities(props.caseId)
    clientEntities.value = entities
  } catch (error) {
    console.error('Failed to load client entities:', error)
  } finally {
    loadingClientEntities.value = false
  }
}

async function handleCreateRecord(recordData) {
  try {
    await wellbeingService.createWellbeingRecord(recordData)
    showCreateDialog.value = false
    await loadWellbeingRecords()
  } catch (error) {
    console.error('Failed to create wellbeing record:', error)
    throw error
  }
}

async function handleUpdateRecord(recordData) {
  try {
    await wellbeingService.updateWellbeingRecord(selectedRecord.value.id, recordData)
    showEditDialog.value = false
    selectedRecord.value = null
    await loadWellbeingRecords()
  } catch (error) {
    console.error('Failed to update wellbeing record:', error)
    throw error
  }
}

async function handleDeleteRecord(record) {
  try {
    await wellbeingService.deleteWellbeingRecord(record.id)
    await loadWellbeingRecords()
  } catch (error) {
    console.error('Failed to delete wellbeing record:', error)
    throw error
  }
}

async function handleViewRecord(record) {
  try {
    // Load full details
    const detailedRecord = await wellbeingService.getWellbeingRecordDetails(record.id)
    selectedRecord.value = detailedRecord
    showDetailsDialog.value = true
  } catch (error) {
    console.error('Failed to load record details:', error)
  }
}

function handleEditRecord(record) {
  selectedRecord.value = record
  showEditDialog.value = true
}

function handleEditFromDetails() {
  showDetailsDialog.value = false
  showEditDialog.value = true
}

function handleTreatmentActionCreated() {
  // Reload the record details to show the new treatment action
  if (selectedRecord.value) {
    handleViewRecord(selectedRecord.value)
  }
}

// Watch for case ID changes
watch(
  () => props.caseId,
  () => {
    loadWellbeingRecords()
    loadClientEntities()
  },
)

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadWellbeingRecords(),
    loadClientEntities()
  ])
})
</script>