import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  email: string
}

interface AuthContextType {
  isAuthenticated: boolean
  user: User | null
  setAuth: (auth: { isAuthenticated: boolean; user: User | null }) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    // 로컬 스토리지에서 인증 정보 확인
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const userData = JSON.parse(userStr)
        setIsAuthenticated(true)
        setUser(userData)
      } catch (error) {
        // 유효하지 않은 데이터면 로그아웃
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }, [])

  const setAuth = ({ isAuthenticated, user }: { isAuthenticated: boolean; user: User | null }) => {
    setIsAuthenticated(isAuthenticated)
    setUser(user)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, setAuth, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}




