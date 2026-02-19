import { useState, useEffect } from 'react'
import axios from 'axios'
import { ExternalLink, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export default function PatientDetail({ patientId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (patientId) {
      fetchPatient()
    }
  }, [patientId])

  const fetchPatient = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Fetching patient:', patientId)
      const response = await axios.get(`/api/patients/${patientId}`)
      console.log('Patient data received:', response.data)
      setData(response.data)
    } catch (err) {
      console.error('Error fetching patient:', err)
      console.error('Error response:', err.response?.data)
      setError(err.response?.data?.detail || 'Failed to load patient data')
    } finally {
      setLoading(false)
    }
  }

  // Safely parse list data
  const parseList = (value) => {
    if (!value) return []
    if (Array.isArray(value)) return value
    if (typeof value === 'string') {
      try {
        // Try parsing as JSON (handles both single and double quotes)
        return JSON.parse(value.replace(/'/g, '"'))
      } catch {
        // Fall back to comma-separated
        return value.split(',').map(s => s.trim()).filter(Boolean)
      }
    }
    return []
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600 bg-green-100'
    if (score >= 50) return 'text-yellow-600 bg-yellow-100'
    return 'text-orange-600 bg-orange-100'
  }

  const getScoreBadge = (score) => {
    if (score >= 70) return 'Excellent'
    if (score >= 50) return 'Good'
    return 'Fair'
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <p className="text-sm text-red-700">
              {error}
            </p>
            <button
              onClick={fetchPatient}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!data || !data.patient) {
    return (
      <div className="text-center p-12">
        <p className="text-gray-500">Patient not found</p>
      </div>
    )
  }

  const patient = data.patient
  const matches = data.matches || []
  const conditions = parseList(patient.conditions)
  const medications = parseList(patient.medications)

  return (
    <div className="space-y-6">
      {/* Patient Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Patient Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <p className="text-sm font-medium text-gray-500">Patient ID</p>
              <p className="mt-1 text-sm text-gray-900">{patient.id}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Age</p>
              <p className="mt-1 text-sm text-gray-900">{patient.age} years</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Gender</p>
              <p className="mt-1 text-sm text-gray-900 capitalize">{patient.gender}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-2">Conditions</p>
              {conditions.length > 0 ? (
                <div className="space-y-1">
                  {conditions.slice(0, 5).map((cond, i) => (
                    <div key={i} className="flex items-center text-sm text-gray-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-blue-600 mr-2 flex-shrink-0"></span>
                      <span>{cond}</span>
                    </div>
                  ))}
                  {conditions.length > 5 && (
                    <p className="text-xs text-gray-500 ml-3.5">
                      ... and {conditions.length - 5} more
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">No conditions recorded</p>
              )}
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-500 mb-2">Medications</p>
              {medications.length > 0 ? (
                <div className="space-y-1">
                  {medications.slice(0, 5).map((med, i) => (
                    <div key={i} className="flex items-center text-sm text-gray-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-600 mr-2 flex-shrink-0"></span>
                      <span>{med}</span>
                    </div>
                  ))}
                  {medications.length > 5 && (
                    <p className="text-xs text-gray-500 ml-3.5">
                      ... and {medications.length - 5} more
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">No medications recorded</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Matches */}
      <div>
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Matched Clinical Trials ({matches.length})
        </h3>
        
        {matches.length === 0 ? (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-sm text-yellow-700">
              No matching trials found for this patient.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match, idx) => (
              <div key={match.nct_id || idx} className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          #{idx + 1}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(match.score)}`}>
                          {getScoreBadge(match.score)}
                        </span>
                      </div>
                      <h4 className="text-base font-medium text-gray-900 mb-1">
                        {match.title}
                      </h4>
                      <p className="text-sm text-gray-500 mb-3">{match.condition}</p>
                      
                      <div className="flex items-center space-x-4">
                        <a
                          href={`https://clinicaltrials.gov/study/${match.nct_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                        >
                          {match.nct_id}
                          <ExternalLink className="ml-1 h-4 w-4" />
                        </a>
                      </div>
                    </div>
                    
                    <div className="ml-4 text-right flex-shrink-0">
                      <p className="text-sm font-medium text-gray-500">Match Score</p>
                      <p className="mt-1 text-3xl font-bold text-gray-900">{match.score}</p>
                      <p className="text-xs text-gray-500">out of 100</p>
                    </div>
                  </div>

                  {match.reasons && match.reasons.length > 0 && (
                    <div className="mt-4 border-t border-gray-200 pt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Match Reasons:</p>
                      <div className="space-y-1">
                        {match.reasons.map((reason, i) => {
                          const isPositive = reason.includes('✓')
                          const cleanReason = reason.replace('✓', '').replace('✗', '').trim()
                          
                          return (
                            <div key={i} className="flex items-start text-sm">
                              {isPositive ? (
                                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                              )}
                              <span className={isPositive ? 'text-gray-700' : 'text-gray-500'}>
                                {cleanReason}
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}