import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import { authApi, SignupRequest } from '@/lib/api'
import { useAuth } from '@/lib/auth-context'
import { Eye, EyeOff, Loader } from 'lucide-react'

export default function SignupPage() {
  const navigate = useNavigate()
  const { setToken, setFirstName } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupRequest & { confirmPassword: string }>()

  const password = watch('password')

  const calculatePasswordStrength = (pwd: string) => {
    let strength = 0
    if (!pwd) return 0
    if (pwd.length >= 8) strength += 25
    if (pwd.length >= 12) strength += 25
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength += 25
    if (/\d/.test(pwd)) strength += 12
    if (/[^a-zA-Z\d]/.test(pwd)) strength += 13
    return Math.min(strength, 100)
  }

  const onPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordStrength(calculatePasswordStrength(e.target.value))
  }

  const onSubmit = async (data: SignupRequest & { confirmPassword: string }) => {
    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await authApi.signup({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        password: data.password,
      })

      setFirstName(response.first_name)
      toast.success('Account created successfully!')
      
      // In a real scenario, you'd get a token after signup
      // For now, redirect to login
      navigate('/login', { state: { email: data.email } })
    } catch (error) {
      toast.error('Failed to create account. Please try again.')
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
            <h1 className="text-4xl font-bold text-white mb-2">Create Account</h1>
            <p className="text-[#a1a1a1]">Join thousands of patients and healthcare providers</p>
          </motion.div>

          <motion.form
            variants={containerVariants}
            className="space-y-4"
            onSubmit={handleSubmit(onSubmit)}
          >
            <motion.div variants={itemVariants} className="space-y-2">
              <label className="block text-sm font-medium text-white">First Name</label>
              <input
                {...register('first_name', { required: 'First name is required' })}
                type="text"
                className="input-field"
                placeholder="John"
              />
              {errors.first_name && (
                <p className="text-red-400 text-sm">{errors.first_name.message}</p>
              )}
            </motion.div>

            <motion.div variants={itemVariants} className="space-y-2">
              <label className="block text-sm font-medium text-white">Last Name</label>
              <input
                {...register('last_name', { required: 'Last name is required' })}
                type="text"
                className="input-field"
                placeholder="Doe"
              />
              {errors.last_name && (
                <p className="text-red-400 text-sm">{errors.last_name.message}</p>
              )}
            </motion.div>

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
              <label className="block text-sm font-medium text-white">Password</label>
              <div className="relative">
                <input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Password must be at least 8 characters' },
                  })}
                  type={showPassword ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="••••••••"
                  onChange={(e) => {
                    onPasswordChange(e)
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a1a1a1] hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              {password && (
                <div className="mt-2">
                  <div className="flex gap-1 h-1">
                    {[0, 25, 50, 75].map((threshold, i) => (
                      <div
                        key={i}
                        className={`flex-1 rounded-full transition-colors ${
                          passwordStrength > threshold
                            ? passwordStrength < 50
                              ? 'bg-red-500'
                              : passwordStrength < 75
                                ? 'bg-yellow-500'
                                : 'bg-green-500'
                            : 'bg-[#2d2d2d]'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-[#a1a1a1] mt-1">
                    {passwordStrength < 50
                      ? 'Weak'
                      : passwordStrength < 75
                        ? 'Fair'
                        : 'Strong'}
                  </p>
                </div>
              )}

              {errors.password && (
                <p className="text-red-400 text-sm">{errors.password.message}</p>
              )}
            </motion.div>

            <motion.div variants={itemVariants} className="space-y-2">
              <label className="block text-sm font-medium text-white">Confirm Password</label>
              <div className="relative">
                <input
                  {...register('confirmPassword', {
                    required: 'Please confirm your password',
                  })}
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="input-field pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#a1a1a1] hover:text-white"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-red-400 text-sm">{errors.confirmPassword.message}</p>
              )}
            </motion.div>

            <motion.div variants={itemVariants} className="flex items-center gap-2">
              <input type="checkbox" id="terms" className="w-4 h-4 cursor-pointer" />
              <label htmlFor="terms" className="text-sm text-[#a1a1a1] cursor-pointer">
                I agree to the{' '}
                <a href="#" className="text-[#00d4aa] hover:underline">
                  Terms & Conditions
                </a>
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
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </motion.button>
          </motion.form>

          <motion.p variants={itemVariants} className="text-center text-[#a1a1a1] text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-[#00d4aa] hover:underline font-medium">
              Sign In
            </Link>
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}
