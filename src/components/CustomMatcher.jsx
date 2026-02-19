import { useState } from 'react'
import axios from 'axios'
import { Search, ExternalLink, CheckCircle, XCircle } from 'lucide-react'

export default function CustomMatcher() {
  const [formData, setFormData] = useState({
    age: 45,
    gender: 'male',
    conditions: 'Type 2 Diabetes, Hypertension',
    medications: 'Metformin, Lisinopril'
  })
  const [matches, setMatches] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await axios.post('/api/match-custom', {
        age: parseInt(formData.age),
        gender: formData.gender,
        conditions: formData.conditions.split(',').map(s => s.trim()).filter(s => s),
        medications: formData.medications.split(',').map(s => s.trim()).filter(s => s)
      })
      setMatches(response.data.matches)
    } catch (error) {
      console.error('Error:', error)
    }
    setLoading(false)
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600 bg-green-100'
    if (score >= 50) return 'text-yellow-600 bg-yellow-100'
    return 'text-orange-600 bg-orange-100'
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Custom Patient Matching</h2>
        <p className="mt-1 text-sm text-gray-500">
          Enter patient details to find matching clinical trials in real-time
        </p>
      </div>

      <div className="bg-white shadow rounded-lg">
        <form onSubmit={handleSubmit} className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Age
              </label>
              <input
                type="number"
                min="18"
                max="100"
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Gender
              </label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({...formData, gender: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Conditions (comma-separated)
              </label>
              <textarea
                rows="3"
                value={formData.conditions}
                onChange={(e) => setFormData({...formData, conditions: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Type 2 Diabetes, Hypertension"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Medications (comma-separated)
              </label>
              <textarea
                rows="3"
                value={formData.medications}
                onChange={(e) => setFormData({...formData, medications: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Metformin, Lisinopril"
              />
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Finding Matches...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Find Matching Trials
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {matches && matches.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">
            Found {matches.length} Matching Trials
          </h3>
          
          {matches.map((match, idx) => (
            <div key={match.nct_id} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        #{idx + 1}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(match.score)}`}>
                        Score: {match.score}/100
                      </span>
                    </div>
                    <h4 className="text-base font-medium text-gray-900">{match.title}</h4>
                    <p className="mt-1 text-sm text-gray-500">{match.condition}</p>
                    
                    <div className="mt-3">
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
                  
                  <div className="ml-4 text-right">
                    <p className="text-3xl font-bold text-gray-900">{match.score}</p>
                    <p className="text-xs text-gray-500">/ 100</p>
                  </div>
                </div>

                <div className="mt-4 border-t border-gray-200 pt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Match Reasons:</p>
                  <div className="space-y-1">
                    {match.reasons.map((reason, i) => (
                      <div key={i} className="flex items-start text-sm">
                        {reason.includes('✓') ? (
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                        )}
                        <span className={reason.includes('✓') ? 'text-gray-700' : 'text-gray-500'}>
                          {reason.replace('✓', '').replace('✗', '').trim()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {matches && matches.length === 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <p className="text-sm text-yellow-700">
            No matching trials found. Try adjusting the patient criteria.
          </p>
        </div>
      )}
    </div>
  )
}
