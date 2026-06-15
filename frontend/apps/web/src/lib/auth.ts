import { ApiError } from '@frontend/types/api'
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { getApiClient } from './api'

const decodeToken = (
  token: string
): {
  token_type: string
  exp: number
  iat: number
  jti: string
  user_id: number
} => {
  return JSON.parse(atob(token.split('.')[1]))
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: {
    strategy: 'jwt'
  },
  pages: {
    signIn: '/login'
  },
  callbacks: {
    session: async ({ session, token }) => {
      const access = decodeToken(token.access as string)
      const refresh = decodeToken(token.refresh as string)

      if (Date.now() / 1000 > access.exp && Date.now() / 1000 > refresh.exp) {
        throw new Error('Refresh token expired')
      }

      session.user = {
        ...session.user,
        id: String(access.user_id),
        username: token.username as string,
      }

      session.refreshToken = token.refresh as string
      session.accessToken = token.access as string

      return session
    },
    jwt: async ({ token, user }) => {
      if (user && (user as any).username) {
        return { ...token, ...user }
      }

      // Refresh access token if expired
      if (token.access && Date.now() / 1000 > decodeToken(token.access as string).exp) {
        const apiClient = await getApiClient()
        const res = await apiClient.token.tokenRefreshCreate({
          access: token.access as string,
          refresh: token.refresh as string
        })
        token.access = res.access
      }

      return token
    }
  },
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        username: { label: 'Email', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) return null

        try {
          const apiClient = await getApiClient()
          const res = await apiClient.token.tokenCreate({
            username: credentials.username as string,
            password: credentials.password as string,
            access: '',
            refresh: ''
          })

          return {
            id: String(decodeToken(res.access).user_id),
            username: credentials.username,
            access: res.access,
            refresh: res.refresh
          }
        } catch (error) {
          if (error instanceof ApiError) return null
        }

        return null
      }
    })
  ]
})
