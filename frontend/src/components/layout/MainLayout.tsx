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
        <div className="mx-auto flex h-16 w-full items-center justify-between px-4 lg:h-20 lg:px-6 xl:h-24 xl:px-8 2xl:h-28 2xl:px-10">
          <div className="flex items-center gap-2 lg:gap-4 xl:gap-5 2xl:gap-6">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 font-bold text-white shadow-lg shadow-blue-200 lg:h-14 lg:w-14 lg:rounded-xl lg:text-2xl xl:h-16 xl:w-16 xl:text-3xl 2xl:h-18 2xl:w-18 2xl:text-4xl">
              VB
            </div>
            <span className="hidden bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-xl font-bold text-transparent md:block lg:text-3xl xl:text-4xl 2xl:text-5xl">
              VoiceBridge
            </span>
          </div>

          <nav className="flex items-center gap-2 md:gap-4 lg:gap-4 xl:gap-5 2xl:gap-6">
            <Link to="/">
              <Button
                variant={isActive('/') ? 'primary' : 'ghost'}
                size="sm"
                className="whitespace-nowrap shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 lg:h-14 lg:px-6 lg:text-xl xl:h-16 xl:px-8 xl:text-2xl 2xl:h-18 2xl:px-10 2xl:text-3xl"
                leftIcon={<Mic className="h-4 w-4 flex-shrink-0 lg:h-6 lg:w-6 xl:h-7 xl:w-7 2xl:h-8 2xl:w-8" />}
              >
                语音助手
              </Button>
            </Link>
            <Link to="/profile">
              <Button
                variant={isActive('/profile') ? 'primary' : 'ghost'}
                size="sm"
                className="whitespace-nowrap shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 lg:h-14 lg:px-6 lg:text-xl xl:h-16 xl:px-8 xl:text-2xl 2xl:h-18 2xl:px-10 2xl:text-3xl"
                leftIcon={<User className="h-4 w-4 flex-shrink-0 lg:h-6 lg:w-6 xl:h-7 xl:w-7 2xl:h-8 2xl:w-8" />}
              >
                个人信息
              </Button>
            </Link>
            <div className="mx-1 h-6 w-px bg-gray-200 lg:mx-2 lg:h-10 xl:h-12 2xl:h-14" />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-500 hover:bg-red-50 hover:text-red-600 lg:h-14 lg:w-14 xl:h-16 xl:w-16 2xl:h-18 2xl:w-18"
            >
              <LogOut className="h-4 w-4 lg:h-6 lg:w-6 xl:h-7 xl:w-7 2xl:h-8 2xl:w-8" />
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
