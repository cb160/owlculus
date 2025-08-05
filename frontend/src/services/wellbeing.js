import api from './api'

export const wellbeingService = {
  /**
   * Get wellbeing records with optional filtering
   */
  async getWellbeingRecords(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.case_id) queryParams.append('case_id', params.case_id)
    if (params.current_status) queryParams.append('current_status', params.current_status)
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)

    const response = await api.get(`/api/wellbeing/records?${queryParams.toString()}`)
    return response.data
  },

  /**
   * Get a wellbeing record with full details including client entity and treatment actions
   */
  async getWellbeingRecordDetails(recordId) {
    const response = await api.get(`/api/wellbeing/records/${recordId}`)
    return response.data
  },

  /**
   * Create a new wellbeing record
   */
  async createWellbeingRecord(wellbeingRecord) {
    const response = await api.post('/api/wellbeing/records', wellbeingRecord)
    return response.data
  },

  /**
   * Update a wellbeing record
   */
  async updateWellbeingRecord(recordId, wellbeingUpdate) {
    const response = await api.put(`/api/wellbeing/records/${recordId}`, wellbeingUpdate)
    return response.data
  },

  /**
   * Delete a wellbeing record
   */
  async deleteWellbeingRecord(recordId) {
    const response = await api.delete(`/api/wellbeing/records/${recordId}`)
    return response.data
  },

  /**
   * Create a treatment action (task) for a wellbeing record
   */
  async createTreatmentAction(recordId, taskCreate) {
    const response = await api.post(`/api/wellbeing/records/${recordId}/treatment-actions`, taskCreate)
    return response.data
  },

  /**
   * Get all client entities for a case
   */
  async getCaseClientEntities(caseId) {
    const response = await api.get(`/api/wellbeing/cases/${caseId}/client-entities`)
    return response.data
  }
}