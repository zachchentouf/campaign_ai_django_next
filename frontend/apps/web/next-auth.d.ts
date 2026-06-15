import 'next-auth'

declare module 'next-auth' {
  interface User {
    username: string
    access: string
    refresh: string
  }

  interface Session {
    refreshToken: string
    accessToken: string
    user: {
      id: string
      username: string
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    username: string
    access: string
    refresh: string
  }
}
