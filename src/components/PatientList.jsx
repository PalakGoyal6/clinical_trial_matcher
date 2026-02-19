import { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, User } from 'lucide-react'

export default function PatientList({ onSelectPatient }) {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchPatients()
  }, [])

  const fetchPatients = async () => {
    try {
      const response = await axios.get('/api/patients')
      setPatients(response.data.patients)
      setLoading(false)
    } catch (error) {
      console.error('Error:', error)
      setLoading(false)
    }
  }

  const filteredPatients = patients.filter(p => 
    p.id.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return <div className="flex justify-center p-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Patients</h2>
        <p className="mt-1 text-sm text-gray-500">Select a patient to view matches</p>
      </div>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search patients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredPatients.map((patient) => (
            <li key={patient.id}>
              <button
                onClick={() => onSelectPatient(patient.id)}
                className="w-full px-4 py-4 hover:bg-gray-50 flex items-center text-left"
              >
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-blue-600">{patient.id}</p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {patient.age} years
                      </p>
                      <p className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {patient.gender}
                      </p>
                    </div>
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
