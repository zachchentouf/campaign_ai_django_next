import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'

const AccountLayout = async ({ children }: { children: React.ReactNode }) => {
  const session = await auth()

  if (session === null) {
    return redirect('/')
  }

  return (
    <div className="flex-grow h-screen flex items-center justify-center -my-12 w-full">
      <div className="w-96">{children}</div>
    </div>
  )
}

export default AccountLayout
