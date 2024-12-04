import { defineStore } from 'pinia'
import axios from 'axios'

export const useChatbotStore = defineStore('chatbot', {
  state: () => ({
    messages: []
  }),
  actions: {
    addMessage(message) {
      this.messages.push(message)
    },
    async sendMessageToAPI(userInput) {
      console.log("Sending message to API:", userInput, this.messages);
      try {
        const response = await axios.post('http://localhost:8000/chatbot/chat/', {
          message: userInput,
          messages: this.messages
        })
        console.log("API response:", response.data);
        return response.data.response
      } catch (error) {
        console.error(error)
        return '오류가 발생했습니다. 다시 시도해주세요.'
      }
    }
  }
})
