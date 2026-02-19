<template>
  <div class="date-input-container">
    <button
      class="date-input-button"
      @click="decrement"
      v-if="!disableCustom"
      :disabled="!canDecrement"
    >
      <v-icon class="text-primary">mdi-chevron-left</v-icon>
    </button>
    <div class="date-input-field-wrapper">
      <v-menu v-model="showCustomTop" location="bottom" v-if="!disableCustom">
        <template v-slot:activator="{ props: menuProps }">
          <div class="calendar-icon" v-bind="menuProps" @click="open = false">
            <v-icon>mdi-calendar</v-icon>
          </div>
        </template>
        <v-card>
          <v-date-picker
            v-model="customSelectedDate"
            multiple="range"
            hide-header
            @click.stop
            :max="maxString"
            :min="minString"
          />
          <v-card-actions>
            <v-spacer />
            <v-btn color="error" @click="showCustomTop = false" variant="tonal">
              Cancel
            </v-btn>
            <v-btn color="primary" @click="selectCustomDate" variant="tonal">
              OK
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
      <v-menu v-model="open" :close-on-content-click="false">
        <template v-slot:activator="{ props: menuProps }">
          <div class="date-input-field" v-bind="menuProps">
            <span class="date-text">{{ labelText }}</span>
            <v-icon class="text-content-low">
              {{ open ? 'mdi-menu-up' : 'mdi-menu-down' }}
            </v-icon>
          </div>
        </template>
        <v-list density="compact" select-strategy="independent">
          <v-list-item
            v-for="item in dateOptions"
            :key="item.title"
            @click="toggleItem(item)"
            :active="isSelected(item)"
            :title="item.title"
          />
          <v-menu v-model="showCustom" location="end" v-if="!disableCustom">
            <template v-slot:activator="{ props: menuProps }">
              <v-list-item
                v-bind="menuProps"
                :active="isCustomSelected"
                append-icon="mdi-calendar"
              >
                Custom
              </v-list-item>
            </template>
            <v-card>
              <v-date-picker
                v-model="customSelectedDate"
                multiple="range"
                hide-header
                @click.stop
                :max="maxString"
                :min="minString"
              />
              <v-card-actions>
                <v-spacer />
                <v-btn
                  color="error"
                  @click="showCustom = false"
                  variant="tonal"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="primary"
                  @click="selectCustomDate"
                  variant="tonal"
                >
                  OK
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-menu>
        </v-list>
      </v-menu>
    </div>
    <button
      class="date-input-button"
      @click="increment"
      v-if="!disableCustom"
      :disabled="!canIncrement"
    >
      <v-icon class="text-primary">mdi-chevron-right</v-icon>
    </button>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, toRefs, watch } from 'vue';
import dayjs from 'dayjs';
import localeData from 'dayjs/plugin/localeData';
import updateLocale from 'dayjs/plugin/updateLocale';
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter';
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore';

dayjs.extend(localeData);
dayjs.extend(updateLocale);
dayjs.extend(isSameOrBefore);
dayjs.extend(isSameOrAfter);

const startDate = defineModel<Date | string>('startDate');
const endDate = defineModel<Date | string>('endDate');

const props = defineProps({
  options: {
    type: Array,
  },
  customOptions: {
    type: Array,
    validator: (val: any) => {
      return (
        Array.isArray(val) &&
        val.every(
          (opt: any) =>
            typeof opt.title === 'string' &&
            typeof opt.key === 'string' &&
            Array.isArray(opt.value) &&
            opt.value.length === 2 &&
            opt.value.every((d: any) => typeof d === 'string'),
        )
      );
    },
    default: () => [],
  },
  max: {
    type: [String, Date],
  },
  min: {
    type: [String, Date],
  },
  defaultSelected: {
    type: String,
  },
  disableCustom: {
    type: Boolean,
    default: false,
  },
});
const { options, customOptions, max, min, defaultSelected, disableCustom } =
  toRefs(props);

const open = ref(false);
const showCustom = ref(false);
const showCustomTop = ref(false);
const selectedItem = ref<any>();
const selectedDateKey = defineModel<string>('selectedDateKey');
const customSelectedDate = ref<Date[] | null>(null);
const isCustomSelected = ref(false);

const maxString = computed(() => {
  if (!max?.value) return null;
  return dayjs(max.value).format('YYYY-MM-DD');
});

const minString = computed(() => {
  if (!min?.value) return null;
  return dayjs(min.value).format('YYYY-MM-DD');
});

interface DateOption {
  title: string;
  key: string;
  value: string[];
  weekRange?: boolean;
  monthRange?: boolean;
  isCustom?: boolean;
}

const dateOptions = computed<DateOption[]>(() => {
  const maxObj = max?.value ? dayjs(max.value) : dayjs().add(3, 'month');
  const minObj = min?.value ? dayjs(min.value) : dayjs('1900-01-01');
  const today = dayjs();
  const yesterday = dayjs().subtract(1, 'day');
  const tomorrow = dayjs().add(1, 'day');

  const all: DateOption[] = [...(customOptions.value || [])] as DateOption[];

  // Yesterday - show if max is yesterday or later AND min is yesterday or earlier
  if (
    (!options?.value || options.value.includes('yesterday')) &&
    maxObj.isSameOrAfter(yesterday, 'day') &&
    minObj.isSameOrBefore(yesterday, 'day')
  ) {
    all.push({
      title: 'Yesterday',
      key: 'yesterday',
      value: [yesterday.format('YYYY-MM-DD'), yesterday.format('YYYY-MM-DD')],
    });
  }

  // Today - show if max is today or later AND min is today or earlier
  if (
    (!options?.value || options.value.includes('today')) &&
    maxObj.isSameOrAfter(today, 'day') &&
    minObj.isSameOrBefore(today, 'day')
  ) {
    all.push({
      title: 'Today',
      key: 'today',
      value: [today.format('YYYY-MM-DD'), today.format('YYYY-MM-DD')],
    });
  }

  // Tomorrow - show if max is tomorrow or later AND min is tomorrow or earlier
  if (
    (!options?.value || options.value.includes('tomorrow')) &&
    maxObj.isSameOrAfter(tomorrow, 'day') &&
    minObj.isSameOrBefore(tomorrow, 'day')
  ) {
    all.push({
      title: 'Tomorrow',
      key: 'tomorrow',
      value: [tomorrow.format('YYYY-MM-DD'), tomorrow.format('YYYY-MM-DD')],
    });
  }

  // WTD - Week to Date, but end at max instead of today, start at min if min > weekStart
  if (!options?.value || options.value.includes('wtd')) {
    let weekStart = dayjs().startOf('week');
    if (minObj.isAfter(weekStart, 'day')) {
      weekStart = minObj;
    }
    const wtdEnd = maxObj.isBefore(today, 'day') ? maxObj : today;

    // Only show WTD if the week start is before or equal to max and after or equal to min
    if (
      weekStart.isSameOrBefore(maxObj, 'day') &&
      weekStart.isSameOrAfter(minObj, 'day')
    ) {
      all.push({
        title: 'WTD',
        key: 'wtd',
        weekRange: true,
        value: [weekStart.format('YYYY-MM-DD'), wtdEnd.format('YYYY-MM-DD')],
      });
    }
  }

  // MTD - Month to Date, but end at max instead of today, start at min if min > monthStart
  if (!options?.value || options.value.includes('mtd')) {
    let monthStart = dayjs().startOf('month');
    if (minObj.isAfter(monthStart, 'day')) {
      monthStart = minObj;
    }
    const mtdEnd = maxObj.isBefore(today, 'day') ? maxObj : today;

    // Only show MTD if the month start is before or equal to max and after or equal to min
    if (
      monthStart.isSameOrBefore(maxObj, 'day') &&
      monthStart.isSameOrAfter(minObj, 'day')
    ) {
      all.push({
        title: 'MTD',
        key: 'mtd',
        monthRange: true,
        value: [monthStart.format('YYYY-MM-DD'), mtdEnd.format('YYYY-MM-DD')],
      });
    }
  }

  // trailing 7 days
  if (!options?.value || options.value.includes('last7')) {
    const last7Start = today.subtract(6, 'day');
    if (
      last7Start.isSameOrBefore(maxObj, 'day') &&
      last7Start.isSameOrAfter(minObj, 'day')
    ) {
      all.push({
        title: 'Last 7 Days',
        key: 'last7',
        value: [last7Start.format('YYYY-MM-DD'), today.format('YYYY-MM-DD')],
      });
    }
  }

  // trailing 30 days
  if (!options?.value || options.value.includes('last30')) {
    const last30Start = today.subtract(29, 'day');
    if (
      last30Start.isSameOrBefore(maxObj, 'day') &&
      last30Start.isSameOrAfter(minObj, 'day')
    ) {
      all.push({
        title: 'Last 30 Days',
        key: 'last30',
        value: [last30Start.format('YYYY-MM-DD'), today.format('YYYY-MM-DD')],
      });
    }
  }

  return all;
});

function isSelected(item: any) {
  if (isCustomSelected.value) return false;
  return selectedItem.value?.key === item.key;
}

function toggleItem(item: any) {
  if (item.isCustom) {
    showCustom.value = !showCustom.value;
    return;
  }
  if (isSelected(item)) {
    open.value = false;
    return;
  }
  selectedItem.value = item;
  startDate.value = dayjs(item.value[0]).startOf('day').toDate();
  endDate.value = dayjs(item.value[1]).endOf('day').toDate();
  open.value = false;
  isCustomSelected.value = false;
  customSelectedDate.value = null;
  selectedDateKey.value = item.key;
}

watch(selectedDateKey, (newKey) => {
  const found = dateOptions.value.find((opt: any) => opt.key === newKey) as any;
  if (found) {
    selectedItem.value = found;
    startDate.value = dayjs(found.value[0]).startOf('day').toDate();
    endDate.value = dayjs(found.value[1]).endOf('day').toDate();
    isCustomSelected.value = false;
    customSelectedDate.value = null;
  }
});

function selectCustomDate() {
  if (!customSelectedDate.value) return;
  startDate.value = dayjs(customSelectedDate.value[0]).startOf('day').toDate();
  endDate.value = dayjs(
    customSelectedDate.value[customSelectedDate.value.length - 1],
  ).endOf('day').toDate();
  showCustom.value = false;
  showCustomTop.value = false;
  isCustomSelected.value = true;
}

const labelText = computed(() => {
  if (!selectedItem.value && !isCustomSelected.value) {
    return '';
  }
  let text = '';
  if (!isCustomSelected.value)
    text = selectedItem.value?.title ? `${selectedItem.value?.title} - ` : '';
  // const formattedStart = dayjs(startDate.value).format();
  // const formattedEnd = dayjs(endDate.value).format();
  const formattedStart = new Date(startDate.value as any).toLocaleDateString();
  const formattedEnd = new Date(endDate.value as any).toLocaleDateString();
  if (formattedStart === formattedEnd) {
    return (text += formattedStart);
  } else {
    text += `${formattedStart} - ${formattedEnd}`;
  }
  // return `${formattedStart} - ${formattedEnd}`;

  return text;
});

onMounted(() => {
  if (defaultSelected?.value) {
    selectedItem.value =
      dateOptions.value.find((opt: any) => opt.key === defaultSelected.value) ||
      dateOptions.value[0];
  } else if (startDate.value && endDate.value) {
    selectedItem.value =
      dateOptions.value.find(
        (opt: any) =>
          dayjs(opt.value[0]).isSame(startDate.value as any, 'day') &&
          dayjs(opt.value[1]).isSame(endDate.value as any, 'day'),
      ) || dateOptions.value[0];
  } else {
    if (!disableCustom.value) {
      isCustomSelected.value = true;
    } else {
      // If custom is disabled, select the first available option
      selectedItem.value = dateOptions.value[0];
    }
  }
  if (selectedItem.value) {
    startDate.value = dayjs(selectedItem.value.value[0]).startOf('day').toDate();
    endDate.value = dayjs(selectedItem.value.value[1]).endOf('day').toDate();
  }
});

function setCustomDate(start: any, end: any) {
  startDate.value = dayjs(start).startOf('day').toDate();
  endDate.value = dayjs(end).endOf('day').toDate();
  const arr: Date[] = [];
  arr.push(new Date(start));
  // push each date in between
  let current = dayjs(start).add(1, 'day');
  while (current.isBefore(dayjs(end), 'day')) {
    arr.push(current.toDate());
    current = current.add(1, 'day');
  }
  arr.push(new Date(end));
  customSelectedDate.value = arr;
}

function adjustDateRange(direction: number) {
  let newStart, newEnd;
  const operation = direction > 0 ? 'add' : 'subtract';
  const amount = Math.abs(direction);

  if (selectedItem.value?.monthRange) {
    newStart = dayjs(startDate.value as any)
      [operation](amount, 'month')
      .startOf('month');
    newEnd = dayjs(startDate.value as any)[operation](amount, 'month').endOf('month');
    startDate.value = newStart.startOf('day').toDate();
    endDate.value = newEnd.endOf('day').toDate();
    selectedItem.value = {
      monthRange: true,
      value: [newStart.format('YYYY-MM-DD'), newEnd.format('YYYY-MM-DD')],
    };
  } else if (selectedItem.value?.weekRange) {
    newStart = dayjs(startDate.value as any)
      [operation](amount, 'week')
      .startOf('week');
    newEnd = dayjs(startDate.value as any)[operation](amount, 'week').endOf('week');
    startDate.value = newStart.startOf('day').toDate();
    endDate.value = newEnd.endOf('day').toDate();
    selectedItem.value = {
      weekRange: true,
      value: [newStart.format('YYYY-MM-DD'), newEnd.format('YYYY-MM-DD')],
    };
  }
  // otherwise adjust by the same number of days as currently selected
  else {
    const currentStart = dayjs(startDate.value as any);
    const currentEnd = dayjs(endDate.value as any);
    const diffDays = currentEnd.diff(currentStart, 'day');
    const daysToMove = diffDays + 1;

    if (direction > 0) {
      newStart = currentStart.add(daysToMove, 'day');
      newEnd = currentEnd.add(daysToMove, 'day');
    } else {
      newStart = currentStart.subtract(daysToMove, 'day');
      newEnd = currentEnd.subtract(daysToMove, 'day');
    }

    startDate.value = newStart.startOf('day').toDate();
    endDate.value = newEnd.endOf('day').toDate();
    selectedItem.value = {
      value: [newStart.format('YYYY-MM-DD'), newEnd.format('YYYY-MM-DD')],
    };
  }
  isCustomSelected.value = true;
  if (newStart && newEnd) setCustomDate(newStart.toDate(), newEnd.toDate());
}

function decrement() {
  adjustDateRange(-1);
}

function increment() {
  adjustDateRange(1);
}

const canIncrement = computed(() => {
  if (!startDate.value || !endDate.value || !max?.value) return true;

  const maxObj = dayjs(max.value);
  let nextEnd;

  if (selectedItem.value?.monthRange) {
    nextEnd = dayjs(startDate.value as any).add(1, 'month').endOf('month');
  } else if (selectedItem.value?.weekRange) {
    nextEnd = dayjs(startDate.value as any).add(1, 'week').endOf('week');
  } else {
    const currentStart = dayjs(startDate.value as any);
    const currentEnd = dayjs(endDate.value as any);
    const diffDays = currentEnd.diff(currentStart, 'day');
    const daysToMove = diffDays + 1;
    nextEnd = currentEnd.add(daysToMove, 'day');
  }

  // Can increment if the next end date is not after the max date
  return nextEnd.isSameOrBefore(maxObj, 'day');
});

const canDecrement = computed(() => {
  if (!startDate.value || !endDate.value || !min?.value) return true;

  const minObj = dayjs(min.value);
  let prevStart;

  if (selectedItem.value?.monthRange) {
    prevStart = dayjs(startDate.value as any).subtract(1, 'month').startOf('month');
  } else if (selectedItem.value?.weekRange) {
    prevStart = dayjs(startDate.value as any).subtract(1, 'week').startOf('week');
  } else {
    const currentStart = dayjs(startDate.value as any);
    const currentEnd = dayjs(endDate.value as any);
    const diffDays = currentEnd.diff(currentStart, 'day');
    const daysToMove = diffDays + 1;
    prevStart = currentStart.subtract(daysToMove, 'day');
  }

  // Can decrement if the previous start date is not before the min date
  return prevStart.isSameOrAfter(minObj, 'day');
});
</script>
<style scoped lang="scss">
.date-input-container {
  display: flex;
  align-items: center;
  gap: 4px;
  --container-height: 40px;
}
.date-input-button {
  border: 1px solid rgb(var(--v-theme-border-low));
  min-height: var(--container-height);
  padding: 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  &:hover:not(:disabled) {
    background: rgb(var(--v-theme-surface-alt-medium));
  }
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    .v-icon {
      color: rgb(var(--v-theme-on-surface-disabled)) !important;
    }
  }
}
.date-input-field-wrapper {
  min-height: var(--container-height);
  border: 1px solid rgb(var(--v-theme-border-low));
  display: flex;
  align-items: center;
  border-radius: 4px;
  user-select: none;
  flex: 1;
  min-width: 0;
  &:hover {
    border-color: rgb(var(--v-theme-border-medium));
  }
}
.date-input-field {
  padding: 8px 12px;
  color: rgb(var(--v-theme-content-medium));
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.date-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.calendar-icon {
  background: rgb(var(--v-theme-surface-alt-medium));
  min-height: var(--container-height);
  height: 100%;
  display: flex;
  align-items: center;
  padding: 8px;
  border-right: 1px solid rgb(var(--v-theme-border-low));
}
.text-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
}
</style>