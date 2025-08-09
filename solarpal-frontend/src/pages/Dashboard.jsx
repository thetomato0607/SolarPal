import { useEffect, useState } from 'react'
import axios from 'axios'
import SkyScene from "@/components/SkyScene";


function Dashboard({ setSubmitted }) {
  const [summary, setSummary] = useState(null)
  const [tip, setTip] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const user_id = 'testuser'

    const fetchData = async () => {
      try {
        const resSummary = await axios.get(`http://127.0.0.1:8000/summary?user_id=${user_id}`)
        const resTip = await axios.get(`http://127.0.0.1:8000/tips?user_id=${user_id}`)
        setSummary(resSummary.data)
        setTip(resTip.data.tip)
        setLoading(false)
      } catch (err) {
        console.error('Error loading dashboard:', err)
      }
    }

    fetchData()
  }, [])

  if (loading) return <div className="text-center mt-20 text-green-600">🌱 Loading your dashboard...</div>

  return (
  <div className="min-h-screen bg-green-50 flex flex-col">
    {/* 🌤️ Sky Scene at the top */}
    <SkyScene />

    {/* 🧾 Dashboard content below */}
    <div className="flex flex-1 items-center justify-center p-6">
      <div className="max-w-md w-full bg-white shadow-2xl rounded-2xl p-6 space-y-5 border border-green-200">
        {/* 🌞 Header */}
        <h2 className="text-3xl font-bold text-green-700 text-center">🌞 Your Solar Summary</h2>

        {/* 📊 Summary Card */}
        <div className="bg-green-100 rounded-lg p-4 shadow-inner space-y-2">
          <p className="text-sm text-gray-700"><strong>🔋 Today's Savings:</strong> £{summary.daily_saving_gbp.toFixed(2)}</p>
          <p className="text-sm text-gray-700"><strong>🌱 CO₂ Offset:</strong> {summary.co2_offset_kg} kg</p>
          <p className="text-sm text-gray-700"><strong>🔋 Battery Status:</strong> {summary.battery_status}</p>
          <p className="text-xs mt-1 text-green-800 italic">{summary.message}</p>
        </div>

        {/* 🌿 Tip Card */}
        <div className="bg-white border-l-4 border-green-400 p-3 text-sm text-green-900 shadow-sm">
          <strong>🌿 Tip of the Day:</strong><br />
          {tip}
        </div>

        {/* 🔁 Reset Button */}
        <div className="text-center pt-4">
          <button
            onClick={() => {
              localStorage.removeItem('solarpal_submitted')
              setSubmitted(false)
            }}
            className="text-sm text-red-500 underline hover:text-red-700"
          >
            🔁 Reset and start over
          </button>
        </div>
      </div>
    </div>
  </div>
  )
}
