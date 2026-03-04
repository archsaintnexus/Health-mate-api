import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import { authApi, LoginRequest } from '@/lib/api'
import { useAuth } from '@/lib/auth-context'
import { Eye, EyeOff, Loader } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setToken, setFirstName } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>()

 const onSubmit = async (data: LoginRequest) => {
  setIsSubmitting(true)
  try {
    const response = await authApi.login(data)
    setToken(response.token)
    
    // Fetch real user data after login
    const profile = await authApi.getProfile()
    setFirstName(profile.first_name)
    
    toast.success('Login successful!')
    navigate('/dashboard')
  } catch (error) {
    toast.error('Invalid email or password')
    console.error(error)
  } finally {
    setIsSubmitting(false)
  }
}
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  }

  return (
    <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <motion.div variants={itemVariants} className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-[#a1a1a1]">Sign in to your Health Mate account</p>
          </motion.div>

          <motion.form
            variants={containerVariants}
            className="space-y-4"
            onSubmit={handleSubmit(onSubmit)}
          >
            <motion.div variants={itemVariants} className="space-y-2">
              <label className="block text-sm font-medium text-white">Email</label>
              <input
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: 'Please enter a valid email',
                  },
                })}
                type="email"
                className="input-field"
                placeholder="john@example.com"
              />
              {errors.email && <p className="text-red-400 text-sm">{errors.email.message}</p>}
            </motion.div>

            <motion.div variants={itemVariants} className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="block text-sm font-medium text-white">Password</label>
                <a href="#" className="text-sm text-[#00d4aa] hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <input
                  {...register('password', { required: 'Password is required' })}
                  type={showPassword ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a1a1a1] hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-400 text-sm">{errors.password.message}</p>
              )}
            </motion.div>

            <motion.div variants={itemVariants} className="flex items-center gap-2">
              <input type="checkbox" id="remember" className="w-4 h-4 cursor-pointer" />
              <label htmlFor="remember" className="text-sm text-[#a1a1a1] cursor-pointer">
                Remember me
              </label>
            </motion.div>

            <motion.button
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isSubmitting}
              className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </motion.button>
          </motion.form>

          <motion.p variants={itemVariants} className="text-center text-[#a1a1a1] text-sm">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="text-[#00d4aa] hover:underline font-medium">
              Create One
            </Link>
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}
