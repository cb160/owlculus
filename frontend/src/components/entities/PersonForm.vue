<template>
  <v-card variant="outlined">
    <v-card-title class="text-subtitle-1">
      <v-icon start>mdi-account</v-icon>
      Personal Details
    </v-card-title>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            :model-value="modelValue.first_name"
            @update:model-value="updateField('first_name', $event)"
            label="First Name"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-account-outline"
          />
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            :model-value="modelValue.last_name"
            @update:model-value="updateField('last_name', $event)"
            label="Last Name"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-account-outline"
          />
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            :model-value="modelValue.email"
            @update:model-value="updateField('email', $event)"
            label="Email"
            type="email"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-email-outline"
          />
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            :model-value="modelValue.phone"
            @update:model-value="updateField('phone', $event)"
            label="Phone"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-phone-outline"
          />
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            :model-value="modelValue.date_of_birth"
            @update:model-value="updateField('date_of_birth', $event)"
            label="Date of Birth"
            type="date"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-cake-variant-outline"
          />
        </v-col>

        <v-col cols="12" md="6">
          <v-select
            :model-value="modelValue.gender"
            @update:model-value="updateField('gender', $event)"
            :items="['Male', 'Female', 'Other', 'Prefer not to say']"
            label="Gender"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-human-male-female"
            clearable
          />
        </v-col>

        <!-- Client Designation Section -->
        <v-col cols="12">
          <v-divider class="my-2" />
          <div class="text-subtitle-2 mb-3 d-flex align-center">
            <v-icon start size="small">mdi-heart-pulse</v-icon>
            Wellbeing Support
          </div>
        </v-col>

        <v-col cols="12">
          <v-switch
            :model-value="modelValue.is_client"
            @update:model-value="updateField('is_client', $event)"
            label="This person is a client requiring wellbeing support"
            color="primary"
            density="comfortable"
            hide-details
          />
          <div class="text-caption text-medium-emphasis mt-1">
            Marking a person as a client enables wellbeing record creation and treatment planning
          </div>
        </v-col>

        <!-- Additional Information -->
        <v-col cols="12">
          <v-divider class="my-2" />
          <div class="text-subtitle-2 mb-3">Additional Information</div>
        </v-col>

        <v-col cols="12">
          <v-textarea
            :model-value="modelValue.notes"
            @update:model-value="updateField('notes', $event)"
            label="Notes"
            placeholder="Additional notes about this person..."
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-note-text-outline"
            rows="3"
            auto-grow
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { entityFormProps, entityFormEmits, useEntityFormField } from '@/composables/useEntityForm'

const props = defineProps(entityFormProps)
const emit = defineEmits(entityFormEmits)

const { updateField } = useEntityFormField(props, emit)
</script>
