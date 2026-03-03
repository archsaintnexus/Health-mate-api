import React, { createContext, useContext, useState, useEffect } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  token: string | null
  firstName: string | null
  setToken: (token: string | null) => void
  setFirstName: (name: string | null) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null)
  const [firstName, setFirstNameState] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('healthmate_token')
    const storedFirstName = localStorage.getItem('healthmate_firstName')
    if (storedToken) {
      setTokenState(storedToken)
      setFirstNameState(storedFirstName)
    }
    setIsLoading(false)
  }, [])

  const setToken = (newToken: string | null) => {
    setTokenState(newToken)
    if (newToken) {
      localStorage.setItem('healthmate_token', newToken)
    } else {
      localStorage.removeItem('healthmate_token')
    }
  }

  const setFirstName = (name: string | null) => {
    setFirstNameState(name)
    if (name) {
      localStorage.setItem('healthmate_firstName', name)
    } else {
      localStorage.removeItem('healthmate_firstName')
    }
  }

  const logout = () => {
    setToken(null)
    setFirstName(null)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen bg-dark">Loading...</div>
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        token,
        firstName,
        setToken,
        setFirstName,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
