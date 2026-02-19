<script setup lang="ts">
import { ref, computed } from 'vue';
import { updateDiaper, updateFeeding, deleteDiaper, deleteFeeding, type Diaper, type Feeding } from '../api';
import { formatTime, formatDuration } from '../helpers/time';

interface Props {
  diapers: Diaper[];
  feedings: Feeding[];
  loading: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  updated: [];
}>();

const showEditModal = ref(false);
const editingEvent = ref<{ type: 'diaper' | 'feeding', data: any } | null>(null);
const showDeleteConfirm = ref(false);
const deleteTarget = ref<{ type: 'diaper' | 'feeding', id: number } | null>(null);
const showAlert = ref(false);
const alertMessage = ref('');

// Edit actions
function startEdit(type: 'diaper' | 'feeding', data: any) {
  const eventData = { ...data };
  
  // Convert ISO timestamps to datetime-local format (YYYY-MM-DDTHH:mm)
  if (type === 'diaper' && eventData.timestamp) {
    eventData.timestamp = new Date(eventData.timestamp).toISOString().slice(0, 16);
  } else if (type === 'feeding') {
    if (eventData.start_time) {
      eventData.start_time = new Date(eventData.start_time).toISOString().slice(0, 16);
    }
    if (eventData.end_time) {
      eventData.end_time = new Date(eventData.end_time).toISOString().slice(0, 16);
    }
  }
  
  editingEvent.value = { type, data: eventData };
  showEditModal.value = true;
}

async function saveEdit() {
  if (!editingEvent.value) return;
  
  try {
    if (editingEvent.value.type === 'diaper') {
      // Convert back to ISO format
      const timestamp = new Date(editingEvent.value.data.timestamp).toISOString();
      await updateDiaper(
        editingEvent.value.data.id,
        editingEvent.value.data.type,
        timestamp
      );
    } else {
      // Convert back to ISO format
      const startTime = new Date(editingEvent.value.data.start_time).toISOString();
      const endTime = new Date(editingEvent.value.data.end_time).toISOString();
      await updateFeeding(
        editingEvent.value.data.id,
        startTime,
        endTime
      );
    }
    
    showEditModal.value = false;
    editingEvent.value = null;
    emit('updated');
  } catch (error) {
    console.error('Failed to update:', error);
    alertMessage.value = 'Failed to update record. Please try again.';
    showAlert.value = true;
  }
}

function cancelEdit() {
  showEditModal.value = false;
  editingEvent.value = null;
}

// Delete actions
function confirmDelete(type: 'diaper' | 'feeding', id: number) {
  deleteTarget.value = { type, id };
  showDeleteConfirm.value = true;
}

async function handleDelete() {
  if (!deleteTarget.value) return;
  
  try {
    if (deleteTarget.value.type === 'diaper') {
      await deleteDiaper(deleteTarget.value.id);
    } else {
      await deleteFeeding(deleteTarget.value.id);
    }
    showDeleteConfirm.value = false;
    deleteTarget.value = null;
    emit('updated');
  } catch (error) {
    console.error(`Failed to delete ${deleteTarget.value?.type}:`, error);
    alertMessage.value = `Failed to delete ${deleteTarget.value?.type}. Please try again.`;
    showAlert.value = true;
  }
}

// Combined events for timeline
const allEvents = computed(() => {
  const events = [
    ...props.diapers.map(d => ({
      id: `diaper-${d.id}`,
      type: 'diaper' as const,
      timestamp: d.timestamp,
      data: d
    })),
    ...props.feedings.map(f => ({
      id: `feeding-${f.id}`,
      type: 'feeding' as const,
      timestamp: f.start_time,
      data: f
    }))
  ];
  
  return events.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
});
</script>

<template>
  <v-card elevation="8">
    <v-card-title class="text-h5">Recent Activity</v-card-title>
    <v-card-text>
      <v-progress-circular 
        v-if="loading" 
        indeterminate 
        color="primary"
        class="d-block mx-auto"
      />
      
      <v-alert v-else-if="allEvents.length === 0" type="info" variant="tonal">
        No activities recorded yet
      </v-alert>

      <v-list v-else lines="two">
        <v-list-item
          v-for="event in allEvents"
          :key="event.id"
          class="mb-2"
        >
          <template v-slot:prepend>
            <v-avatar size="48" color="grey-lighten-3">
              <span class="text-h5">
                {{ event.type === 'diaper' 
                  ? (event.data.type === 'pee' ? '💧' : event.data.type === 'poop' ? '💩' : event.data.type === 'blowout' ? '💥' : '🦆')
                  : '🍼' 
                }}
              </span>
            </v-avatar>
          </template>

          <v-list-item-title class="text-capitalize">
            <span v-if="event.type === 'diaper'">
              Diaper - {{ event.data.type }}
            </span>
            <span v-else>
              Feeding - {{ formatDuration(event.data.start_time, event.data.end_time) }}
            </span>
          </v-list-item-title>

          <v-list-item-subtitle>
            {{ formatTime(event.timestamp) }}
          </v-list-item-subtitle>

          <template v-slot:append>
            <v-btn
              icon="mdi-pencil"
              variant="text"
              size="small"
              @click="startEdit(event.type, event.data)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click="confirmDelete(event.type, event.data.id)"
            />
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>

    <!-- Edit Modal -->
    <v-dialog v-model="showEditModal" max-width="400">
      <v-card v-if="editingEvent">
        <v-card-title class="text-h5 text-center">
          Edit {{ editingEvent.type === 'diaper' ? 'Diaper' : 'Feeding' }}
        </v-card-title>
        <v-card-text>
          <!-- Edit Diaper -->
          <div v-if="editingEvent.type === 'diaper'">
            <v-label class="mb-2 d-block">Type:</v-label>
            <v-row dense class="mb-4">
              <v-col cols="6">
                <v-btn
                  block
                  class="pee-btn"
                  :variant="editingEvent.data.type === 'pee' ? 'flat' : 'outlined'"
                  @click="editingEvent.data.type = 'pee'"
                >
                  💧 Pee
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn
                  block
                  class="poop-btn"
                  :variant="editingEvent.data.type === 'poop' ? 'flat' : 'outlined'"
                  @click="editingEvent.data.type = 'poop'"
                >
                  💩 Poop
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn
                  block
                  class="both-btn"
                  :variant="editingEvent.data.type === 'both' ? 'flat' : 'outlined'"
                  @click="editingEvent.data.type = 'both'"
                >
                  🦆 Both
                </v-btn>
              </v-col>
              <v-col cols="6">
                <v-btn
                  block
                  class="blowout-btn"
                  :variant="editingEvent.data.type === 'blowout' ? 'flat' : 'outlined'"
                  @click="editingEvent.data.type = 'blowout'"
                >
                  💥 Blowout
                </v-btn>
              </v-col>
            </v-row>
            <v-text-field
              v-model="editingEvent.data.timestamp"
              label="Time"
              type="datetime-local"
              variant="outlined"
            />
          </div>
          
          <!-- Edit Feeding -->
          <div v-else>
            <v-text-field
              v-model="editingEvent.data.start_time"
              label="Start Time"
              type="datetime-local"
              variant="outlined"
              class="mb-4"
            />
            <v-text-field
              v-model="editingEvent.data.end_time"
              label="End Time"
              type="datetime-local"
              variant="outlined"
            />
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="cancelEdit">Cancel</v-btn>
          <v-btn color="success" variant="tonal" @click="saveEdit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Modal -->
    <v-dialog v-model="showDeleteConfirm" max-width="400">
      <v-card>
        <v-card-title class="text-h5 text-center">
          Confirm Delete
        </v-card-title>
        <v-card-text class="text-center">
          <p v-if="deleteTarget">Are you sure you want to delete this {{ deleteTarget.type }} record?</p>
          <p class="text-caption text-grey">This action cannot be undone.</p>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="showDeleteConfirm = false; deleteTarget = null;">Cancel</v-btn>
          <v-btn color="error" variant="tonal" @click="handleDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Alert Modal -->
    <v-dialog v-model="showAlert" max-width="400">
      <v-card>
        <v-card-title class="text-h5 text-center">
          Error
        </v-card-title>
        <v-card-text class="text-center">
          <p>{{ alertMessage }}</p>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" block @click="showAlert = false">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>
.pee-btn {
  background: #74b9ff !important;
  color: white !important;
}

.poop-btn {
  background: #a29bfe !important;
  color: white !important;
}

.both-btn {
  background: #fd79a8 !important;
  color: white !important;
}

.blowout-btn {
  background: #ff6348 !important;
  color: white !important;
}
</style>
