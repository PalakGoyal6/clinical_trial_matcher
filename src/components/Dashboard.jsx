import { Users, FileText, CheckCircle, TrendingUp, Clock, Target } from 'lucide-react'

export default function Dashboard({ stats }) {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      name: 'Total Patients',
      value: stats.total_patients,
      icon: Users,
      color: 'bg-blue-500',
      change: null
    },
    {
      name: 'Active Trials',
      value: stats.total_trials,
      icon: FileText,
      color: 'bg-green-500',
      change: null
    },
    {
      name: 'Total Matches',
      value: stats.total_matches?.toLocaleString() || '0',
      icon: CheckCircle,
      color: 'bg-purple-500',
      change: null
    },
    {
      name: 'Avg Matches/Patient',
      value: stats.avg_matches_per_patient || 0,
      icon: TrendingUp,
      color: 'bg-yellow-500',
      change: null
    },
  ]

  const performanceCards = [
    {
      name: 'Match Time',
      value: `${stats.avg_time_seconds}s`,
      description: 'per patient',
      icon: Clock,
      color: 'text-blue-600'
    },
    {
      name: 'Speedup',
      value: `${stats.speedup?.toLocaleString()}×`,
      description: 'vs manual (30 min)',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      name: 'Accuracy',
      value: `${stats.accuracy}%`,
      description: 'strict validation',
      icon: Target,
      color: 'text-purple-600'
    },
    {
      name: 'Coverage',
      value: `${stats.coverage}%`,
      description: 'patients matched',
      icon: CheckCircle,
      color: 'text-yellow-600'
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">System Overview</h2>
        <p className="mt-1 text-sm text-gray-500">
          NLP-powered clinical trial matching system
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.name}
              className="relative bg-white pt-5 px-4 pb-12 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden"
            >
              <dt>
                <div className={`absolute ${item.color} rounded-md p-3`}>
                  <Icon className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <p className="ml-16 text-sm font-medium text-gray-500 truncate">
                  {item.name}
                </p>
              </dt>
              <dd className="ml-16 pb-6 flex items-baseline sm:pb-7">
                <p className="text-2xl font-semibold text-gray-900">
                  {item.value}
                </p>
              </dd>
            </div>
          )
        })}
      </div>

      {/* Performance Benchmarks */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Performance Benchmarks
          </h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {performanceCards.map((item) => {
              const Icon = item.icon
              return (
                <div key={item.name} className="border-l-4 border-gray-200 pl-4">
                  <div className="flex items-center">
                    <Icon className={`h-5 w-5 ${item.color} mr-2`} />
                    <p className="text-sm font-medium text-gray-500">{item.name}</p>
                  </div>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{item.value}</p>
                  <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Technology Stack
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Data Sources</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>ClinicalTrials.gov API (real trial data)</li>
                <li>Synthetic patient generator</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">NLP & Matching</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>spaCy for medical entity extraction</li>
                <li>Weighted multi-criteria scoring</li>
                <li>Keyword overlap + semantic similarity</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Matching Criteria */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Matching Criteria
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-blue-500 text-white font-bold">
                  20
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Age Range</p>
                <p className="text-sm text-gray-500">Patient age within trial range</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-green-500 text-white font-bold">
                  10
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Gender</p>
                <p className="text-sm text-gray-500">Exact match or trial accepts all</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-purple-500 text-white font-bold">
                  50
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Keyword Overlap</p>
                <p className="text-sm text-gray-500">Medical condition keywords match</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-yellow-500 text-white font-bold">
                  20
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Condition Similarity</p>
                <p className="text-sm text-gray-500">Primary condition semantic match</p>
              </div>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            <span className="font-semibold">Total Score:</span> 0-100 points (higher = better match)
          </p>
        </div>
      </div>
    </div>
  )
}
