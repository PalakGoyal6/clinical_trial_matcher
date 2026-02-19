import { Activity, Users, PlusCircle, BarChart3 } from 'lucide-react'

export default function Navbar({ currentPage, setCurrentPage }) {
  const navItems = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'patients', name: 'Patients', icon: Users },
    { id: 'custom', name: 'Custom Match', icon: PlusCircle },
  ]

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                Clinical Trial Matcher
              </span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    className={`${
                      currentPage === item.id
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
