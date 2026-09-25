import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../pages/api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('ct_token'))
  const [loading, setLoading] = useState(true)

  // Restore login session when the application starts
  useEffect(() => {
    let mounted = true

    const restoreSession = async () => {
      const savedToken = localStorage.getItem('ct_token')

      if (!savedToken) {
        if (mounted) {
          setUser(null)
          setLoading(false)
        }
        return
      }

      try {
        const response = await api.get('/auth/me')

        if (mounted) {
          setUser(response.data)
          setToken(savedToken)
        }
      } catch (error) {
        console.error('Session restore failed:', error)

        localStorage.removeItem('ct_token')

        if (mounted) {
          setToken(null)
          setUser(null)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    restoreSession()

    return () => {
      mounted = false
    }
  }, [])

  // Login
  const login = useCallback(async (email, password) => {
    const form = new URLSearchParams({
      username: email,
      password: password,
    })

    const response = await api.post('/auth/login', form, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    const { access_token, ...userData } = response.data

    // Save JWT
    localStorage.setItem('ct_token', access_token)

    // Update React authentication state
    setToken(access_token)
    setUser(userData)

    return response.data
  }, [])

  // Register
  const register = useCallback(async (email, fullName, password) => {
    const response = await api.post('/auth/register', {
      email,
      full_name: fullName,
      password,
    })

    const { access_token, ...userData } = response.data

    // Save JWT
    localStorage.setItem('ct_token', access_token)

    // Update React authentication state
    setToken(access_token)
    setUser(userData)

    return response.data
  }, [])

  // Logout
  const logout = useCallback(() => {
    localStorage.removeItem('ct_token')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}