import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { DashboardHeader } from '@/components/dashboard/DashboardHeader'
import { Calendar, Clock, Search, X } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Provider {
  id: number
  full_name: string
  specialty: string
  location: string
  bio: string | null
  avatar_url: string | null
  rating: number
  years_exp: number
  is_active: boolean
}

interface Slot {
  id: number
  provider_id: number
  start_time: string
  end_time: string
  is_booked: boolean
}

interface Appointment {
  id: number
  user_id: number
  provider_id: number
  slot_id: number
  reason: string | null
  status: string
  created_at: string
  provider: Provider
  slot: Slot
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

export default function AppointmentsPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [slots, setSlots] = useState<Slot[]>([])
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null)
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null)
  const [specialty, setSpecialty] = useState('')
  const [location, setLocation] = useState('')
  const [reason, setReason] = useState('')
  const [loadingProviders, setLoadingProviders] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [loadingBook, setLoadingBook] = useState(false)
  const [loadingAppointments, setLoadingAppointments] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [bookingSuccess, setBookingSuccess] = useState(false)

  useEffect(() => {
    fetchMyAppointments()
  }, [])

  const fetchMyAppointments = async () => {
    setLoadingAppointments(true)
    try {
      const data = await apiClient.get<Appointment[]>('/appointments/my')
      setAppointments(data)
    } catch {
      setAppointments([])
    } finally {
      setLoadingAppointments(false)
    }
  }

  const handleSearch = async () => {
    setLoadingProviders(true)
    setError(null)
    setSelectedProvider(null)
    setSlots([])
    setSelectedSlot(null)
    try {
      const params = new URLSearchParams()
      if (specialty) params.append('specialty', specialty)
      if (location) params.append('location', location)
      const query = params.toString() ? `?${params.toString()}` : ''
      const data = await apiClient.get<Provider[]>(`/appointments/providers${query}`)
      setProviders(data)
    } catch {
      setError('No providers found for your search.')
      setProviders([])
    } finally {
      setLoadingProviders(false)
    }
  }

  const handleSelectProvider = async (provider: Provider) => {
    setSelectedProvider(provider)
    setSelectedSlot(null)
    setLoadingSlots(true)
    setError(null)
    try {
      const data = await apiClient.get<Slot[]>(
        `/appointments/providers/${provider.id}/slots`
      )
      setSlots(data)
    } catch {
      setError('No available slots for this provider.')
      setSlots([])
    } finally {
      setLoadingSlots(false)
    }
  }

  const handleBook = async () => {
    if (!selectedProvider || !selectedSlot) return
    setLoadingBook(true)
    setError(null)
    try {
      await apiClient.post<Appointment>('/appointments/book', {
        provider_id: selectedProvider.id,
        slot_id: selectedSlot.id,
        reason: reason || null,
      })
      setBookingSuccess(true)
      setSelectedProvider(null)
      setSelectedSlot(null)
      setSlots([])
      setReason('')
      await fetchMyAppointments()
      setTimeout(() => setBookingSuccess(false), 4000)
    } catch {
      setError('This slot was just booked by someone else. Please select another.')
    } finally {
      setLoadingBook(false)
    }
  }

  const handleCancel = async (appointmentId: number) => {
    try {
      await apiClient.delete(`/appointments/my/${appointmentId}`)
      await fetchMyAppointments()
    } catch {
      setError('Could not cancel appointment.')
    }
  }

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleString('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  }

  return (
    <div className="min-h-screen bg-[#0a0f1e]">
      <Sidebar />
      <DashboardHeader />

      <main className="ml-64 mt-16 p-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          <motion.div variants={itemVariants}>
            <h1 className="text-4xl font-bold text-white mb-2">Book Appointment</h1>
            <p className="text-[#a1a1a1]">
              Schedule a consultation with our healthcare professionals
            </p>
          </motion.div>

          {bookingSuccess && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-lg bg-[#00d4aa]/10 border border-[#00d4aa]/30 text-[#00d4aa] font-medium"
            >
              Appointment booked successfully!
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 font-medium flex justify-between items-center"
            >
              {error}
              <button onClick={() => setError(null)}>
                <X size={16} />
              </button>
            </motion.div>
          )}

          {/* Search */}
          <motion.div variants={itemVariants} className="card">
            <h2 className="text-2xl font-bold text-white mb-6">Search Doctors</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">Specialty</label>
                <input
                  type="text"
                  value={specialty}
                  onChange={e => setSpecialty(e.target.value)}
                  placeholder="e.g. Cardiology"
                  className="input-field"
                />
              </div>
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={e => setLocation(e.target.value)}
                  placeholder="e.g. Lagos"
                  className="input-field"
                />
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSearch}
              disabled={loadingProviders}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              <Search size={16} />
              {loadingProviders ? 'Searching...' : 'Search Doctors'}
            </motion.button>
          </motion.div>

          {/* Provider Results */}
          {providers.length > 0 && (
            <motion.div variants={itemVariants}>
              <h2 className="text-2xl font-bold text-white mb-6">Available Doctors</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {providers.map(provider => (
                  <motion.div
                    key={provider.id}
                    variants={itemVariants}
                    whileHover={{ y: -4 }}
                    className={`card cursor-pointer transition-all ${
                      selectedProvider?.id === provider.id
                        ? 'border-[#00d4aa]'
                        : 'hover:border-[#00d4aa]/50'
                    }`}
                  >
                    {provider.avatar_url && (
                      <img
                        src={provider.avatar_url}
                        alt={provider.full_name}
                        className="w-full h-40 rounded-lg object-cover mb-4"
                      />
                    )}
                    <h3 className="text-xl font-bold text-white mb-1">{provider.full_name}</h3>
                    <p className="text-[#00d4aa] text-sm font-medium mb-1">{provider.specialty}</p>
                    <p className="text-[#a1a1a1] text-sm mb-3">{provider.location}</p>
                    <div className="flex items-center justify-between text-sm text-[#a1a1a1]">
                      <span>⭐ {provider.rating.toFixed(1)}</span>
                      <span>{provider.years_exp} yrs exp</span>
                    </div>
                    {provider.bio && (
                      <p className="text-[#a1a1a1] text-xs mt-3 line-clamp-2">{provider.bio}</p>
                    )}
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full btn-primary text-sm mt-4"
                      onClick={() => handleSelectProvider(provider)}
                    >
                      {selectedProvider?.id === provider.id ? 'Selected ✓' : 'View Slots'}
                    </motion.button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Slot Selection + Booking */}
          {selectedProvider && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-2xl font-bold text-white mb-2">
                Available Slots — {selectedProvider.full_name}
              </h2>
              <p className="text-[#a1a1a1] text-sm mb-6">Click a slot to select it</p>

              {loadingSlots ? (
                <p className="text-[#a1a1a1]">Loading slots...</p>
              ) : slots.length === 0 ? (
                <p className="text-[#a1a1a1]">No available slots for this provider.</p>
              ) : (
                <div className="flex flex-wrap gap-3 mb-6">
                  {slots.map(slot => (
                    <motion.button
                      key={slot.id}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setSelectedSlot(slot)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        selectedSlot?.id === slot.id
                          ? 'bg-[#00d4aa] text-[#0a0f1e]'
                          : 'bg-white/5 text-white hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Clock size={14} />
                        {formatTime(slot.start_time)}
                      </div>
                    </motion.button>
                  ))}
                </div>
              )}

              {selectedSlot && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4 border-t border-[#2d2d2d] pt-6"
                >
                  <p className="text-white text-sm font-medium">
                    Selected: <span className="text-[#00d4aa]">{formatTime(selectedSlot.start_time)}</span>
                  </p>
                  <div className="space-y-2">
                    <label className="text-white font-medium text-sm">
                      Reason for visit (optional)
                    </label>
                    <input
                      type="text"
                      value={reason}
                      onChange={e => setReason(e.target.value)}
                      placeholder="e.g. Annual checkup"
                      className="input-field"
                    />
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleBook}
                    disabled={loadingBook}
                    className="btn-primary disabled:opacity-50"
                  >
                    {loadingBook ? 'Booking...' : 'Confirm Booking'}
                  </motion.button>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* My Appointments */}
          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-white mb-6">My Appointments</h2>
            <div className="card space-y-4">
              {loadingAppointments ? (
                <p className="text-[#a1a1a1]">Loading appointments...</p>
              ) : appointments.length === 0 ? (
                <p className="text-[#a1a1a1]">No appointments yet.</p>
              ) : (
                appointments.map(apt => (
                  <motion.div
                    key={apt.id}
                    className="pb-4 border-b border-[#2d2d2d] last:border-0 last:pb-0 flex justify-between items-start"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <div className="flex-1">
                      <p className="text-white font-bold">
                        {apt.provider.full_name} — {apt.provider.specialty}
                      </p>
                      <p className="text-[#a1a1a1] text-sm mt-1">{apt.provider.location}</p>
                      <div className="flex gap-4 mt-2 text-[#a1a1a1] text-sm">
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {formatTime(apt.slot.start_time)}
                        </span>
                      </div>
                      {apt.reason && (
                        <p className="text-[#a1a1a1] text-xs mt-1">
                          Reason: {apt.reason}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${
                        apt.status === 'confirmed'
                          ? 'bg-[#00d4aa]/10 text-[#00d4aa]'
                          : apt.status === 'cancelled'
                          ? 'bg-red-500/10 text-red-400'
                          : 'bg-white/10 text-white'
                      }`}>
                        {apt.status}
                      </span>
                      {apt.status === 'confirmed' && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleCancel(apt.id)}
                          className="px-4 py-2 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-all text-sm whitespace-nowrap"
                        >
                          Cancel
                        </motion.button>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  )
}