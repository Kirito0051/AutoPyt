<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
    <h1 class="text-2xl font-bold mb-6">Upload CSV Files</h1>

    <!-- File Input: Multiple Files -->
    <input type="file" accept=".csv" @change="handleFileChange" class="mb-4" multiple />

    <!-- Upload Button -->
    <button @click="uploadFiles" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      :disabled="!files.length">
      Upload and Process
    </button>

    <!-- Download Processed Files Links -->
    <div v-if="downloadLinks.length" class="mt-6 space-y-4">
      <p class="text-lg font-semibold">Processed Files:</p>
      <ul>
        <li v-for="(link, index) in downloadLinks" :key="index" class="text-green-600">
          <a :href="link" class="font-semibold" download>
            Download Processed File {{ index + 1 }}
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const files = ref([]) // Array to hold selected files
const downloadLinks = ref([]) // Array to hold download links for processed files

// Handle file selection
function handleFileChange(event) {
  files.value = Array.from(event.target.files) // Convert FileList to Array
}

// Upload files to the backend
async function uploadFiles() {
  if (files.value.length === 0) {
    alert('Please select files first')
    return
  }

  const formData = new FormData()
  files.value.forEach(file => formData.append('files', file))

  try {
    const response = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData
    })

    // Handle the response with multiple processed files
    if (response.ok) {
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      downloadLinks.value.push(url) // Add the processed file download URL
    } else {
      alert('Error uploading files')
    }
  } catch (error) {
    console.error('Upload failed:', error)
    alert('An error occurred while uploading the files.')
  }
}
</script>

<style scoped>
/* Optional styling for the component */
</style>
