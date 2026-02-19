import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, Users, FileText, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react'
import Dashboard from './components/Dashboard'
import PatientList from './components/PatientList'
import PatientDetail from './components/PatientDetail'
import CustomMatcher from './components/CustomMatcher'
import Navbar from './components/Navbar'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [selectedPatient, setSelectedPatient] = useState(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handlePatientSelect = (patientId) => {
    setSelectedPatient(patientId)
    setCurrentPage('patient-detail')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {currentPage === 'dashboard' && <Dashboard stats={stats} />}
        {currentPage === 'patients' && <PatientList onSelectPatient={handlePatientSelect} />}
        {currentPage === 'patient-detail' && <PatientDetail patientId={selectedPatient} />}
        {currentPage === 'custom' && <CustomMatcher />}
      </main>
    </div>
  )
}

export default App
