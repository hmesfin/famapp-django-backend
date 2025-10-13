/**
 * VeeValidate configuration and custom rules
 * Ham Dog & TC's production-ready validation setup
 */
import { configure, defineRule } from 'vee-validate'
import { required, min, max, email, confirmed } from '@vee-validate/rules'

// Import all the rules you need
defineRule('required', required)
defineRule('min', min)
defineRule('max', max)
defineRule('email', email)
defineRule('confirmed', confirmed)

// Custom rules with personality (because we can't give up ALL our quirky messages!)
defineRule('project_name', (value: string) => {
  if (!value || !value.trim()) {
    return '🤷 A project with no name? That\'s like a ship without a sail! Give it something memorable!'
  }
  if (value.length < 3) {
    return '✏️ Come on, you can do better than that! At least 3 characters, please!'
  }
  if (value.length > 255) {
    return '📏 Whoa there! Project names should be under 255 characters. We\'re not writing novels here!'
  }
  return true
})

defineRule('project_description', (value: string) => {
  if (!value || !value.trim()) {
    return '📝 What\'s this project about? Don\'t be shy, tell us the story!'
  }
  if (value.length < 10) {
    return '🎭 That\'s a bit too mysterious! Give us at least 10 characters to work with!'
  }
  if (value.length > 2000) {
    return '📚 Epic story, but let\'s keep descriptions under 2000 characters!'
  }
  return true
})

defineRule('task_title', (value: string) => {
  if (!value || !value.trim()) {
    return '📋 Every great task needs a title! What are we doing here?'
  }
  if (value.length < 3) {
    return '🎯 A bit more descriptive please - at least 3 characters!'
  }
  if (value.length > 255) {
    return '📏 Keep task titles under 255 characters for everyone\'s sanity!'
  }
  return true
})

defineRule('date_range', (endDate: string, [startDate]: [string]) => {
  if (!endDate || !startDate) return true
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  
  if (start > end) {
    return '🤔 Unless you have a time machine, projects can\'t end before they start! Move that end date forward, friend!'
  }
  return true
})

defineRule('active_project_start', (startDate: string, [status]: [string]) => {
  if (status !== 'active' || !startDate) return true
  
  const date = new Date(startDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (date < today) {
    return '⏰ Whoa there, time traveler! Active projects can\'t start yesterday. Either move that date forward or switch to "Planning" status while you build your DeLorean!'
  }
  return true
})

// Configure VeeValidate
configure({
  generateMessage: (ctx) => {
    // Fallback messages for built-in rules
    const messages: Record<string, string> = {
      required: `${ctx.field} is required`,
      min: `${ctx.field} must be at least ${ctx.rule?.params?.[0]} characters`,
      max: `${ctx.field} must be at most ${ctx.rule?.params?.[0]} characters`,
      email: 'Please enter a valid email address'
    }
    
    return messages[ctx.rule?.name as string] || `${ctx.field} is not valid`
  }
})

// Export validation schemas for easy reuse
export const projectValidationSchema = {
  name: 'required|project_name',
  description: 'required|project_description', 
  status: 'required',
  start_date: 'required',
  end_date: 'date_range:@start_date'
}

export const taskValidationSchema = {
  title: 'required|task_title',
  description: 'max:2000',
  status: 'required',
  priority: 'required',
  story_points: 'min:0',
  due_date: ''
}