import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, User, Mic } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { logout } from '@/api/auth';

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md supports-[backdrop-filter]:bg-white/60">
        <div className="mx-auto flex h-16 w-full items-center justify-between px-4 lg:h-32 lg:px-[8vw] xl:h-40 xl:px-[10vw] 2xl:h-44 2xl:px-[12vw]">
          <div className="flex items-center gap-2 lg:gap-6 xl:gap-8 2xl:gap-10">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 font-bold text-white shadow-lg shadow-blue-200 lg:h-24 lg:w-24 lg:rounded-2xl lg:text-4xl xl:h-28 xl:w-28 xl:text-5xl 2xl:h-32 2xl:w-32 2xl:text-6xl">
              VB
            </div>
            <span className="hidden bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-xl font-bold text-transparent md:block lg:text-5xl xl:text-6xl 2xl:text-7xl">
              VoiceBridge
            </span>
          </div>

          <nav className="flex items-center gap-3 md:gap-6 lg:gap-12 xl:gap-14 2xl:gap-16">
            <Link to="/">
              <Button
                variant={isActive('/') ? 'primary' : 'ghost'}
                size="sm"
                className="whitespace-nowrap shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 lg:h-24 lg:min-w-[15vw] lg:px-14 lg:text-3xl xl:h-28 xl:min-w-[16vw] xl:px-16 xl:text-4xl 2xl:h-32 2xl:min-w-[18vw] 2xl:px-20 2xl:text-5xl"
                leftIcon={<Mic className="h-4 w-4 flex-shrink-0 lg:h-12 lg:w-12 xl:h-14 xl:w-14 2xl:h-16 2xl:w-16" />}
              >
                语音助手
              </Button>
            </Link>
            <Link to="/profile">
              <Button
                variant={isActive('/profile') ? 'primary' : 'ghost'}
                size="sm"
                className="whitespace-nowrap shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 lg:h-24 lg:min-w-[15vw] lg:px-14 lg:text-3xl xl:h-28 xl:min-w-[16vw] xl:px-16 xl:text-4xl 2xl:h-32 2xl:min-w-[18vw] 2xl:px-20 2xl:text-5xl"
                leftIcon={<User className="h-4 w-4 flex-shrink-0 lg:h-12 lg:w-12 xl:h-14 xl:w-14 2xl:h-16 2xl:w-16" />}
              >
                个人信息
              </Button>
            </Link>
            <div className="mx-2 h-6 w-px bg-gray-200 lg:mx-6 lg:h-20 xl:h-24 2xl:h-28" />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-500 hover:bg-red-50 hover:text-red-600 lg:h-22 lg:w-22 xl:h-24 xl:w-24 2xl:h-28 2xl:w-28"
            >
              <LogOut className="h-4 w-4 lg:h-10 lg:w-10 xl:h-12 xl:w-12 2xl:h-14 2xl:w-14" />
            </Button>
          </nav>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="animate-in fade-in mx-auto flex-1 px-[3vw] py-8 duration-500" style={{ maxWidth: '95vw' }}>
        <Outlet />
      </main>

      <footer className="border-t border-gray-100 bg-white py-6 text-center text-sm text-gray-400">
        <p>© 2025 VoiceBridge AI. 为您提供最贴心的语音服务。</p>
      </footer>
    </div>
  );
}
