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
    alert('Failed to update record');
  }
}

function cancelEdit() {
  showEditModal.value = false;
  editingEvent.value = null;
}

// Delete actions
async function handleDelete(type: 'diaper' | 'feeding', id: number) {
  if (confirm(`Delete this ${type} record?`)) {
    try {
      if (type === 'diaper') {
        await deleteDiaper(id);
      } else {
        await deleteFeeding(id);
      }
      emit('updated');
    } catch (error) {
      console.error(`Failed to delete ${type}:`, error);
    }
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
  <section class="events">
    <h2>Recent Activity</h2>
    
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else-if="allEvents.length === 0" class="empty">
      No activities recorded yet
    </div>

    <div v-else class="event-list">
      <div 
        v-for="event in allEvents" 
        :key="event.id"
        class="event-item"
        :class="event.type"
      >
        <div class="event-icon">
          <span v-if="event.type === 'diaper'">
            {{ event.data.type === 'pee' ? '💧' : event.data.type === 'poop' ? '💩' : event.data.type === 'blowout' ? '💥' : '🦆' }}
          </span>
          <span v-else>🍼</span>
        </div>
        
        <div class="event-content">
          <div class="event-title">
            <span v-if="event.type === 'diaper'">
              Diaper - {{ event.data.type }}
            </span>
            <span v-else>
              Feeding - {{ formatDuration(event.data.start_time, event.data.end_time) }}
            </span>
          </div>
          <div class="event-time">
            {{ formatTime(event.timestamp) }}
          </div>
        </div>

        <div class="event-actions">
          <button 
            class="edit-btn"
            @click="startEdit(event.type, event.data)"
            title="Edit"
          >
            ✏️
          </button>
          <button 
            class="delete-btn"
            @click="handleDelete(event.type, event.data.id)"
            title="Delete"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal && editingEvent" class="modal-overlay" @click="cancelEdit">
      <div class="modal" @click.stop>
        <h2>Edit {{ editingEvent.type === 'diaper' ? 'Diaper' : 'Feeding' }}</h2>
        
        <!-- Edit Diaper -->
        <div v-if="editingEvent.type === 'diaper'" class="edit-form">
          <div class="form-group">
            <label>Type:</label>
            <div class="modal-actions">
              <button 
                class="modal-btn pee-btn"
                :class="{ selected: editingEvent.data.type === 'pee' }"
                @click="editingEvent.data.type = 'pee'"
              >
                💧 Pee
              </button>
              <button 
                class="modal-btn poop-btn"
                :class="{ selected: editingEvent.data.type === 'poop' }"
                @click="editingEvent.data.type = 'poop'"
              >
                💩 Poop
              </button>
              <button 
                class="modal-btn both-btn"
                :class="{ selected: editingEvent.data.type === 'both' }"
                @click="editingEvent.data.type = 'both'"
              >
                🦆 Both
              </button>
              <button 
                class="modal-btn blowout-btn"
                :class="{ selected: editingEvent.data.type === 'blowout' }"
                @click="editingEvent.data.type = 'blowout'"
              >
                💥 Blowout
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>Time:</label>
            <input 
              type="datetime-local" 
              v-model="editingEvent.data.timestamp"
              class="time-input"
            />
          </div>
        </div>
        
        <!-- Edit Feeding -->
        <div v-else class="edit-form">
          <div class="form-group">
            <label>Start Time:</label>
            <input 
              type="datetime-local" 
              v-model="editingEvent.data.start_time"
              class="time-input"
            />
          </div>
          <div class="form-group">
            <label>End Time:</label>
            <input 
              type="datetime-local" 
              v-model="editingEvent.data.end_time"
              class="time-input"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="save-btn" @click="saveEdit">Save</button>
          <button class="cancel-btn" @click="cancelEdit">Cancel</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.events {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.events h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.loading, .empty {
  text-align: center;
  color: #666;
  padding: 2rem;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  transition: background 0.2s ease;
}

.event-item:hover {
  background: #e9ecef;
}

.event-icon {
  font-size: 2rem;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 0.5rem;
}

.event-content {
  flex: 1;
}

.event-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
  text-transform: capitalize;
}

.event-time {
  font-size: 0.875rem;
  color: #666;
}

.event-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn {
  background: #74b9ff;
  color: white;
  border: none;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.edit-btn:hover {
  background: #0984e3;
}

.delete-btn {
  background: #ff7675;
  color: white;
  border: none;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.delete-btn:hover {
  background: #d63031;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  text-align: center;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.modal-btn {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 1.5rem;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.pee-btn { background: #74b9ff; }
.poop-btn { background: #a29bfe; }
.both-btn { background: #fd79a8; }
.blowout-btn { background: #ff6348; }

.cancel-btn {
  background: #dfe6e9;
  color: #2d3436;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  width: 100%;
}

/* Edit Modal Styles */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.time-input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.time-input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-footer {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.save-btn {
  flex: 1;
  background: #00b894;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.save-btn:hover {
  background: #00a383;
}

.modal-btn.selected {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
  transform: scale(1.05);
}
</style>
