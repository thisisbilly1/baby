<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { createDiaper, createFeeding, getDiapers, getFeedings, type Diaper, type Feeding } from './api';
import Recent from './components/Recent.vue';
import { formatTime } from './helpers/time';

const diapers = ref<Diaper[]>([]);
const feedings = ref<Feeding[]>([]);
const loading = ref(false);
const feedingStart = ref<Date | null>(null);
const showDiaperModal = ref(false);
const showFeedingModal = ref(false);

const FEEDING_STORAGE_KEY = 'baby-tracker-feeding-in-progress';

// Load data
async function loadData() {
  loading.value = true;
  try {
    [diapers.value, feedings.value] = await Promise.all([
      getDiapers(),
      getFeedings()
    ]);
  } catch (error) {
    console.error('Failed to load data:', error);
    alert('Failed to load data. Make sure the server is running.');
  } finally {
    loading.value = false;
  }
}

// Load in-progress feeding from localStorage
function loadInProgressFeeding() {
  const saved = localStorage.getItem(FEEDING_STORAGE_KEY);
  if (saved) {
    feedingStart.value = new Date(saved);
    showFeedingModal.value = true;
  }
}

// Diaper actions
async function recordDiaper(type: 'pee' | 'poop' | 'both' | 'blowout') {
  try {
    await createDiaper(type);
    await loadData();
    showDiaperModal.value = false;
  } catch (error) {
    console.error('Failed to record diaper:', error);
    alert('Failed to record diaper');
  }
}

// Feeding actions
function startFeeding() {
  feedingStart.value = new Date();
  localStorage.setItem(FEEDING_STORAGE_KEY, feedingStart.value.toISOString());
  showFeedingModal.value = true;
}

async function endFeeding() {
  if (!feedingStart.value) return;
  
  try {
    const endTime = new Date();
    await createFeeding(
      feedingStart.value.toISOString(),
      endTime.toISOString()
    );
    feedingStart.value = null;
    localStorage.removeItem(FEEDING_STORAGE_KEY);
    showFeedingModal.value = false;
    await loadData();
  } catch (error) {
    console.error('Failed to record feeding:', error);
    alert('Failed to record feeding');
  }
}

function cancelFeeding() {
  feedingStart.value = null;
  localStorage.removeItem(FEEDING_STORAGE_KEY);
  showFeedingModal.value = false;
}

onMounted(() => {
  loadInProgressFeeding();
  loadData();
});
</script>

<template>
  <div class="app">
    <main class="container">
      <!-- Primary Actions -->
      <div class="actions">
        <button 
          class="action-btn diaper-btn"
          @click="showDiaperModal = true"
        >
          <span class="icon">🚼</span>
          <span class="label">Diaper</span>
        </button>

        <button 
          class="action-btn feeding-btn"
          @click="startFeeding"
        >
          <span class="icon">🍼</span>
          <span class="label">Feeding</span>
        </button>
      </div>

      <!-- Diaper Modal -->
      <div v-if="showDiaperModal" class="modal-overlay" @click="showDiaperModal = false">
        <div class="modal" @click.stop>
          <h2>Record Diaper</h2>
          <div class="modal-actions">
            <button class="modal-btn pee-btn" @click="recordDiaper('pee')">
              💧 Pee
            </button>
            <button class="modal-btn poop-btn" @click="recordDiaper('poop')">
              💩 Poop
            </button>
            <button class="modal-btn both-btn" @click="recordDiaper('both')">
              🦆 Both
            </button>
            <button class="modal-btn blowout-btn" @click="recordDiaper('blowout')">
              💥 Blowout
            </button>
          </div>
          <button class="cancel-btn" @click="showDiaperModal = false">Cancel</button>
        </div>
      </div>

      <!-- Feeding Modal -->
      <div v-if="showFeedingModal" class="modal-overlay" @click="cancelFeeding">
        <div class="modal" @click.stop>
          <h2>Feeding in Progress</h2>
          <p class="feeding-time">Started: {{ formatTime(feedingStart!.toISOString()) }}</p>
          <div class="modal-actions">
            <button class="modal-btn end-btn" @click="endFeeding">
              ✓ End Feeding
            </button>
          </div>
          <button class="cancel-btn" @click="cancelFeeding">Cancel</button>
        </div>
      </div>

      <!-- Recent Events -->
      <Recent 
        :diapers="diapers"
        :feedings="feedings"
        :loading="loading"
        @updated="loadData"
      />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 2rem;
}

header {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Primary Action Buttons */
.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 3rem;
}

.action-btn {
  background: white;
  border: none;
  border-radius: 1rem;
  padding: 3rem 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.action-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.action-btn:active {
  transform: translateY(-2px);
}

.action-btn .icon {
  font-size: 4rem;
}

.action-btn .label {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.diaper-btn:hover {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
}

.feeding-btn:hover {
  background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
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
.end-btn { background: #00b894; }

.cancel-btn {
  background: #dfe6e9;
  color: #2d3436;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  width: 100%;
}

.feeding-time {
  text-align: center;
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 1.5rem;
}

@media (max-width: 640px) {
  .actions {
    grid-template-columns: 1fr;
  }
  
  .action-btn .icon {
    font-size: 3rem;
  }
  
  .action-btn .label {
    font-size: 1.25rem;
  }
}
</style>
