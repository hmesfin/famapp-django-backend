# Frontend Lessons Learned 📚
*Ham Dog & TC's hard-won wisdom from the trenches*

## Form Styling Patterns 🎨

### ALWAYS Add Padding to Form Inputs
**Problem**: Tailwind CSS doesn't automatically add padding to form inputs, making them tiny and hard to use.

**Solution**: Always add `px-3 py-2` to all input, textarea, and select elements:
```vue
<!-- WRONG - Tiny input with no padding -->
<input class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600">

<!-- RIGHT - Properly padded input -->
<input class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 px-3 py-2">
```

**Applies to**:
- `<input>` elements (text, email, password, date, etc.)
- `<textarea>` elements
- `<select>` elements
- Custom input components

## VeeValidate 4 Form Patterns 🔧

### Edit Form Prepopulation Issues
**Problem**: Form fields not showing existing values when editing, even though data is being passed correctly.

**Solution Pattern**:
1. Use a reactive `formData` ref to hold form values
2. Use both `v-model` on Field components AND `:value` on inputs
3. Use `setValues()` instead of `resetForm()` for updating existing data
4. Watch only for modal opening, not closing

```vue
<!-- Template -->
<Field name="name" v-model="formData.name" v-slot="{ field, errors, value }">
  <input
    v-bind="field"
    :value="value"  <!-- Explicit value binding -->
    type="text"
    class="... px-3 py-2"  <!-- Don't forget padding! -->
  />
</Field>

<!-- Script -->
const formData = ref({
  name: '',
  // ... other fields
})

watch(() => props.show, (newValue, oldValue) => {
  if (newValue && !oldValue) {  // Only when opening
    if (props.editData) {
      formData.value = { ...props.editData }
      setValues(formData.value)  // Use setValues, not resetForm
    }
  }
})
```

### Modal Form Reset Timing
**Problem**: Validation errors flash briefly when closing modal because form resets trigger validation.

**Solution**: Delay form reset until after modal transition completes:
```vue
// Clean up form AFTER modal has fully closed
watch(() => props.show, (newValue) => {
  if (!newValue) {
    setTimeout(() => {
      resetForm()
      formData.value = { /* initial values */ }
    }, 300) // Match modal transition duration
  }
})
```

## Dark Mode Considerations 🌙

### Always Include Dark Mode Classes
**Problem**: Forms look broken in dark mode if you forget dark mode classes.

**Solution**: Always pair light and dark classes:
```vue
<!-- Input styling with dark mode support -->
class="... border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
```

## Component Communication Patterns 📡

### Emit Events vs Direct Store Actions
**Problem**: Confusion about when to emit events vs call store actions directly.

**Solution**:
- **Emit events** from child components for parent to handle
- **Call store actions** only in parent/view components
- This keeps components reusable and testable

```vue
<!-- Child Component (e.g., SprintList) -->
@click="$emit('delete', sprint)"  // Emit, don't delete directly

<!-- Parent Component (e.g., ProjectDetailView) -->
@delete="handleDeleteSprint"  // Parent handles the actual deletion
```

## API Integration Patterns 🔌

### Task List Serializer Missing Fields
**Problem**: List serializers often miss fields needed for display (like description).

**Solution**: Always check what fields the list serializer includes and add missing ones:
```python
# Django - Don't forget commonly needed fields in list serializers!
class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['public_id', 'title', 'description', ...]  # Include description!
```

### Fetching Full Details for Modal Views
**Problem**: List data doesn't have all fields needed for detail views.

**Solution**: Fetch full details when opening detail modals:
```typescript
async function handleTaskClick(task: Task) {
  // Fetch full details including nested objects
  const fullTask = await projectStore.fetchTask(task.public_id)
  selectedTask.value = fullTask
  showDetailModal.value = true
}
```

## Common Gotchas to Avoid 🚫

1. **Forgetting `px-3 py-2` on inputs** - Makes forms unusable
2. **Using `resetForm()` with values for editing** - Use `setValues()` instead
3. **Resetting form on modal close** - Causes validation flash
4. **Not including dark mode classes** - Breaks in dark mode
5. **Missing fields in list serializers** - Causes data not to display
6. **Direct store actions in child components** - Reduces reusability

## The Golden Rules 🏆

1. **Always test in both light and dark modes**
2. **Always add padding to form inputs**
3. **Always check serializer fields match frontend needs**
4. **Always emit events from child components**
5. **Always fetch full details for detail views**
6. **When Ham Dog corrects TC, document it!** 😄

---

*"Every bug is a lesson waiting to be learned!"* - Ham Dog & TC