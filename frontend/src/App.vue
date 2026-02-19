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
  <v-app>
    <v-main class="bg-gradient">
      <v-container class="py-8" style="max-width: 600px;">
        <!-- Primary Actions -->
        <v-row class="mb-8">
          <v-col cols="12" sm="6">
            <v-card
              elevation="8"
              class="action-card pa-8"
              hover
              @click="showDiaperModal = true"
            >
              <v-card-text class="text-center pa-0">
                <div class="text-h1 mb-4">🚼</div>
                <div class="text-h5 font-weight-bold">Diaper</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6">
            <v-card
              elevation="8"
              class="action-card pa-8"
              hover
              @click="startFeeding"
            >
              <v-card-text class="text-center pa-0">
                <div class="text-h1 mb-4">🍼</div>
                <div class="text-h5 font-weight-bold">Feeding</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Diaper Modal -->
        <v-dialog v-model="showDiaperModal" max-width="400">
          <v-card>
            <v-card-title class="text-h5 text-center">Record Diaper</v-card-title>
            <v-card-text>
              <v-row dense>
                <v-col cols="6">
                  <v-btn
                    block
                    size="x-large"
                    class="pee-btn"
                    @click="recordDiaper('pee')"
                  >
                    💧 Pee
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    block
                    size="x-large"
                    class="poop-btn"
                    @click="recordDiaper('poop')"
                  >
                    💩 Poop
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    block
                    size="x-large"
                    class="both-btn"
                    @click="recordDiaper('both')"
                  >
                    🦆 Both
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    block
                    size="x-large"
                    class="blowout-btn"
                    @click="recordDiaper('blowout')"
                  >
                    💥 Blowout
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-btn block variant="text" @click="showDiaperModal = false">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Feeding Modal -->
        <v-dialog v-model="showFeedingModal" max-width="400">
          <v-card>
            <v-card-title class="text-h5 text-center">Feeding in Progress</v-card-title>
            <v-card-text>
              <p class="text-center text-body-1 mb-4" v-if="feedingStart">
                Started: {{ formatTime(feedingStart!.toISOString()) }}
              </p>
              <v-btn
                block
                size="large"
                class="end-btn"
                prepend-icon="mdi-check"
                @click="endFeeding"
              >
                End Feeding
              </v-btn>
            </v-card-text>
            <v-card-actions>
              <v-btn block variant="text" @click="cancelFeeding">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Recent Events -->
        <Recent 
          :diapers="diapers"
          :feedings="feedings"
          :loading="loading"
          @updated="loadData"
        />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.action-card {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
}

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

.end-btn {
  background: #00b894 !important;
  color: white !important;
}
</style>
