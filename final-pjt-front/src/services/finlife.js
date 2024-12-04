// src/services/finlife.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/finlife'

export const getDepositProducts = async () => {
  const response = await axios.get(`${API_BASE_URL}/deposit-products/`)
  return response.data
}

export const getDepositProductOptions = async (finPrdtCd) => {
  const response = await axios.get(`${API_BASE_URL}/deposit-products-options/${finPrdtCd}/`)
  return response.data
}

export const getBankList = async () => {
  const response = await axios.get(`${API_BASE_URL}/getBankName/`)
  return response.data
}