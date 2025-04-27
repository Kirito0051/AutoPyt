<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
    <h1 class="text-3xl font-bold mb-8 text-gray-800">CSV File Processor</h1>

    <!-- Drop Zone -->
    <div @drop.prevent="handleDrop" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" :class="[
      'border-2 border-dashed rounded-lg p-8 mb-6 w-full max-w-md text-center transition-all',
      dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300',
      files.length ? 'border-green-500 bg-green-50' : ''
    ]">
      <div class="flex flex-col items-center space-y-4">
        <i class="fas fa-cloud-upload-alt text-4xl text-gray-400"></i>
        <p class="text-gray-600">
          Drag & drop your CSV files here or
          <label class="text-blue-500 hover:text-blue-600 cursor-pointer">
            <input type="file" accept=".csv" @change="handleFileChange" multiple class="hidden"
              aria-label="Select CSV files" />
            browse
          </label>
        </p>
        <p class="text-sm text-gray-500">Supports multiple CSV files</p>
      </div>
    </div>

    <!-- Selected Files List -->
    <div v-if="files.length" class="w-full max-w-md mb-6">
      <h2 class="text-lg font-semibold mb-3">Selected Files:</h2>
      <ul class="space-y-2">
        <li v-for="(file, index) in files" :key="index"
          class="flex items-center justify-between bg-white p-3 rounded-lg shadow-sm">
          <span class="truncate max-w-[200px]">{{ file.name }}</span>
          <button @click="removeFile(index)" class="text-red-500 hover:text-red-600" aria-label="Remove file">
            <i class="fas fa-times"></i>
          </button>
        </li>
      </ul>
    </div>

    <!-- Upload Button -->
    <button @click="uploadFiles" :disabled="!files.length || isUploading"
      class="flex items-center space-x-2 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      aria-label="Upload and process files">
      <i class="fas fa-spinner fa-spin" v-if="isUploading"></i>
      <span>{{ isUploading ? 'Processing...' : 'Upload and Process' }}</span>
    </button>

    <!-- Processing Results -->
    <div v-if="downloadLinks.length" class="mt-8 w-full max-w-md">
      <h2 class="text-lg font-semibold mb-4">Processed Files:</h2>
      <ul class="space-y-3">
        <li v-for="(link, index) in downloadLinks" :key="index"
          class="bg-white p-4 rounded-lg shadow-sm border border-green-200">
          <a :href="link" class="flex items-center justify-between text-green-600 hover:text-green-700" download
            aria-label="Download processed file">
            <span class="font-medium">Processed File {{ index + 1 }}</span>
            <i class="fas fa-download"></i>
          </a>
        </li>
      </ul>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
      role="alert">
      <span class="block sm:inline">{{ error }}</span>
      <button @click="error = null" class="ml-4" aria-label="Close error alert">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const files = ref([])
const downloadLinks = ref([])
const dragOver = ref(false)
const isUploading = ref(false)
const error = ref(null)

// Handle file drop
function handleDrop(event) {
  dragOver.value = false
  const droppedFiles = Array.from(event.dataTransfer.files).filter(file =>
    file.name.toLowerCase().endsWith('.csv')
  )
  // Use Set to prevent duplicate files
  const newFiles = new Set([...files.value, ...droppedFiles])
  files.value = Array.from(newFiles)
}

// Handle file input change
function handleFileChange(event) {
  const newFiles = Array.from(event.target.files)
  const newFileSet = new Set([...files.value, ...newFiles])
  files.value = Array.from(newFileSet)
}

// Remove a file from the list
function removeFile(index) {
  files.value = files.value.filter((_, i) => i !== index)
}

// Upload files
async function uploadFiles() {
  if (files.value.length === 0) {
    error.value = 'Please select files first'
    return
  }

  isUploading.value = true
  error.value = null
  const formData = new FormData()
  files.value.forEach(file => formData.append('files', file))

  try {
    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      downloadLinks.value.push(url)
      files.value = [] // Clear files after successful upload
    } else {
      throw new Error('Upload failed')
    }
  } catch (err) {
    error.value = 'An error occurred while uploading the files.'
    console.error('Upload failed:', err)
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
